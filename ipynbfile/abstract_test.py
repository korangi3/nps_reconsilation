from qrlib.QRComponent import QRComponent
from RPA.Browser.Selenium import Selenium
from abc import abstractmethod, ABC
from DatabaseComponent import SOA_Report, Bank_Report
import datetime
import pandas as pd
from qrlib.QRUtils import display
from qrlib.QREnv import QREnv

class Reconcile(QRComponent, ABC):
    matched_soa_with_bank:pd.DataFrame = None
    unmatched_soa_with_bank:pd.DataFrame = None
    matched_bank_with_soa:pd.DataFrame = None
    unmatched_bank_with_soa:pd.DataFrame = None

    bank_statement_df:pd.DataFrame = None
    soa_statement_df:pd.DataFrame = None

    def __init__(self, bank_name):
        QRComponent.__init__(self)
        self.site_url = 'https://adminonepg.nepalpayment.com/'
        self.selenium:Selenium = Selenium()
        self.soa_report_db = SOA_Report()
        self.bank_report_db = Bank_Report()
        self.bank_name = bank_name
        

    @abstractmethod
    def main(self):
        pass

    def signin(self):
        pass


    def preprocessing_soa_stmt(self):
        self.soa_statement_df['Transaction Id'] =  self.soa_statement_df['Transaction Id'].str.strip("'").dropna()
        self.soa_statement_df['Date'] = self.soa_statement_df['Date'].astype(str)
        for index, date in enumerate(self.soa_statement_df['Date']):
            self.soa_statement_df.loc[index, 'Date'] = date.split(' ')[0]

    
    def matching_bank_stmt_with_soa(self):
        for index1 , bank_statement in self.bank_statement_df.iterrows():
            if bank_statement['Transaction Id'] in (self.soa_statement_df['Transaction Id'].values):
                self.bank_statement_df.loc[index1,'Matched_TID'] = bank_statement['Transaction Id']
                continue
            self.bank_statement_df.loc[index1,'Unmatched_TID'] = bank_statement['Transaction Id']
        self.unmatched_rows_bank_with_soa = self.bank_statement_df[self.bank_statement_df['Unmatched_TID'].notnull()]
        self.matched_rows_bank_with_soa = self.bank_statement_df[self.bank_statement_df['Matched_TID'].notnull()]
        display(f"total unmatched TID with soa-->{self.bank_statement_df['Unmatched_TID'].count()}")  
        display(f"total matched TID-->{self.bank_statement_df['Matched_TID'].count()}")
        display(f'unmatched data of bank with soa-->{self.unmatched_rows_bank_with_soa}')


    def matching_soa_stmt_with_bank_stmt(self):
        for index1, statement_soa in self.soa_statement_df.iterrows():
            transaction_id = statement_soa['Transaction Id']

            if transaction_id in self.bank_statement_df['Transaction Id'].values:
                self.soa_statement_df.loc[index1,'Matched_TID'] = transaction_id
                continue
            self.soa_statement_df.loc[index1,'Unmatched_tid'] = transaction_id
        self.matched_row = self.soa_statement_df[self.soa_statement_df['Matched_TID'].notnull()]
        self.unmatched_soa_with_bank = self.soa_statement_df[self.soa_statement_df['Unmatched_tid'].notnull()]
        display(f"number of soa transaction matched with bank-->{self.soa_statement_df['Matched_TID'].count()}")
        display(f"number of soa transaction unmatched with bank-->{self.soa_statement_df['Unmatched_tid'].count()}")
        display(f"Unmatched soa with bank-->{self.unmatched_soa_with_bank.head()}")


    def total_debit_credit_amount_of_bank(self):
        credit = self.bank_statement_df[self.bank_statement_df['Mode'] == 'CR']
        self.total_credit_bank = credit['Amount'].sum()
        display(f'total bank credit amount {self.total_credit_bank}')
        debit = self.bank_statement_df[self.bank_statement_df['Mode'] == 'DR']
        self.total_debit_bank = debit['Amount'].sum()
        display(f'total bank debit amount {self.total_debit_bank}')


    def total_debit_credit_amount_of_soa(self):
        credit = self.soa_statement_df[self.soa_statement_df['Mode'] == 'CR']
        self.credit_amount_soa = credit['Amount'].sum()
        display(f'total soa credit amount {self.credit_amount_soa}')
        debit = self.soa_statement_df[self.soa_statement_df['Mode'] == 'DR']
        self.debit_amount_soa = debit['Amount'].sum()
        display(f'total soa debit amount {self.debit_amount_soa}')


    def extract_number_of_tid_CR_and_DR_from_soa(self):
        soa_stmt_of_dr = self.soa_statement_df[self.soa_statement_df['Mode']== 'DR']
        self.total_tid_of_debit_of_soa = soa_stmt_of_dr['Transaction Id'].count()
        soa_stmt_of_cr = self.soa_statement_df[self.soa_statement_df['Mode']== 'CR']
        self.total_tid_of_credit_of_soa =soa_stmt_of_cr['Transaction Id'].count()


    def extract_number_of_tid_CR_and_DR_from_bank_stmt(self):
        bank_stmt_of_dr = self.bank_statement_df[self.bank_statement_df['Mode']== 'DR']
        self.bank_debit_tid = bank_stmt_of_dr['Remarks'].count()
        display(f'bank debit transaction id-->{self.bank_debit_tid}')
        bank_stmt_of_cr = self.bank_statement_df[self.bank_statement_df['Mode']== 'CR']
        self.bank_credit_tid =bank_stmt_of_cr['Remarks'].count()
        display(f'bank credit transaction id-->{self.bank_credit_tid}')   


    def debit_credit_amount_matches_tid_of_bank_with_soa(self):
        credit = self.matched_rows_bank_with_soa[self.matched_rows_bank_with_soa['Mode'] == 'CR']
        total_credit_amount_matches_of_tid_with_bank = credit['Amount'].sum()
        display(f'Total credit that matches tid of bank with soa: {total_credit_amount_matches_of_tid_with_bank}')
        debit = self.matched_rows_bank_with_soa[self.matched_rows_bank_with_soa['Mode'] == 'DR']
        total_debit_amount_matches_of_tid_with_bank_to_soa = debit['Amount'].sum()
        display(f'Total debit that matches tid of bank with soa: {total_debit_amount_matches_of_tid_with_bank_to_soa}')


    def debit_credit_amount_of_soa_matched_with_bank(self):
        credit = self.matched_row[self.matched_row['Mode'] == 'CR']
        credit_amount_soa_matched_with_bank = credit['Amount'].sum()
        display(f'credit amout of soa matched with bank {credit_amount_soa_matched_with_bank}')
        debit = self.matched_row[self.matched_row['Mode'] == 'DR']
        debit_amount_soa_matched_with_bank = debit['Amount'].sum()
        display(f'debit amount of soa matched with bank {debit_amount_soa_matched_with_bank}')     


    def write_soa_data(self):
        created_at = datetime.date.today()
        updated_at = created_at
        for soa_index, soa_statement in self.soa_statement_df.iterrows():
            transaction_id = soa_statement['Transaction Id']
            transaction_type = soa_statement['Transaction Type']
            transaction_mode = soa_statement['Mode']
            transaction_amount = soa_statement['Amount']
            transaction_date = soa_statement['Date']
            if transaction_id == soa_statement['Matched_TID']:
                status = 'Matched'
            else:
                status = 'UnMatched'


            transaction_check = self.soa_report_db.objects().filter(
                bank_name = self.bank_name,
                transaction_id = transaction_id,
                transaction_type = transaction_type,
                transaction_mode = transaction_mode,
                transaction_amount = transaction_amount,
                transaction_date = transaction_date,
                status = status,
            )
            if transaction_check:
                continue

            self.soa_report_db.create(
                bank_name = self.bank_name,
                transaction_id = transaction_id,
                transaction_type = transaction_type,
                transaction_mode = transaction_mode,
                transaction_amount = transaction_amount,
                transaction_date = transaction_date,
                status = status,
                created_at = created_at,
                updated_at = updated_at
            )


    def write_bank_data(self):
        created_at = datetime.date.today()
        updated_at = created_at

        for bank_index, bank_statement in self.bank_statement_df.iterrows():
            transaction_id = bank_statement['Transaction Id']
            # transaction_type = bank_statement['Transaction Type']

            transaction_mode = bank_statement['Mode']
            transaction_amount = bank_statement['Amount']
            transaction_date = bank_statement['Date']
            if transaction_id == bank_statement['Matched_TID']:
                status = 'Matched'
            else:
                status = 'UnMatched'

            transaction_check = self.bank_report_db.objects().filter(
                bank_name = self.bank_name,
                transaction_id = transaction_id,
                # transaction_type = transaction_type,
                transaction_mode = transaction_mode,
                transaction_amount = transaction_amount,
                transaction_date = transaction_date,
                status = status,
            )
            if transaction_check:
                continue

            self.bank_report_db.create(
                bank_name = self.bank_name,
                transaction_id = transaction_id,
                # transaction_type = transaction_type,
                transaction_mode = transaction_mode,
                transaction_amount = transaction_amount,
                transaction_date = transaction_date,
                status = status,
                created_at = created_at,
                updated_at = updated_at
            )


    def generate_report(self):
        soa_data = {
        'no. of transaction of soa': [self.total_tid_of_credit_of_soa, self.total_tid_of_debit_of_soa],  
        'total amount of transaction of soa': [self.credit_amount_soa, self.debit_amount_soa]     
        }
        bank_data = {
            'no. of transaction of bank': [self.bank_credit_tid, self.bank_debit_tid],   
            'total amount of transaction of bank': [self.total_credit_bank, self.total_debit_bank]     
            }
        rows = ['CR', 'DR']
        df_soa_report = pd.DataFrame(soa_data, index=rows)
        df_bank_report = pd.DataFrame(bank_data, index=rows)

        display(f'soa report of reconcilation -->{df_soa_report}')
        excel_writer = pd.ExcelWriter(f'output/{self.bank_name}_reconciliation.xlsx', engine='xlsxwriter')
        df_soa_report.to_excel(excel_writer, sheet_name=f'{self.bank_name}_reconciliation_report')
        self.unmatched_soa_with_bank.to_excel(excel_writer, sheet_name=f'{self.bank_name}_reconciliation_report', startrow=df_soa_report.shape[0] + 2, index=False)
        display(f'bank report of reconcilation -->{df_bank_report}')
        df_bank_report.to_excel(excel_writer, sheet_name=f'{self.bank_name}_reconciliation_report', startrow=0, startcol=13)
        self.unmatched_rows_bank_with_soa.to_excel(excel_writer, sheet_name=f'{self.bank_name}_reconciliation_report', startrow=df_bank_report.shape[0] + 2, startcol=13, index=False)
        excel_writer.close()
