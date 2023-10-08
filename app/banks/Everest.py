from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class EverestBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.proceed = True
        self.get_phase1_df()
        self.get_phase4_df()

    @run_phase(phase_number=1)
    def get_phase1_df(self):
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.EVEREST_BANK_FILE, skiprows= 11)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.EVEREST_SOA_FILE, encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        try:
            self.bank_statement_df = pd.read_excel(Banks_FILEPATH.EVEREST_BANK_FILE, skiprows= 1)
            self.soa_statement_df = pd.read_csv(SOA_FILEPATH.EVEREST_SOA_FILE, encoding='latin-1')
        except:
            self.proceed = False

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase4()
        self.updated_standardize_bank_stmt()
        self.updated_standardize_bank_stmt_phase_4()
        self.extracting_tid_from_bank_stmt()
        self.extracting_tid_from_bank_stmt_phase_4()
        self.preprocessing_soa_stmt()
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
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df.drop(columns='Unnamed: 0', inplace=True)
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df['Cr. Amt'] = self.bank_statement_df['Cr. Amt'].replace('', 0).fillna(0)
        self.bank_statement_df['Dr. Amt'] = self.bank_statement_df['Dr. Amt'].replace('', 0).fillna(0)
        if self.bank_statement_df['Cr. Amt'].dtype == 'object':
            self.bank_statement_df['Cr. Amt'] = pd.to_numeric(self.bank_statement_df['Cr. Amt'].str.replace(',', ''), errors='coerce')
        if self.bank_statement_df['Dr. Amt'].dtype == 'object':
            self.bank_statement_df['Dr. Amt'] = pd.to_numeric(self.bank_statement_df['Dr. Amt'].str.replace(',', ''), errors='coerce')
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        """
        Standardize bank statement data.

        Converts date columns to datetime objects and applies formatting to other columns.
        """
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Tran Date'], format="%d-%m-%Y", errors='coerce').dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Remarks" and "Tran Particular" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            if "100000" in str(row["Remarks"]):
                id_matches = re.findall(r'10*[0-9]{7}', str(row["Remarks"]))
                if not id_matches:
                    continue
                id = id_matches[0].replace("100000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif row['Tran Particular'] and isinstance(row['Tran Particular'], str):
                transaction_particular = row['Tran Particular']
                match = re.search(r'\b\d{4}\b', transaction_particular)
                if not match:
                    continue
                id = match.group()
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
        display('total_tid', self.bank_statement_df['Transaction Id'].count())

    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['Dr. Amt'] > 0:
            mode = 'DR'
            amount = row['Dr. Amt']
        elif row['Cr. Amt'] > 0:
            mode = 'CR'
            amount = row['Cr. Amt']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%d-%m-%Y", errors='coerce').dt.date

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
                continue
            
            elif "DMSS1000000" in str(row['Desc2']):
                id = str(row['Desc2'])[-6:]
                
                # id = re.findall(r'D(\d+)', str(row['Desc2']))
                # id = id[0].replace('1000000','')
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
                
            elif "S100000000" in str(row['Desc2']):
                id = re.findall(r'S(\d+)', str(row['Desc2']))
                id =  id[0].replace("100000000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
                
            elif "FT-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{7}', str(row['Desc2']))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                continue
                
            elif "10000" in str(row['Desc1']):
                id = str(row['Desc1']).split(',')[0].replace('10000','')
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            else:
                continue
