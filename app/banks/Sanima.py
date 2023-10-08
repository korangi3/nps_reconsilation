from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH,SOA_FILEPATH
from xlsxwriter import Workbook
from datetime import datetime
from utils.Utils import run_phase
import pandas as pd
import re

class SanimaBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.SANIMA_BANK_FILE,skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.SANIMA_SOA_FILE, encoding='latin-1')
        

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase_4()
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
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report if needed
        '''
        self.bank_statement_df['Date'] = self.bank_statement_df['TRAN_DATE'].apply(self.convert_date_format)
        display(f"bank statement date ===>{self.bank_statement_df['Date']}")

    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report if needed
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date
        display(f"bank statement date ===>{self.bank_statement_df['Date']}")
        
    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        '''
        applies formatting to columns and call the standard_function below.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        '''
        applies formatting to columns and call the standard_function below.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Tran_Particular" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            # Concatenate the values from 'TRAN_PARTICULAR' and 'TRAN_PARTICULAR_2' columns into a single string
            combined_particulars = str(row['TRAN_PARTICULAR']) + str(row['TRAN_PARTICULAR_2'])

            if "100000" in combined_particulars:
                id_list = re.findall(r'10*[0-9]{7}', combined_particulars)
                if id_list:
                    # Assuming there's only one match, replace "100000" with an empty string
                    transaction_id = id_list[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id

            elif "200000" in combined_particulars:
                id_list = re.findall(r'10*[0-9]{7}', combined_particulars)
                if id_list:
                    # Assuming there's only one match, replace "200000" with an empty string
                    transaction_id = id_list[0].replace("200000", "")
                    self.bank_statement_df.loc[index, 'Transaction id'] = transaction_id
        display(f"Total tid of bank==> {self.bank_statement_df['Transaction Id'].count()}")

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Tran_Particular" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            # Concatenate the values from 'TRAN_PARTICULAR' and 'TRAN_PARTICULAR_2' columns into a single string
             for roww in (row['Desc2'] , row['Desc1']):
                # id = ''
                if "NPS-IF-" in roww:
                    id = re.findall(r'[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                    break
                
                elif "FTMS-" in roww:
                    id = re.findall(r'[0-9]{6}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                    break
                
                elif "10000" in roww:
                    id = re.findall(r'10*[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")
                    break
                
                    
                elif re.findall(r'\d{7}-.*', roww):
                    id = re.findall(r'[0-9]{7}', roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
        display(f"Total tid of bank==> {self.bank_statement_df['Transaction Id'].count()}")

    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['PART_TRAN_TYPE'] == 'D' :
            mode = 'DR'
            amount = row['TRAN_AMT']
        elif row['PART_TRAN_TYPE'] == 'C':
            mode = 'CR'
            amount = row['TRAN_AMT']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])

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

    @run_phase(phase_number=1)
    def convert_date_format(self,input_date):
        """
        Converting the date format to the standard format to match it with the soa statement
        """
        parsed_date = datetime.strptime(input_date, "%d-%b-%Y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        return formatted_date  