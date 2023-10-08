from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import re

class CitizenBank(Reconcile):
    def __init__(self,bank_name,excelwriter):
        super().__init__(bank_name,excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.CITIZEN_BANK_FILE, skiprows= 1)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.CITIZEN_SOA_FILE, encoding='latin-1')
        

    def main(self):
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
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Tran Date'],format='%Y-%m-%d').dt.date
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  
        display(f"bank date====>{self.bank_statement_df['Date']}")

    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')  
        display(f"bank date====>{self.bank_statement_df['Date']}")

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=4)
    def updated_standardize_bank_stmt_phase_4(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format_phase_4, axis=1)    


    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        for index, row in self.bank_statement_df.iterrows():
            #Extracting the transaction id from the column name Tran Particular which contain the transaction id in the form of 100000045678 this RE remove the 100000 and give 5 digit after it
            extracted_number_1000000 = re.findall(r'1000000(\d{5})', str(row["Tran Particular"]))
            extracted_number_100000 = re.findall(r'100000(\d{6})', str(row["Tran Particular"]))

            if extracted_number_1000000:
                extracted_number = extracted_number_1000000[0]
                self.bank_statement_df.at[index, 'Transaction Id'] = extracted_number
            elif extracted_number_100000:
                extracted_number = extracted_number_100000[0]
                self.bank_statement_df.at[index, 'Transaction Id'] = extracted_number
                
            particular_str = row["Tran Particular"]
            cips_matches = re.findall(r'cIPS/\d+/(\d+)/\d+', particular_str)#extracting the transaction id afeter CIPS in the column name Tran Particular
            
            if not cips_matches:
                continue
            transaction_id = cips_matches[0]
            self.bank_statement_df.loc[index, 'Transaction Id'] = transaction_id
        display(f"total_tid {self.bank_statement_df['Transaction Id'].count()}")
        display(f"transaction_id ====>{self.bank_statement_df['Transaction Id']}")

    @run_phase(phase_number=4)
    def extracting_tid_from_bank_stmt_phase_4(self):
        for index, row in self.bank_statement_df.iterrows():
            if "10000" in str(row['Desc1']):
                id = re.findall(r'10*[0-9]{7}', str(row['Desc1']))
                id =  id[0].replace("10000", "")
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "NPS-IF-" in str(row['Desc3']):
                id = re.findall(r'[0-9]{7}', str(row['Desc3']))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
            elif "FTMS-" in str(row['Desc3']):
                id = re.findall(r'[0-9]{6}', str(row['Desc3']))
                self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
        display(f"total_tid {self.bank_statement_df['Transaction Id'].count()}")
        display(f"transaction_id ====>{self.bank_statement_df['Transaction Id']}")

    @run_phase(phase_number=1)
    def standard_format(self,row):
        '''
    Standardizing the bank statement format with similar column of the SOA statement
    '''
        if row['Dr Amount'] > 0:
            mode = 'DR'
            amount = row['Dr Amount']
        elif row['Cr Amount'] > 0:
            mode = 'CR'
            amount = row['Cr Amount']
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
