from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from DatabaseComponent import SqliteClient
from Constants import Banks_FILEPATH,SOA_FILEPATH
from utils.Utils import run_phase
import pandas as pd
import re


class SunriseBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.SUNRISE_BANK_FILE, sheet_name='Account Statement',skiprows=2)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.SUNRISE_SOA_FILE,encoding='latin-1')
        

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        self.bank_stmt_preprocessing()
        self.update_dataframe()
        self.extracting_tid_from_bank_stmt()
        self.preprocessing_soa_stmt()
        self.matching_bank_stmt_with_soa_report()
        self.matching_soa_report_with_bank_stmt()
        self.total_debit_credit_amount_of_bank()
        self.total_debit_credit_amount_of_soa()
        self.debit_credit_amount_matches_tid_of_bank_with_soa()
        self.debit_credit_amount_of_soa_matched_with_bank()
        self.extract_number_of_tid_CR_and_DR_from_soa()
        self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
        self.write_soa_data()
        self.write_bank_data()
        self.generate_report()

    @run_phase(phase_number=1)
    def bank_stmt_preprocessing(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        self.bank_statement_df.drop(columns=['Unnamed: 0','Unnamed: 1','Unnamed: 4'],inplace=True)
        self.bank_statement_df.drop(index=self.bank_statement_df.index[0], axis=0, inplace=True)
        self.bank_statement_df.rename(columns={'TRAN DATE': 'Date'}, inplace=True)
        if self.bank_statement_df['CR AMT'].dtype == 'object':
            self.bank_statement_df['CR AMT'] = pd.to_numeric(self.bank_statement_df['CR AMT'].str.replace(',', ''), errors='coerce')
        if self.bank_statement_df['DR AMT'].dtype == 'object':
            self.bank_statement_df['DR AMT'] = pd.to_numeric(self.bank_statement_df['DR AMT'].str.replace(',', ''), errors='coerce')
        display(f'{self.bank_statement_df.count()}')
        display(f'{self.bank_statement_df.head()}')

    @run_phase(phase_number=1)
    def update_dataframe(self):
        '''
        applies formatting to the column by calling the Standard_format function and also format the date.
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%d").dt.date
        new_columns = self.bank_statement_df.apply(self.standard_format, axis=1)
        self.bank_statement_df[['Mode', 'Amount']] = new_columns

    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['CR AMT'] > 0:
            mode = 'DR'
            amount = row['CR AMT']
        elif row['CR AMT'] > 0:
            mode = 'CR'
            amount = row['CR AMT']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract the transaction id from the column name PARTICULAR using regular expression
        """
        for index, row in self.bank_statement_df.iterrows():
            particular_str = str(row["PARTICULAR"])
            if "100000" in particular_str:
                id_matches = re.findall(r'100000(\d+)', particular_str)
                if id_matches:
                    transaction_id = id_matches[0]
                    self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id
                
            # Extract CIPS value
            cips_matches = re.findall(r'/(?P<cips_value>\d+)/(\d+)/$', particular_str)
            if cips_matches:
                transaction_id = cips_matches[0][1]
                self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id
        display(f'total tid extracted from bank stmt: {self.bank_statement_df["Transaction Id"].count()}')
    