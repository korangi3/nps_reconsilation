from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class ShangrillaBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.SHANGRILLA_BANK_FILE, skiprows= 1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.SHANGRILLA_SOA_FILE, encoding='latin-1')
        

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
        self.write_bank_data()
        self.write_soa_data()
        self.generate_report()

    @run_phase(phase_number=1)
    def preprocessing_bank_stmt(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report
        '''
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df = self.bank_statement_df.loc[self.bank_statement_df['Desc1'] != '~Date summary']
        self.bank_statement_df['Date'] = self.bank_statement_df['TranDate']
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%d/%m/%Y").dt.date
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'Date-->{self.bank_statement_df["Date"]}')  

    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report if needed
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date

              
    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        '''
        applies formatting to the column by calling the Standard_format function.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)  

    @run_phase(phase_number=4)     
    def updated_standardize_bank_stmt_phase_4(self):
        '''
        applies formatting to columns.
        '''
        result = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)

        # Check if 'Mode' and 'Amount' columns exist in self.bank_statement_df, and if not, create them.
        if 'Mode' not in self.bank_statement_df.columns:
            self.bank_statement_df['Mode'] = None
        if 'Amount' not in self.bank_statement_df.columns:
            self.bank_statement_df['Amount'] = None

        # Assign the values from the result to the corresponding columns.
        self.bank_statement_df[['Mode', 'Amount']] = result


    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extracting the transaction id from the column 'Desc2' using regular expression 
        """
        for index, row in self.bank_statement_df.iterrows():
            if "100000" in str(row["Desc2"]):
                id_matches = re.findall(r'10*[0-9]{6}', str(row["Desc2"]))
                if id_matches:
                    id = id_matches[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            desc2_str = str(row["Desc2"])
            matches = re.findall(r'\b\d{2,4}\b', desc2_str)
            if matches:
                id = matches[0]
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extracting the transaction id from the column 'Desc2' using regular expression 
        """
        for index, row in self.bank_statement_df.iterrows():
    # print(self.bank_statement_df.iloc[index]['Transaction ID'])
            for roww in (row['Desc2'] , row['Desc3']):
                id = ''
                if "NPS-IF-" in roww:
                    id = re.findall(r'[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                    break
                
                
                elif "10000" in roww:
                    if re.findall(r'#10*\d{7}',roww):
                        continue
                    id = re.findall(r'10*[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")
                    break
                
                elif "FTMS-" in roww:
                    id = re.findall(r'[0-9]{6}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
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
    def standard_format_phase_4(self, row):
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
            amount = abs(row['Amount'])
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
