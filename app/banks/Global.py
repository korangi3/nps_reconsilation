from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH, SOA_FILEPATH
# from Constants import Banks_FILEPATH, SOA_FILEPATH, PHASE1_LWT_FILEPATH,PHASE1_FT_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd, numpy as np, datetime
import re

class GlobalBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        '''
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        '''
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.GLOBAL_BANK_FILE, skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.GLOBAL_SOA_FILE, encoding='latin-1')
        # self.lwt_merchant_df = pd.read_excel(PHASE1_LWT_FILEPATH.LWT_FILE,)
        # self.ft_merchant_df = pd.read_csv(PHASE1_FT_FILEPATH.GLOBAL_FT_FILE, encoding='latin-1')
        

    def main(self):
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase_4()
        self.standardize_bank_stmt()
        self.updated_standardize_bank_stmt_phase_4()
        self.extracting_tid_from_bank_stmt()
        self.extracting_tid_from_bank_stmt_phase_4()
        self.preprocessing_soa_stmt()
        self.matching_bank_stmt_with_soa_report()
        self.matching_soa_report_with_bank_stmt()
        self.update_soa_report_with_merchant_id()
        self.matching_soa_report_with_bank_stmt_with_merchant_id()
        self.matching_bank_stmt_with_soa_report_with_merchant_id()
        self.total_debit_credit_amount_of_soa()
        self.total_debit_credit_amount_of_bank()
        self.debit_credit_amount_matches_tid_of_bank_with_soa()
        self.debit_credit_amount_of_soa_matched_with_bank()
        self.extract_number_of_tid_CR_and_DR_from_soa()
        self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
        # self.write_soa_data()
        # self.write_bank_data()
        self.generate_report()

    @run_phase(phase_number=1)
    def preprocessing_bank_stmt(self):
        '''
         This method cleans and formats the bank statement DataFrame and convert the date column to standard format to match with soa
        '''
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Tran Date'], format='%Y-%m-%d')
        self.bank_statement_df['Deposit'] = self.bank_statement_df['Deposit'].replace('', 0).fillna(0)
        self.bank_statement_df['Withdraw'] = self.bank_statement_df['Withdraw'].replace('', 0).fillna(0)
        if self.bank_statement_df['Deposit'].dtype == 'object':
            self.bank_statement_df['Deposit'] = pd.to_numeric(self.bank_statement_df['Deposit'].str.replace(',', ''), errors='coerce')

        if self.bank_statement_df['Withdraw'].dtype == 'object':
            self.bank_statement_df['Withdraw'] = pd.to_numeric(self.bank_statement_df['Withdraw'].str.replace(',', ''), errors='coerce')

    @run_phase(phase_number=1)
    def standardize_bank_stmt(self):
        '''
        formatting to bank statement data.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1) 

    @run_phase(phase_number=1)
    def update_soa_report_with_merchant_id(self):
        '''
        This method updates the SOA report with merchant IDs from LWT(Load Wallet Transaction) and FT(FundTransfer) data.
        '''
        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']
            if wallet_item['Transaction Type'] == 'LoadWallet':
                lwt_merchant_tid_row = self.lwt_merchant_df[self.lwt_merchant_df['LoadWalletTransactionId'] == wallet_tid]
                if lwt_merchant_tid_row.empty:
                    continue
                lwt_merchant_tid = lwt_merchant_tid_row.iloc[0]['Merchant Transaction Id']
                self.soa_statement_df.at[wallet_index, 'Transaction Id'] = lwt_merchant_tid

            elif wallet_item['Transaction Type'] == 'FundTransfer':
                ft_merchant_tid_row = self.ft_merchant_df[self.ft_merchant_df['Transaction Detail Id'] == wallet_tid]
                if ft_merchant_tid_row.empty:
                    continue
                ft_merchant_tid = ft_merchant_tid_row.iloc[0]['Merchant Transaction Id']
                self.soa_statement_df.at[wallet_index, 'Transaction Id'] = ft_merchant_tid

    @run_phase(phase_number=1)
    def matching_soa_report_with_bank_stmt_with_merchant_id(self):
        '''
        This method matches transactions in SOA report with bank statement transactions using merchant IDs.
        '''
        lwt_bank_df = self.bank_statement_df[self.bank_statement_df['Description'].str.contains('IMEPAY') & ~self.bank_statement_df['Description'].str.contains('TRFO|TRFB')]['Description']
        ft_bank_df = self.bank_statement_df[self.bank_statement_df['Description'].str.contains('IMEPAY') & self.bank_statement_df['Description'].str.contains('TRFO|TRFB')]['Description']

        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']

            if wallet_item['Transaction Type'] == 'LoadWallet':
                if not lwt_bank_df.str.contains(wallet_tid).any():
                    continue
                if self.soa_statement_df.at[wallet_index, 'Matched']:
                    continue
                self.soa_statement_df.at[wallet_index, 'Matched'] = True
            
            elif wallet_item['Transaction Type'] == 'FundTransfer':
                if not ft_bank_df.str.contains(wallet_tid).any():
                    continue
                if self.soa_statement_df.at[wallet_index, 'Matched']:
                    continue
                self.soa_statement_df.at[wallet_index, 'Matched'] = True

        match_count = (self.soa_statement_df['Matched'] == True).sum()
        unmatch_count = (self.soa_statement_df['Matched'] == False).sum()
        display(f'Matched final count soa_statement after getting merchant id ==== {match_count}')
        display(f'Unmatched final count soa_statement after getting merchant id ==== {unmatch_count}') 
       
    @run_phase(phase_number=1)
    def matching_bank_stmt_with_soa_report_with_merchant_id(self):
        '''
        This method matches bank statement transactions with SOA report transactions using merchant IDs.
        '''
        lwt_soa_df = self.soa_statement_df[self.soa_statement_df['Transaction Type'].str.contains('LoadWallet', na=False)]['Transaction Id']
        ft_soa_df = self.soa_statement_df[self.soa_statement_df['Transaction Type'].str.contains('FundTransfer', na=False)]['Transaction Id']

        for wallet_index, wallet_item in self.bank_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']
            if str(wallet_tid)=='nan':
                continue
            if lwt_soa_df.str.contains(wallet_tid).any():
                if self.bank_statement_df.at[wallet_index, 'Matched']:
                    continue
                self.bank_statement_df.loc[wallet_index, 'Matched'] = True
            elif ft_soa_df.str.contains(wallet_tid).any():
                if self.bank_statement_df.at[wallet_index, 'Matched']:
                    continue
                self.bank_statement_df.loc[wallet_index, 'Matched'] = True

        match_count = (self.bank_statement_df['Matched'] == True).sum()
        unmatch_count = (self.bank_statement_df['Matched'] == False).sum()
        display(f'Matched final count bank_statement after getting merchant id  ==== {match_count}')
        display(f'Unmatched final count bank_statement after getting merchant id ==== {unmatch_count}')

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        '''
        This method extracts transaction IDs from various patterns in bank statement descriptions.
        '''
        for index, row in self.bank_statement_df.iterrows():
            row_desc:str = row["Description"]
            id_text_list:list = row_desc.split()

            if "10000" in str(row_desc): #extract the transaction id from column name Description
                id = re.sub(r'10*', '', id_text_list[-1], count=1)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif 'CIPS' in row['Description']: #extract the transaction id from the column name Description whose value contain CIPS
                description_cips = row['Description'].split("/")
                value = description_cips[1]
                self.bank_statement_df.loc[index,'Transaction Id'] = value

            elif 'IMEPAY' in str(row_desc) and not('TRFO' in str(row_desc) or 'TRFB' in str(row_desc)):#this will extract the TID from load wallet
                id_text_list = row_desc.split('-')
                for id in id_text_list:
                    if not re.match(r'^202', id):
                        continue
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id  #this will extract the transaction id from the fundtransfer 
            elif 'IMEPAY' in str(row_desc) and ('TRFO' in str(row_desc) or 'TRFB' in str(row_desc)):
                id_text_list = row_desc.split('-')
                for id in id_text_list:
                    if not re.match(r'^202', id):
                        continue
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            else:
                continue

        display(f'total_tid -----> {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=1)
    def standard_format(self,row):
        '''
          Determine transaction mode and amount from bank statement data.

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
    
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        """
        Drop unnecessary rows and standardize column names.
        """
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date

    run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        '''
        applies formatting to columns.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Desc3" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            
            if "NPS-IF-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{7}', str(row['Desc2']))
                if not id:
                    continue
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
            elif "FTMS-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{6}', str(row['Desc2']))
                if not id:
                    continue
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
            elif "10000" in str(row['Desc2']):
                id = re.findall(r'10*[0-9]{7}', str(row['Desc2']))
                if not id:
                    continue
                id =  id[0].replace("10000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "10000" in str(row['Desc1']):
                id = re.findall(r'10*[0-9]{7}', str(row['Desc1']))
                if not id:
                    continue
                id =  id[0].replace("10000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=4)
    def standard_format_phase_4(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['Txn Type'] == 'D' :
            mode = 'DR'
            amount = row['Amount']
        elif row['Txn Type'] == 'C':
            mode = 'CR'
            amount = row['Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
