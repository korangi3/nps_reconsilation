from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class CenturyBank(Reconcile):
    def __init__(self,bank_name,excel_writer):
        super().__init__(bank_name,excel_writer)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.CENTURY_BANK_FILE, skiprows= 1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.CENTURY_SOA_FILE, encoding='latin-1')
        

    def main(self):
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.updated_standardize_bank_stmt()
        self.extracting_tid_from_bank_stmt()
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
        Cleaning the bank statement data if necessary and also convert the date into the standard format to matched it with the soa
        '''
        self.bank_statement_df = self.bank_statement_df.loc[self.bank_statement_df['Particulars'] != '~~Date summary Balance']
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'],format="%Y-%m-%d").dt.date
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  
        display(f'Date-->{self.bank_statement_df["Date"]}')  

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        '''
        Extracting the transaction ID from the bank statement
        '''
        for index, row in self.bank_statement_df.iterrows():
            combined_particulars = str(row['TID'])
            if "100000" in combined_particulars:
                #extracting the Transaction Id after 100000 of gateway transaction type
                id_list = re.findall(r'10*[0-9]{6}', combined_particulars)
                if id_list:
                    # Assuming there's only one match, replace "100000" with an empty string
                    transaction_id = id_list[0].replace("100000", "")
                    self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id
            #split the row particulars column value and take a transaction id from the index 1
            t_id = str(row['Particulars']).split()
            tid_val = [item for item in t_id if item.strip()]  # Remove empty elements
            if len(tid_val) > 1:
                transaction_id = tid_val[1]
                self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id
        display('total_tid', self.bank_statement_df['Transaction Id'].count())

    @run_phase(phase_number=1)
    def standard_format(self,row):
        '''
        Standardizing the bank statement format with similar column of the SOA statement
        '''
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
