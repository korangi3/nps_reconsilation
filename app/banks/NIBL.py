from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
from bs4 import BeautifulSoup
import pandas as pd
import re

class NIBLBank(Reconcile):
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
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.NIBL_BANK_FILE, skiprows= 9)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.NIBL_SOA_FILE, encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        self.NIBLPath = Banks_FILEPATH.NIBL_BANK_FILE
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.NIBL_SOA_FILE, encoding='latin-1')

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        # display(f'{self.bank_statement_df.head()}')
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
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
         # Convert 'Date' column to datetime if not already done
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Transaction Date'],format="%d/%m/%Y").dt.date
        
        self.bank_statement_df['Transaction Amount'] = pd.to_numeric(self.bank_statement_df['Transaction Amount'].str.replace(',', ''), errors='coerce') 
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        '''
        calling the standard format function below
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Desc2" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            # Check if 'Description' column has spaces
            if not (' ' in row['Description']):
                continue

            # Split the description into words
            description_words = row['Description'].split()

            # Check if there are at least 3 words (index 0, 1, 2)
            if len(description_words) >= 3:
                value = description_words[2]
                if '100000' in value:
                # Use regular expression to remove '10*' from the value
                    id = re.sub(r'10*', '', value, count=1)

                # Update 'Transaction Id' column with the extracted id
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
        if row['Cr/Dr'] == 'Dr' :
            mode = 'DR'
            amount = row['Transaction Amount']
        elif row['Cr/Dr'] == 'Cr':
            mode = 'CR'
            amount = row['Transaction Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])



    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
         # Convert 'Date' column to datetime if not already done
        # self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Transaction Date'],format="%d/%m/%Y").dt.date
        
        # self.bank_statement_df['Transaction Amount'] = pd.to_numeric(self.bank_statement_df['Transaction Amount'].str.replace(',', ''), errors='coerce') 

        with open(self.NIBLPath, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        file.close()

        self.bank_statement_df = pd.read_html(str(table), skiprows=2)[0]
        # Set the values in the first row as column names
        self.bank_statement_df.columns = self.bank_statement_df.iloc[0]
        # Drop the first row (which is now the column names)
        self.bank_statement_df = self.bank_statement_df.iloc[1:]
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Transaction Date'], format="%m/%d/%Y").dt.date
        self.bank_statement_df['Transaction Amount'] = self.bank_statement_df['Transaction Amount'].astype(float)

    

        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        '''
        calling the standard format function below
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)
        self.bank_statement_df.drop(columns=['Cr/Dr','Transaction Amount'],axis=1,inplace=True)
          

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Desc2" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            if "NPS-IF-" in str(row["Description"]):
                match = re.search(r'NPS-IF-(\d{7})', str(row["Description"]))
                if match:
                    id = match.group(1)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id

            elif "10000" in str(row["Description"]):
                id = re.findall(r'10000*[0-9]{7}',str(row["Description"]))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")
            
            elif "FTMS-" in str(row["Description"]):
                match = re.search(r'FTMS-(\d+)',str(row["Description"]))
                if match:
                    id= match.group(1)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
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
        if row['Cr/Dr'] == 'Dr' :
            mode = 'DR'
            amount = abs(row['Transaction Amount'])
        elif row['Cr/Dr'] == 'Cr':
            mode = 'CR'
            amount = row['Transaction Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])