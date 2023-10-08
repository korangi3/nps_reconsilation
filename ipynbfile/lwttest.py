from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH, SOA_FILEPATH, PHASE1_LWT_FILEPATH
from xlsxwriter import Workbook
import pandas as pd, numpy as np, datetime
import re

class MegaBank(Reconcile):
    bank_statement_df = pd.read_excel(Banks_FILEPATH.MEGA_BANK_FILE, sheet_name='Sheet1')
    soa_statement_df = pd.read_csv(SOA_FILEPATH.MEGA_SOA_FILE, encoding='latin-1')
    soa_merchant_df = pd.read_excel(PHASE1_LWT_FILEPATH.MEGA_LWT_FILE, sheet_name='Sheet1', skiprows=1)

    def __init__(self,bank_name):
        super().__init__(bank_name)
        

    def main(self):
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.standardize_bank_stmt()
        self.extracting_tid_from_bank_stmt()
        self.preprocessing_soa_stmt()
        self.update_soa_report_with_merchant_id()
        self.matching_bank_stmt_with_soa_report()
        self.matching_soa_report_with_bank_stmt()
        # self.total_debit_credit_amount_of_soa()
        # self.total_debit_credit_amount_of_bank()
        # self.debit_credit_amount_matches_tid_of_bank_with_soa()
        # self.debit_credit_amount_of_soa_matched_with_bank()
        # self.extract_number_of_tid_CR_and_DR_from_soa()
        # self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
        # self.write_soa_data()
        # self.write_bank_data()
        # self.generate_report()


    def preprocessing_bank_stmt(self):
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df['Deposit'] = self.bank_statement_df['Deposit'].replace('', 0).fillna(0)
        self.bank_statement_df['Withdraw'] = self.bank_statement_df['Withdraw'].replace('', 0).fillna(0)
        if self.bank_statement_df['Deposit'].dtype == 'object':
            self.bank_statement_df['Deposit'] = pd.to_numeric(self.bank_statement_df['Deposit'].str.replace(',', ''), errors='coerce')
        if self.bank_statement_df['Withdraw'].dtype == 'object':
            self.bank_statement_df['Withdraw'] = pd.to_numeric(self.bank_statement_df['Withdraw'].str.replace(',', ''), errors='coerce')
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')


    def standardize_bank_stmt(self):
        self.bank_statement_df['Date'] = self.bank_statement_df['Value Date'].apply(self.convert_date_format)
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1) 


    def update_soa_report_with_merchant_id(self):
        display(f'columns of merchants are: {self.soa_merchant_df.columns}')
        self.soa_statement_df['Merchant Id'] = np.nan
        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            if not wallet_item['Transaction Type'] == 'LoadWallet':
                continue
            wallet_tid = wallet_item['Transaction Id']
            merchant_tid_row = self.soa_merchant_df[self.soa_merchant_df['Load Wallet Transaction Id'] == wallet_tid]
            if merchant_tid_row.empty:
                continue
            merchant_tid = merchant_tid_row.iloc[0]['Merchant Transaction Id']
            self.soa_statement_df.at[wallet_index, 'Transaction Id'] = merchant_tid


    def extracting_tid_from_bank_stmt(self):
        for index, row in self.bank_statement_df.iterrows():
            row_desc:str = row["Description"]
            id_text_list:list = row_desc.split()

            if "10000" in str(row_desc):
                id = re.sub(r'10*', '', id_text_list[-1], count=1)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id

        display(f'transaction_id ====> {self.bank_statement_df["Transaction Id"]}')
        display(f'total_tid -----> {self.bank_statement_df["Transaction Id"].count()}')

    
    def standard_format(self,row):
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
    def convert_date_format(date_str):
        try:
            parsed_date = datetime.datetime.strptime(date_str, '%d-%B-%Y')
            return parsed_date.strftime('%d/%m/%Y')
        except:
            parsed_date = datetime.datetime.strptime(date_str, '%d-%b-%Y')
            return parsed_date.strftime('%d/%m/%Y')
