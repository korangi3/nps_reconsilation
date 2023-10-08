from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class ADBLBank(Reconcile):
    """
        Initialize an ADBLBank reconciliation instance.

        :param bank_name: The name of the bank.
        :param excelwriter: Excel writer object to output reconciliation results.
    """
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
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.ADBL_BANK_FILE)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.ADBL_SOA_FILE, encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        try:
            self.bank_statement_df = pd.read_excel(Banks_FILEPATH.ADBL_BANK_FILE, skiprows= 8)
            self.soa_statement_df = pd.read_csv(SOA_FILEPATH.ADBL_SOA_FILE, encoding='latin-1')
        except:
            self.proceed = False

    def main(self):
        """
        Executes the entire reconciliation workflow step by step.
        """
        if self.proceed:
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
        else:
            display('No data for ADBL')

    @run_phase(phase_number=1)
    def preprocessing_bank_stmt(self):
        """
        Drop unnecessary rows and standardize column names.
        """
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        display(f'columns-->{self.bank_statement_df.columns}')  

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        """
        Convert date format and classify transactions as debit or credit.
        """
        self.bank_statement_df['Date'] = self.bank_statement_df['Value Date']
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y%m%d").dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        '''
        Extracts transaction id from bank statement.
        '''

        for index, row in self.bank_statement_df.iterrows():
            if "100000" in str(row["Narrative"]):
                #extracting the six digit transaction code from the  the Narrative column of the bank statement after 100000
                id_matches = re.findall(r'10*[0-9]{6}', str(row["Narrative"]))
                if id_matches:
                    id = id_matches[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
            soa_remarks = row['SOA Remark']
            if pd.notna(soa_remarks): 
                # Check if 'SOA Remarks' is not NaN
                self.bank_statement_df.at[index, 'Transaction Id'] = soa_remarks
        display('total_tid', self.bank_statement_df['Transaction Id'].count())

    @run_phase(phase_number=1)
    def standard_format(self,row):
        """
        Standardize transaction amount and mode.

        Classify transactions as debit (DR) or credit (CR).
        """
        if abs(row['DEBIT']) > 0:
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
    def preprocessing_bank_stmt_phase_4(self):
        """
        Drop unnecessary rows and standardize column names.
        """
        self.bank_statement_df.drop(self.bank_statement_df.index[0],inplace=True)
        self.bank_statement_df.drop(self.bank_statement_df.index[-1], inplace=True)
        self.bank_statement_df["DEBIT"] = self.bank_statement_df["DEBIT"].str.replace("'","").str.replace(",","")
        self.bank_statement_df["DEBIT"].fillna("0.0", inplace=True)  
        self.bank_statement_df['DEBIT']= self.bank_statement_df['DEBIT'].astype(float)

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        """
        Convert date format and classify transactions as debit or credit.
        """
        self.bank_statement_df['Date'] = self.bank_statement_df['Value Date']
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y%m%d").dt.date
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)    

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        '''
        Extracts transaction id from bank statement.
        '''
        for index, row in self.bank_statement_df.iterrows():
            if "NPS-IF-" in str(row["Narrative"]):
                id = re.findall(r'[0-9]{7}',str(row["Narrative"]))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]

            elif "10000" in str(row["Narrative"]):
                id = re.findall(r'10*[0-9]{7}',str(row["Narrative"]))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0].replace("10000","")
            
            elif "FTMS-" in str(row["Narrative"]):
                id = re.findall(r'[0-9]{6}',str(row["Narrative"]))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
        display('total_tid', self.bank_statement_df['Transaction Id'].count())

    @run_phase(phase_number=4)
    def standard_format_phase_4(self,row):
        """
        Standardize transaction amount and mode.

        Classify transactions as debit (DR) or credit (CR).
        """
        if abs(row['DEBIT']) > 0:
            mode = 'DR'
            amount = row['DEBIT']
        elif row['CREDIT'] > 0:
            mode = 'CR'
            amount = row['CREDIT']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])