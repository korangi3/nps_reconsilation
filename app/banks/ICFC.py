from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class ICFC(Reconcile):
    """
        Initialize an ICFC reconciliation instance.

        :param bank_name: The name of the bank.
        :param excelwriter: Excel writer object to output reconciliation results.
    """
    def __init__(self, bank_name, excelwriter):
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.DataFrame()
        self.soa_statement_df = pd.DataFrame()
        self.get_phase4_df()

    @run_phase(phase_number=4)  
    def get_phase4_df(self):
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.ICFC_BANK_FILE, skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.ICFC_SOA_FILE, encoding='latin-1')

    def main(self):
        if self.bank_statement_df.empty or self.soa_statement_df.empty:
            return
        self.preprocessing_soa_stmt()
        self.preprocessing_bank_stmt()
        self.updated_standardize_bank_stmt_phase_4()
        self.extracting_tid_from_bank_stmt_phase_4()
        self.matching_bank_stmt_with_soa_report()
        self.matching_soa_report_with_bank_stmt()
        self.total_debit_credit_amount_of_soa()
        self.total_debit_credit_amount_of_bank()
        self.debit_credit_amount_matches_tid_of_bank_with_soa()
        self.debit_credit_amount_of_soa_matched_with_bank()
        self.extract_number_of_tid_CR_and_DR_from_soa()
        self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
        # self.write_soa_data()
        # self.write_bank_data()
        self.generate_report()

    @run_phase(phase_number=4)
    def preprocessing_bank_stmt(self):
        """
        Drop unnecessary rows and standardize column names.
        """
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date

    @run_phase(phase_number=4)
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
            if "10000" in (row['Desc3']):
                id = re.findall(r'10*[0-9]{7}', row['Desc3'])
                id =  id[0].replace("10000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "10000" in (row['Desc3']):
                id = re.findall(r'10*[0-9]{7}', row['Desc3'])
                id =  id[0].replace("10000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "NPS-IF-" in row['Desc3']:
                id = re.findall(r'[0-9]{7}', row['Desc3'])
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
            elif "FTMS-" in row['Desc3']:
                id = re.findall(r'[0-9]{6}', row['Desc3'])
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
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
        if row['Txn Type'] == 'DR' :
            mode = 'DR'
            amount = row['Amount']
        elif row['Txn Type'] == 'CR':
            mode = 'CR'
            amount = row['Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
