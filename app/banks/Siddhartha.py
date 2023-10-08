from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from DatabaseComponent import SqliteClient
from Constants import Banks_FILEPATH,SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re


class SiddharthaBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.get_phase1_df()
        self.get_phase4_df()

    @run_phase(phase_number=1)
    def get_phase1_df(self):
        all_sheets = pd.read_excel(Banks_FILEPATH.SIDDHARTHA_BANK_FILE, sheet_name=None,skiprows=12)
        self.bank_statement_df = all_sheets['Account Activity Report(26)']
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.SIDDHARTHA_SOA_FILE,encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.SIDDHARTHA_BANK_FILE,skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.SIDDHARTHA_SOA_FILE,encoding='latin-1')

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase4()
        self.updated_standardize_bank_stmt()
        self.updated_standardize_bank_stmt_phase_4()
        self.extracting_tid_from_bank_stmt()
        self.extracting_tid_from_bank_stmt_phase_4()
        self.preprocessing_soa_stmt()
        self.matching_soa_report_with_bank_stmt()
        self.matching_bank_stmt_with_soa_report()
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
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        if self.bank_statement_df['Credit'].dtype == 'object':
            self.bank_statement_df['Credit'] = pd.to_numeric(self.bank_statement_df['Credit'].str.replace(',', ''), errors='coerce')
        if self.bank_statement_df['Debit'].dtype == 'object':
            self.bank_statement_df['Debit'] = pd.to_numeric(self.bank_statement_df['Debit'].str.replace(',', ''), errors='coerce')
        
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'Date-->{self.bank_statement_df["Date"]}')

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        '''
        applies formatting to the column by calling the Standard_format function.
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Trn Date'], format="%m/%d/%Y %I:%M:%S %p").dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extraccting the transaction id from the column 'Description' using regular expression 
        """
        for index, row in self.bank_statement_df.iterrows():
            for roww in (row['Desc1'] , row['Desc2']):
            # if "WT" in str(row['Desc2']):
            #     id = str(row['Desc2']).replace('/WT','')
            #     id = id.split()
            #     id =  id[0].replace("10000000", "")
            #     self.bank_statement_df.at[index, 'Transaction Id'] = id
                if "100000" in roww:
                    id_matches = re.findall(r'10*[0-9]{6}', roww)
                    if id_matches:
                        id = id_matches[0].replace("100000", "")
                        self.bank_statement_df.loc[index, 'Transaction Id'] = id
                        break
                elif "FT-" in roww:
                    if "FT-" in roww:
                        id = re.findall(r'[0-9]{7}',roww)
                        self.bank_statement_df.loc[index, 'Transaction ID'] = id[0]
                        break

        display(f"total number of tid extracted -->{self.bank_statement_df['Transaction Id'].count()}")
        return self.bank_statement_df
    
    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['Debit'] > 0:
            mode = 'DR'
            amount = row['Debit']
        elif row['Credit'] > 0:
            mode = 'CR'
            amount = row['Credit']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
   
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        '''
        applies formatting to columns.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)    

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
            amount = abs(row['Amount'])
        elif row['Txn Type'] == 'C':
            mode = 'CR'
            amount = row['Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Desc3" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            if "D100000000" in str(row['Desc2']):
                id = re.findall(r'D(\d+)', str(row['Desc2']))
                id = id[0].replace('100000000','')
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "S100000000" in str(row['Desc2']):
                id = re.findall(r'S(\d+)', str(row['Desc2']))
                id =  id[0].replace("100000000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "DMSS1000000" in str(row['Desc2']):
                id = re.findall(r'DMSS(\d+)', str(row['Desc2']))
                id =  id[0].replace("1000000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "OL10000" in str(row['Desc2']):
                id = str(row['Desc2']).split()[1]
                id =  id.replace("10000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "FT-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{7}', str(row['Desc2']))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
            elif "10000" in str(row['Desc1']):
                id = str(row['Desc1']).split(',')[0].replace('10000','')
                id = re.findall(r'[0-9]{7}', id)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')
