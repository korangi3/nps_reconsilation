from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class MblBank(Reconcile):
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
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.MBL_BANK_FILE, skiprows= 2)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.MBL_SOA_FILE, encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.MBL_BANK_FILE, skiprows= 1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.MBL_SOA_FILE, encoding='latin-1')
        

    def main(self):
        '''
         This method orchestrates the entire reconciliation process by calling various steps.
        '''
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase4()
        self.updated_standardize_bank_stmt()
        self.updated_standardize_bank_stmt_phase4()
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
        display(f'bank statement MBL conlumn === {self.bank_statement_df.columns}')
        self.bank_statement_df = self.bank_statement_df[(~self.bank_statement_df['Txn Reference'].str.contains('TRTR')) &
        (~self.bank_statement_df['Txn Reference'].str.contains('TRRR'))
        ]
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Txn Date']).dt.date
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'Date-->{self.bank_statement_df["Date"]}')

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        '''
        applies formatting to columns.
        '''
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs from "Txn Reference" columns.
        """
        for index, row in self.bank_statement_df.iterrows():
            for roww in (row['Desc1'] , row['Desc2']):
        
                if "NPS-IF-" in roww:
                    id = re.findall(r'[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction ID'] = id[0]
                    break
                
                elif "10000" in roww:
                    id = re.findall(r'10*[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction ID'] = id[0].replace("10000","")
                    break
                
                elif "FTMS-" in roww:
                    id = re.findall(r'[0-9]{6}',roww)
                    self.bank_statement_df.loc[index, 'Transaction ID'] = id[0]
                    
                elif re.findall(r'\d{7}-.*', roww):
                    id = re.findall(r'[0-9]{7}', roww)
                    self.bank_statement_df.loc[index, 'Transaction ID'] = id[0]
            ''' This code is commented.
            if '100000' in row['Txn Reference']:
            # Split the description into words
                description_words = row['Txn Reference'].split("/")
                value = description_words[0]
                id = re.sub(r'10*', '', value, count=1)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            '''

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
        if row['Txn Amount'] == 'D' :
            mode = 'DR'
            amount = abs(row['Txn Amount'])
        elif row['Part Txn Type'] == 'C':
            mode = 'CR'
            amount = row['Txn Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase4(self):
        '''
        This method cleans and formats the bank statement DataFrame and also format the Date to match it with the Soa report if needed
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase4(self):
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
            if "NPS-IF-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{7}', str(row['Desc2']))
                if not id:
                    continue
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                continue
            elif "FTMS-" in str(row['Desc2']):
                id = re.findall(r'[0-9]{6}', str(row['Desc2']))
                if not id:
                    continue
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                continue
            elif "10000" in str(row['Desc2']):
                # id = re.findall(r'10*[0-9]{7}', str(row['Desc2']))
                # if not id:
                #     continue
                id = row['Desc2']
                index_10000 = id.index('10000')
                id = id[index_10000:index_10000+12]
                id =  id.replace("10000", "")
                
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "10000" in str(row['Desc1']):
                display(row['Desc1'])
                # id = re.findall(r'10*[0-9]{7}', str(row['Desc1']))
                # if not id:
                #     continue
                id = row['Desc1']
                # id = id[0]
                
                index_10000 = id.index('10000')
                id = id[index_10000:index_10000+12]
                id =  id.replace("10000", "")
                
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif re.findall(r'[0-9]{7}', str(row['Desc1'])):
                id = re.findall(r'[0-9]{7}', str(row['Desc1']))
                if not id:
                    continue
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')   
