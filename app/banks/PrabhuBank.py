from ReconcileAbstract import Reconcile
from Constants import Banks_FILEPATH, SOA_FILEPATH
from qrlib.QRUtils import display
from utils.Utils import run_phase
import pandas as pd
import numpy as np
import re

class PrabhuBank(Reconcile):
    def __init__(self, bank_name, excelwriter):
        '''
        Parameters:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        '''
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.PRABHU_BANK_FILE,skiprows=1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.PRABHU_SOA_FILE, encoding='latin-1', skiprows=1)
        display(self.bank_statement_df.head())
        display(self.soa_statement_df.head())

    def main(self):
        '''
        This method orchestrates the entire reconciliation process by calling various steps.
        '''
        self.preprocessing_soa_stmt()
        self.preprocessing_bank_stmt()
        self.preprocessing_bank_stmt_phase_4()
        self.convert_standard_bank_stmt()
        self.convert_standard_bank_stmt_phase_4()
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
        This method removes irrelevant entries from the bank statement DataFrame.
        '''
        self.bank_statement_df = self.bank_statement_df.loc[self.bank_statement_df['FORACID']!='*********Opening Baln************']
        self.bank_statement_df = self.bank_statement_df.loc[self.bank_statement_df['FORACID']!=np.NaN]

    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        '''
        This method removes irrelevant entries from the bank statement DataFrame.
        '''
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date
        display(f"bank_date {self.bank_statement_df['Date']}")

    @run_phase(phase_number=1)
    def convert_standard_bank_stmt(self):
        """
        Convert and standardize bank statement data.

        Converts date columns and applies formatting to bank statement data.
        """
        # self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['TRAN_DATE'], format='%m/%d/%Y %I:%M:%S %p')
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)

    @run_phase(phase_number=4)
    def convert_standard_bank_stmt_phase_4(self):
        """
        Convert and standardize bank statement data.

        Converts date columns and applies formatting to bank statement data.
        """
        # self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['TRAN_DATE'], format='%m/%d/%Y %I:%M:%S %p')
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)

    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        """
        if row['DEBIT'] > 0:
            mode = 'DR'
            amount = row['DEBIT']
        elif row['CREDIT'] > 0:
            mode = 'CR'
            amount = row['CREDIT']
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
    def extracting_tid_from_bank_stmt(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs using various patterns from bank statement descriptions.
        """
        count = 1
        for index, row in self.bank_statement_df.iterrows():
            combined_foracid = str(row['FORACID'])

            if "10000" in str(combined_foracid):
                id = re.sub(r'10*', '', combined_foracid, count=1)
                transaction_id = id
            elif "ATM" in combined_foracid or "CHG" in combined_foracid:
                parts = combined_foracid.split('-')
                parts_len = len(parts)
                if parts_len <= 1:
                    count+=1
                    continue
                transaction_id = parts[-1]
            else:
                count+=1
                continue

            self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id
        display('total_tid',self.bank_statement_df['Transaction Id'].count())

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        """
        Extract transaction IDs from bank statement data.

        This method extracts transaction IDs using various patterns from bank statement descriptions.
        """
        display(self.bank_statement_df.head())
        for index, row in self.bank_statement_df.iterrows():
            for roww in (row['Desc2'] , row['Desc1']):
                id = ''
                roww = str(roww)
                if "NPS-IF-" in roww:
                    id = re.findall(r'[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                    break
                
                
                elif "10000" in roww:
                    id = re.findall(r'10*[0-9]{7}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")
                    break
                
                elif "FTMS-" in roww:
                    id = re.findall(r'[0-9]{6}',roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                    
                elif re.findall(r'\d{7}-.*', roww):
                    id = re.findall(r'[0-9]{7}', roww)
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
        display('total_tid',self.bank_statement_df['Transaction Id'].count())

