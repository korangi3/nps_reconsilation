from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class RBBBank(Reconcile):
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
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.RBB_BANK_FILE)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.RBB_SOA_FILE, encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.RBB_BANK_FILE, skiprows= 10)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.RBB_SOA_FILE, encoding='latin-1')

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase_4()
        self.preprocessing_soa_stmt()
        self.updated_standardize_bank_stmt()
        self.updated_standardize_bank_stmt_phase_4()
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
        # self.write_soa_data()
        # self.write_bank_data()
        self.generate_report()

    @run_phase(phase_number=1)
    def preprocessing_bank_stmt(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        self.bank_statement_df.drop(index=0, inplace=True)
       
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  
    
    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        '''
        applies formatting to columns by calling the stadard format function.
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%d").dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Transaction Detail" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            if "100000" in str(row["Tid"]):
                id_matches = re.findall(r'10*[0-9]{6}', str(row["Tid"]))
                if id_matches:
                    id = id_matches[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            
            elif row['Transaction Detail']:
                transaction_detail = row['Transaction Detail']
                last_four_digits = None
                match = re.search(r' (\d{4})\s*$', transaction_detail)
                if match:
                    last_four_digits = match.group(1)
                self.bank_statement_df.at[index, 'Transaction Id'] = last_four_digits
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
    def preprocessing_bank_stmt_phase_4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        self.bank_statement_df.drop(columns=['Unnamed: 0','Unnamed: 1','Unnamed: 2','Unnamed: 4','Unnamed: 6','Unnamed: 7','Unnamed: 8','Unnamed: 10','Unnamed: 12','Unnamed: 13','Unnamed: 14','Unnamed: 17','Unnamed: 19','Unnamed: 20','Unnamed: 20','Unnamed: 21'],inplace=True)
        self.bank_statement_df.drop(self.bank_statement_df.index[0],inplace=True)
        self.bank_statement_df = self.bank_statement_df.iloc[:-3]
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  
    
    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        '''
        applies formatting to columns by calling the stadard format function.
        '''
        # self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%d").dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)    

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Transaction Detail" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            if "NPS-IF-" in str(row["Transaction Detail"]):
                match = re.search(r'NPS-IF-(\d{7})', str(row["Transaction Detail"]))
                if match:
                    id = match.group(1)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id

            # elif 'IntS' in str(row["Transaction Detail"]):
            #     id_matches = re.findall(r'IntS10*[0-9]{6}', str(row["Transaction Detail"]))
            #     if id_matches:
            #         id = id_matches[0]
            #         display(f'idddddddddddddddddd{id}')
            #         self.bank_statement_df.loc[index, 'Transaction Id'] = id
            
            elif "FTMS-" in str(row["Transaction Detail"]):
                match = re.search(r'FTMS-(\d+)',str(row["Transaction Detail"]))
                if match:
                    id= match.group(1)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id

            elif "10000" in str(row["Transaction Detail"]):
                id = re.findall(r'10000[0-9]+',str(row["Transaction Detail"]))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")

            else:
                continue
        display('total_tid', self.bank_statement_df['Transaction Id'].count())

    @run_phase(phase_number=4)
    def standard_format_phase_4(self,row):
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

