from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class KumariBank(Reconcile):
    def __init__(self,bank_name,excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name,excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.KUMARI_BANK_FILE, skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.KUMARI_SOA_FILE, encoding='latin-1')
        

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_soa_stmt()
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase_4()
        self.updated_standardize_bank_stmt()
        self.updated_standardize_bank_stmt_phase4()
        self.extracting_tid_from_bank_stmt()
        self.extracting_tid_from_bank_stmt_phase_4()
        self.matching_bank_stmt_with_soa_report()
        self.matching_soa_report_with_bank_stmt()
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
        self.bank_statement_df['Date'] = self.bank_statement_df['Tran dates']
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'],format='%Y-%m-%d').dt.date
        display(f'columns-->{self.bank_statement_df.columns}')  

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Ref Num" and "Tran Particular" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            # if "WT" in str(row['Desc2']):
            #     id = str(row['Desc2']).replace('/WT','')
            #     id = id.split()
            #     id =  id[0].replace("10000000", "")
            #     self.bank_statement_df.at[index, 'Transaction Id'] = id
            if "1000000" in str(row["Tran Particular"]):
                id_matches = re.findall(r'10*[0-9]{5}', str(row["Tran Particular"]))
                if id_matches:
                    id = id_matches[0].replace("1000000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "100000" in str(row["Tran Particular"]):
                id_matches = re.findall(r'10*[0-9]{6}', str(row["Tran Particular"]))
                if id_matches:
                    id = id_matches[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "1000000" in str(row["Ref Num"]):
                id_matches = re.findall(r'10*[0-9]{5}', str(row["Ref Num"]))
                if id_matches:
                    id = id_matches[0].replace("1000000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "100000" in str(row["Ref Num"]):
                id_matches = re.findall(r'10*[0-9]{6}', str(row["Ref Num"]))
                if id_matches:
                    id = id_matches[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['Debit Amount'] > 0:
            mode = 'DR'
            amount = row['Debit Amount']
        elif row['Credit Amount'] > 0:
            mode = 'CR'
            amount = row['Credit Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])

    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        '''
         This method cleans and formats the bank statement DataFrame.
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format='%Y-%m-%d %H:%M:%S.%f').dt.date

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase4(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Desc3" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            row_3 = str(row['Desc3'])
            row_1 = str(row['Desc1'])
            if "NPS-IF-" in row_3:
                id = re.findall(r'[0-9]{7}', row_3)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                continue
            elif "FTMS-" in row_3:
                id = re.findall(r'[0-9]{6}', row_3)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                continue
            
            elif "WT10000" in row_3:
                id = row_3[-5:]
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
                
            elif "10000" in row_1:
                id = re.findall(r'10*[0-9]{7}', row_1)
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
