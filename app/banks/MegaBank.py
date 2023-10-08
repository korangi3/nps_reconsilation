from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH, SOA_FILEPATH, PHASE1_LWT_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd, numpy as np, datetime
import re

class MegaBank(Reconcile):
    bank_statement_df = pd.read_excel(Banks_FILEPATH.MEGA_BANK_FILE, sheet_name='Sheet1')
    soa_statement_df = pd.read_csv(SOA_FILEPATH.MEGA_SOA_FILE, encoding='latin-1')

    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
    # @run_phase(phase_number=1)
    # def get_phase1_df(self):
    #     self.bank_statement_df = pd.read_excel(Banks_FILEPATH.EVEREST_BANK_FILE, skiprows= 11)
    #     self.soa_statement_df = pd.read_csv(SOA_FILEPATH.EVEREST_SOA_FILE, encoding='latin-1')
        

    def main(self):
        """
        This method orchestrates the entire reconciliation process by calling various steps.
        """
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.standardize_bank_stmt()
        self.extracting_tid_from_bank_stmt()
        self.preprocessing_soa_stmt()
        self.update_soa_report_with_merchant_id()
        self.matching_bank_stmt_with_soa_report()
        self.matching_soa_report_with_bank_stmt()
        self.matching_soa_report_with_bank_stmt_of_load_wallet()
        self.matching_bank_stmt_with_soa_report_of_load_wallet()
        self.total_debit_credit_amount_of_soa()
        self.total_debit_credit_amount_of_bank()
        self.debit_credit_amount_matches_tid_of_bank_with_soa()
        self.debit_credit_amount_of_soa_matched_with_bank()
        self.extract_number_of_tid_CR_and_DR_from_soa()
        self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
        self.write_soa_data()
        self.write_bank_data()
        self.generate_report()

    @run_phase(phase_number=1)
    def preprocessing_bank_stmt(self):
        '''
        This method cleans and formats the bank statement DataFrame.
        '''
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df = self.bank_statement_df.iloc[1:-1]
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df['Deposit'] = self.bank_statement_df['Deposit'].replace('', 0).fillna(0)
        self.bank_statement_df['Withdraw'] = self.bank_statement_df['Withdraw'].replace('', 0).fillna(0)
        if self.bank_statement_df['Deposit'].dtype == 'object':
            self.bank_statement_df['Deposit'] = pd.to_numeric(self.bank_statement_df['Deposit'].str.replace(',', ''), errors='coerce')
        if self.bank_statement_df['Withdraw'].dtype == 'object':
            self.bank_statement_df['Withdraw'] = pd.to_numeric(self.bank_statement_df['Withdraw'].str.replace(',', ''), errors='coerce')
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')

    @run_phase(phase_number=1)
    def standardize_bank_stmt(self):
        '''
         Converts date columns and applies formatting to bank statement data.
        '''
        display(f'date======{self.bank_statement_df["Value Date"]}')
        self.bank_statement_df['Date'] = np.nan
        try:
            self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Value Date'], format='%d-%b-%Y').dt.date
        except:
            self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Value Date'], format='%d-%B-%Y').dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from various patterns in bank statement descriptions.
        """
        for index, row in self.bank_statement_df.iterrows():
            row_desc:str = row["Description"]
            id_text_list:list = row_desc.split()

            if "10000" in str(row_desc):
                id = re.sub(r'10*', '', id_text_list[-1], count=1)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif 'IMEPAY' in str(row_desc):
                id_text_list = row_desc.split('-')
                for id in id_text_list:
                    if not '202' in id:
                        continue
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id

        display(f'transaction_id ====> {self.bank_statement_df["Transaction Id"]}')
        display(f'total_tid -----> {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=1)
    def update_soa_report_with_merchant_id(self):
        """
        This method updates the SOA report with merchant IDs for Load Wallet transactions.
        """
        display(f'columns of merchants are: {self.soa_merchant_df.columns}')
        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            if not wallet_item['Transaction Type'] == 'LoadWallet':
                continue
            wallet_tid = wallet_item['Transaction Id']
            merchant_tid_row = self.soa_merchant_df[self.soa_merchant_df['LoadWalletTransactionId'] == wallet_tid]
            if merchant_tid_row.empty:
                continue
            merchant_tid = merchant_tid_row.iloc[0]['MerchantTransactionId']
            self.soa_statement_df.at[wallet_index, 'Transaction Id'] = merchant_tid

    @run_phase(phase_number=1)
    def matching_soa_report_with_bank_stmt_of_load_wallet(self):
        '''
        This method matches SOA report transactions with bank statement transactions for Load Wallet transactions.
        '''
        lwt_bank_df = self.bank_statement_df[self.bank_statement_df['Description'].str.contains('IMEPAY')]['Description']

        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']

            if not wallet_item['Transaction Type'] == 'LoadWallet':
                continue
            if not lwt_bank_df.str.contains(wallet_tid).any():
                continue
            if self.soa_statement_df.at[wallet_index, 'Matched']:
                continue

            display(f'Matched tid status from wallet df that is false: {self.soa_statement_df.at[wallet_index, "Matched"]}')
            self.soa_statement_df.at[wallet_index, 'Matched'] = True
            display(f'Matched tid status from wallet df: {self.soa_statement_df.at[wallet_index, "Matched"]}')

        match_count = (self.soa_statement_df['Matched'] == True).sum()
        unmatch_count = (self.soa_statement_df['Matched'] == False).sum()
        display(f'Matched final count soa_statement after getting merchant id ==== {match_count}')
        display(f'Unmatched final count soa_statement after getting merchant id ==== {unmatch_count}') 

    @run_phase(phase_number=1)
    def matching_bank_stmt_with_soa_report_of_load_wallet(self):
        '''
        This method matches bank statement transactions with SOA report transactions for Load Wallet transactions.
        '''
        lwt_soa_df = self.soa_statement_df[self.soa_statement_df['Transaction Type'].str.contains('LoadWallet', na=False)]['Transaction Id']
        for wallet_index, wallet_item in self.bank_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']
            
            if str(wallet_tid)=='nan':
                continue
            if not lwt_soa_df.str.contains(wallet_tid).any():
                continue
            if self.bank_statement_df.at[wallet_index, 'Matched']:
                continue
            display(f'bank wallet tid: {wallet_tid}')
            self.bank_statement_df.loc[wallet_index, 'Matched'] = True

        match_count = (self.bank_statement_df['Matched'] == True).sum()
        unmatch_count = (self.bank_statement_df['Matched'] == False).sum()
        display(f'Matched final count bank_statement after getting merchant id  ==== {match_count}')
        display(f'Unmatched final count bank_statement after getting merchant id ==== {unmatch_count}')


    @staticmethod
    @run_phase(phase_number=1)
    def standard_format(row):
        '''
        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        '''
        if row['Withdraw'] > 0:
            mode = 'DR'
            amount = row['Withdraw']
        elif row['Deposit'] > 0:
            mode = 'CR'
            amount = row['Deposit']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    

    @staticmethod
    @run_phase(phase_number=1)
    def convert_date_format(date_str):
        '''
        Parameters:
            date_str (str): Date in one format.

        Returns:
            str: Date in another format.
        '''
        try:
            parsed_date = datetime.datetime.strptime(date_str, '%d-%B-%Y')
            return parsed_date.strftime('%d/%m/%Y')
        except:
            parsed_date = datetime.datetime.strptime(date_str, '%d-%b-%Y')
            return parsed_date.strftime('%d/%m/%Y')
