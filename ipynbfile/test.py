from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_file
from Constants import SOA_FILE
from xlsxwriter import Workbook
import pandas as pd
import re


class EverestBank(Reconcile):
    def __init__(self):
        super().__init__()
        self.bank = Banks_file()
        self.soa = SOA_FILE()
        # self.url = 'https://adminonepg.nepalpayment.com/'
        self.bank_statement_df = pd.read_excel(self.bank.EVEREST_BANK_FILE,skiprows= 11)
        self.soa_statement_df = pd.read_csv(self.soa.EVEREST_SOA_FILE,encoding='latin-1')
        

    def main(self):
        display(f'{self.bank_statement_df.head()}')
        display(f'{self.soa_statement_df.head()}')
        self.preprocessing_bank_stmt()
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)
        # display(f'bank columns after standard format-->{self.bank_statement_df.columns}')
        bank_stmt_with_tid = self.extracting_tid_from_bank_stmt(self.bank_statement_df)
        soa_stmt = self.preprocessing_soa_stmt(self.soa_statement_df)
        self.matching_bank_stmt_with_soa(bank_stmt_with_tid,soa_stmt)
        self.matching_soa_stmt_with_bank_stmt(bank_stmt_with_tid,soa_stmt)
        self.total_debit_credit_amount_of_soa()
        self.total_debit_credit_amount_of_bank()
        self.debit_credit_amount_matches_tid_of_bank_with_soa()
        self.debit_credit_amount_of_soa_matched_with_bank()
        self.extract_number_of_tid_CR_and_DR_from_soa()
        self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
        self.report_of_soa_stmt()
        self.report_of_bank_stmt()
        # self.standard_format()
        
        


    def preprocessing_bank_stmt(self):
        self.bank_statement_df.drop(index=0, inplace=True)
        self.bank_statement_df.drop(columns='Unnamed: 0', inplace=True)
        
        # Strip column names
        self.bank_statement_df.columns = self.bank_statement_df.columns.str.strip()
        self.bank_statement_df['Date'] = self.bank_statement_df['Tran Date']

        # Replace empty strings and NaN with zero in 'Cr Amt' and 'Dr Amt' columns
        self.bank_statement_df['Cr. Amt'] = self.bank_statement_df['Cr. Amt'].replace('', 0).fillna(0)
        self.bank_statement_df['Dr. Amt'] = self.bank_statement_df['Dr. Amt'].replace('', 0).fillna(0)

        # Remove commas and convert 'Cr Amt' and 'Dr Amt' to numeric
        if self.bank_statement_df['Cr. Amt'].dtype == 'object':
            self.bank_statement_df['Cr. Amt'] = pd.to_numeric(self.bank_statement_df['Cr. Amt'].str.replace(',', ''), errors='coerce')
        if self.bank_statement_df['Dr. Amt'].dtype == 'object':
            self.bank_statement_df['Dr. Amt'] = pd.to_numeric(self.bank_statement_df['Dr. Amt'].str.replace(',', ''), errors='coerce')
        
        display(f'preprocessed_bank_stmt--> {self.bank_statement_df.head()}')
        display(f'columns-->{self.bank_statement_df.columns}')

        # return self.bank_statement_df
        
        

    def extracting_tid_from_bank_stmt(self,bank_statement_df):
        for index, row in bank_statement_df.iterrows():
            if "100000" in str(row["Remarks"]):
                id_matches = re.findall(r'10*[0-9]{7}', str(row["Remarks"]))
                if not id_matches:
                    continue
                id = id_matches[0].replace("100000", "")
                bank_statement_df.loc[index, 'Transaction Id'] = id
            elif row['Tran Particular'] and isinstance(row['Tran Particular'], str):
                transaction_particular = row['Tran Particular']
                match = re.search(r'\b\d{4}\b', transaction_particular)
                if not match:
                    continue
                id = match.group()
                bank_statement_df.loc[index, 'Transaction Id'] = id
        print('total_tid',bank_statement_df['Transaction Id'].count())
        return bank_statement_df

    def standard_format(self,row):
        if row['Dr. Amt'] > 0:
            mode = 'DR'
            amount = row['Dr. Amt']
        elif row['Cr. Amt'] > 0:
            mode = 'CR'
            amount = row['Cr. Amt']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])

    def total_debit_credit_amount_of_bank(self):
        # self.bank_statement_df['Cr. Amt'] = pd.to_numeric(self.bank_statement_df['Cr. Amt'].str.replace(',', ''), errors='coerce')
        self.total_credit = self.bank_statement_df['Cr. Amt'].sum()
        display(f'Total credit bank amount: {self.total_credit}')
        # self.bank_statement_df['Dr. Amt'] = pd.to_numeric(self.bank_statement_df['Dr. Amt'].str.replace(',', ''), errors='coerce')
        self.total_debit = self.bank_statement_df['Dr. Amt'].sum()
        display(f'Total debit bank amount: {self.total_debit}')

    def total_debit_credit_amount_of_soa(self):
        credit = self.soa_statement_df[self.soa_statement_df['Mode'] == 'CR']
        self.credit_amount_soa = credit['Amount'].sum()
        display(f'total soa credit amount {self.credit_amount_soa}')
        debit = self.soa_statement_df[self.soa_statement_df['Mode'] == 'DR']
        self.debit_amount_soa = debit['Amount'].sum()
        display(f'total soa debit amount {self.debit_amount_soa}')

    def preprocessing_soa_stmt(self,soa_statement_df):
        soa_statement_df['Transaction Id'] =  soa_statement_df['Transaction Id'].str.strip("'").dropna()
        display(f'preprocessing_soa_stmt--> {soa_statement_df.head()}')
        return soa_statement_df


    def matching_bank_stmt_with_soa(self, bank_statement_df, soa_statement_df):
        for index1 , bank_statement in bank_statement_df.iterrows():
            if bank_statement['Transaction Id'] in (soa_statement_df['Transaction Id'].values):
                bank_statement_df.loc[index1,'Matched_TID'] = bank_statement['Transaction Id']
                continue
            bank_statement_df.loc[index1,'Unmatched_TID'] = bank_statement['Transaction Id']
        self.unmatched_rows_bank_with_soa = bank_statement_df[bank_statement_df['Unmatched_TID'].notnull()]
        self.matched_rows_bank_with_soa = bank_statement_df[bank_statement_df['Matched_TID'].notnull()]
        display(f"total unmatched TID with soa-->{bank_statement_df['Unmatched_TID'].count()}")  
        display(f"total matched TID-->{bank_statement_df['Matched_TID'].count()}")
        display(f'unmatched data of bank with soa-->{self.unmatched_rows_bank_with_soa}')
        return bank_statement_df

    def matching_soa_stmt_with_bank_stmt(self,bank_statement_df,soa_statement_df):
        for index1, statement_soa in soa_statement_df.iterrows():
            transaction_id = statement_soa['Transaction Id']

            if transaction_id in bank_statement_df['Transaction Id'].values:
                # bank_match.append(bank_statement_soa)
                soa_statement_df.loc[index1,'Matched_tid'] = transaction_id
                continue
                # banknotmatch.append(bank_statement_soa)
            soa_statement_df.loc[index1,'Unmatched_tid'] = transaction_id
        self.matched_row = soa_statement_df[soa_statement_df['Matched_tid'].notnull()]
        self.unmatched_soa_with_bank = soa_statement_df[soa_statement_df['Unmatched_tid'].notnull()]
        display(f"number of soa transaction matched with bank-->{soa_statement_df['Matched_tid'].count()}")
        display(f"number of soa transaction unmatched with bank-->{soa_statement_df['Unmatched_tid'].count()}")
        display(f"Unmatched soa with bank-->{self.unmatched_soa_with_bank.head()}")


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

    def report_of_soa_stmt(self):
        data = {
        'no. of transaction of soa': [self.total_tid_of_credit_of_soa, self.total_tid_of_debit_of_soa],  
        'total amount of transaction of soa': [self.credit_amount_soa, self.debit_amount_soa]     
        }

        # Create a list of your row names
        rows = ['CR', 'DR']

        # Create a DataFrame from the dictionary
        df_soa_report = pd.DataFrame(data, index=rows)
        display(f'soa report of reconcilation -->{df_soa_report}')
        

        
        # Create an ExcelWriter object
        self.excel_writer = pd.ExcelWriter('everest_reconciliation.xlsx', engine='xlsxwriter')

        # Write each DataFrame to a specific sheet in the Excel file
        df_soa_report.to_excel(self.excel_writer, sheet_name='Everest_reconciliation_report')
        self.unmatched_soa_with_bank.to_excel(self.excel_writer, sheet_name='Everest_reconciliation_report', startrow=df_soa_report.shape[0] + 2, index=False)

        

    def report_of_bank_stmt(self):
        data = {
            'no. of transaction of bank': [self.bank_credit_tid, self.bank_debit_tid],   
            'total amount of transaction of bank': [self.total_credit, self.total_debit]     
                }

        # Create a list of your row names
        rows = ['CR', 'DR']

        # Create a DataFrame from the dictionary
        df_bank_report = pd.DataFrame(data, index=rows)
        display(f'bank report of reconcilation -->{df_bank_report}')
      
        # Write each DataFrame to the Excel file with specific start rows and columns
        df_bank_report.to_excel(self.excel_writer, sheet_name='Everest_reconciliation_report', startrow=0, startcol=13)
        self.unmatched_rows_bank_with_soa.to_excel(self.excel_writer, sheet_name='Everest_reconciliation_report', startrow=df_bank_report.shape[0] + 2, startcol=13, index=False)

        self.excel_writer.close()

    