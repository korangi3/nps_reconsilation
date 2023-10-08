from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import warnings
warnings.filterwarnings("ignore")
warnings.resetwarnings()
import pandas as pd
import re

class NMBBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.NMB_BANK_FILE,skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.NMB_SOA_FILE, encoding='latin-1')
        

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt_phase_4()
        self.updated_standardize_bank_stmt_phase_4()
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
        # self.write_soa_data()
        # self.write_bank_data()
        self.generate_report()

    
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        '''
         This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report if needed
        '''
        self.bank_statement_df['Merged_Description'] = self.bank_statement_df['Desc1'].astype(str) + self.bank_statement_df['Desc3']
        self.bank_statement_df.drop(columns=['Desc1','Desc3'],inplace=True)
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date

        # self.bank_statement_df['Desc2'] = self.bank_statement_df['Desc2'].astype(str)
        # self.bank_statement_df['Desc2'] = self.bank_statement_df['Desc2'].str.rstrip('.0')
        # self.bank_statement_df = self.bank_statement_df.loc[self.bank_statement_df['Desc1'] != '~Date summary']
        # self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['TranDate'],format="%d/%m/%Y").dt.date

   
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
            if 'NPS-IF-' in str(row["Merged_Description"]):
                match = re.search(r'NPS-IF-(\d{7})', str(row["Merged_Description"]))
                if match:
                    id = match.group(1)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            # elif 'F-' in str(row["Merged_Description"]):
            #     match = re.search(r'F-(\d{7})', str(row["Merged_Description"]))
            #     if match:
            #         id = match.group(1)
            #         self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "FTMS-" in str(row["Merged_Description"]):
                id = re.findall(r'[0-9]{6}', str(row["Merged_Description"]))
                self.bank_statement_df.loc[index, 'Transaction ID'] = id[0]
            elif "10000" in str(row["Merged_Description"]):
                id = re.findall(r'10000*[0-9]{7}',str(row["Merged_Description"]))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")
            # elif "FTMS-" in str(row["Merged_Description"]):
            #     match = re.search(r'FTMS-(\d+)',str(row["Merged_Description"]))
            #     if match:
            #         id= match.group(1)
            #         self.bank_statement_df.loc[index, 'Transaction Id'] = id

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
            amount = abs(row['Amount'])
        elif row['Txn Type'] == 'C':
            mode = 'CR'
            amount = abs(row['Amount'])
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])