from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class NICAsiaBank(Reconcile):
    def __init__(self,bank_name,excel_writer):
        """
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name,excel_writer)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.NICAsia_BANK_FILE, skiprows= 1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.NICAsia_SOA_FILE, encoding='latin-1')
        

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase_4()
        self.updated_standardize_bank_stmt()
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
        self.bank_statement_df.drop(columns=['Unnamed: 0','Unnamed: 3','Unnamed: 4','Unnamed: 8','Unnamed: 6','Unnamed: 11','Unnamed: 12','Unnamed: 14','Unnamed: 15','Unnamed: 16','Unnamed: 17','Unnamed: 18'], inplace=True)
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['DATE'],format="%Y/%m/%d").dt.date
        display(f'columns-->{self.bank_statement_df.columns}')  

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "TRAN PARTICULAR" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            if "100000" in str(row["TRAN PARTICULAR"]):
                id_matches = re.findall(r'10*[0-9]{6}', str(row["TRAN PARTICULAR"]))
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
        if row['DR. AMT'] > 0:
            mode = 'DR'
            amount = row['DR. AMT']
        elif row['CR. AMT'] > 0:
            mode = 'CR'
            amount = row['CR. AMT']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
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
            amount = abs(row['Amount'])
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Desc2" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            # if "WT" in str(row['Desc2']):
            #     id = str(row['Desc2']).replace('WT','')
            #     id = re.findall(r'[0-9]{7}', str(row['Desc2']))
            #     id =  id[0].replace("10000000", "")
            #     self.bank_statement_df.at[index, 'Transaction Id'] = id[0]
            if "WT10000" in str(row['Desc2']):
                id = str(row['Desc2'])[-5:]
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue

            elif "NPS-IF-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{7}', str(row['Desc2']))
                self.bank_statement_df.at[index, 'Transaction Id'] = id[0]
                continue

            elif "FTMS-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{6}', str(row['Desc2']))
                self.bank_statement_df.at[index, 'Transaction Id'] = id[0]
                continue

            elif "10000" in str(row['Desc2']):
                id = re.findall(r'10*[0-9]{7}', str(row['Desc2']).split(',')[0])
                id =  id[0].replace("10000", "")
                self.bank_statement_df.at[index, 'Transaction Id'] = id
                continue

            elif "10000" in str(row['Desc1']):
                id = re.findall(r'10*[0-9]{7}', str(row['Desc1']))
                id =  id[0].replace("10000", "")
                self.bank_statement_df.at[index, 'Transaction Id'] = id

        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')
