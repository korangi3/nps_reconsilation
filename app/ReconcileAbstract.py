from qrlib.QRComponent import QRComponent
from RPA.Browser.Selenium import Selenium
from abc import abstractmethod, ABC
from DatabaseComponent import SOA_Report, Bank_Report
# from Constants import PHASE1_LWT_FILEPATH
from qrlib.QRUtils import display
from utils.Utils import run_phase
import datetime
import pandas as pd
import numpy as np

class Reconcile(QRComponent, ABC):
    matched_soa_with_bank:pd.DataFrame = None
    unmatched_soa_with_bank:pd.DataFrame = None
    matched_bank_with_soa:pd.DataFrame = None
    unmatched_bank_with_soa:pd.DataFrame = None

    bank_statement_df:pd.DataFrame = None
    soa_statement_df:pd.DataFrame = None
    # soa_merchant_df = pd.read_excel(PHASE1_LWT_FILEPATH.LWT_FILE)

    def __init__(self, bank_name, excel_writers):
        QRComponent.__init__(self)
        self.site_url = 'https://adminonepg.nepalpayment.com/'
        self.selenium:Selenium = Selenium()
        self.soa_report_db = SOA_Report()
        self.bank_report_db = Bank_Report()
        self.bank_name = bank_name
        self.excel_writers = excel_writers
        

    @abstractmethod
    def main(self):
        pass

    def signin(self):
        pass


    @run_phase(phase_number=[1,4])
    def preprocessing_soa_stmt(self):
        self.soa_statement_df['Transaction Id'] =  self.soa_statement_df['Transaction Id'].str.strip("'").dropna()
        self.soa_statement_df['Date'] = pd.to_datetime(self.soa_statement_df['Date']).dt.date
        self.soa_statement_df['Amount'].astype('float')
        self.bank_statement_df['Matched_TID'] = np.nan
        self.bank_statement_df['Matched_AD'] = np.nan
        self.bank_statement_df['Matched'] = np.nan
        self.soa_statement_df['Matched_TID'] = np.nan
        self.soa_statement_df['Matched_AD'] = np.nan
        self.soa_statement_df['Matched'] = np.nan

        duplicate_rows = self.soa_statement_df[self.soa_statement_df.duplicated(subset='Transaction Id', keep=False)]
        summed_value = duplicate_rows.groupby('Transaction Id')['Amount'].sum()

        for dict_keys in summed_value.to_dict().keys():
            amount = summed_value[dict_keys]
            self.soa_statement_df.loc[(self.soa_statement_df['Transaction Id'] == dict_keys) & (self.soa_statement_df['Transaction Type'] == 'BankVoucherEntry'), 'Amount'] = amount

        self.soa_statement_df = self.soa_statement_df.loc[self.soa_statement_df['Transaction Type'] != 'NchlVoucherEntry']

    @run_phase(phase_number=[1,4])
    def update_soa_report_with_merchant_id_of_load_wallet(self):
        display(f'columns of merchants are: {self.soa_merchant_df.columns}')

        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            if not wallet_item['Transaction Type'] == 'LoadWallet':
                continue
            wallet_tid = wallet_item['Transaction Id']
            merchant_tid_row = self.soa_merchant_df[self.soa_merchant_df['LoadWalletTransactionId'] == wallet_tid]

            if merchant_tid_row.empty:
                continue
            merchant_tid = merchant_tid_row.iloc[0]['MerchantTransactionId']
            self.soa_statement_df.at[wallet_index, 'Transaction Id'] = merchant_tid

    @run_phase(phase_number=[1,4])
    def matching_soa_report_with_bank_stmt(self):
        unmatch_count = 0
        match_count = 0
        display(f'soa statement date--->{self.soa_statement_df["Date"]}')

        for _, soa_statement in self.soa_statement_df.iterrows():
            tid = soa_statement['Transaction Id']
            # soa_date = soa_statement['Date']
            # soa_amount = soa_statement['Amount']

            if tid in self.bank_statement_df['Transaction Id'].values:
                self.soa_statement_df.loc[soa_statement.name, 'Matched_TID'] = True
                match_count += 1
            else:
                # match_found = False
                # matching_soa = self.bank_statement_df[
                #                                         (self.bank_statement_df['Date'] == soa_date) & 
                #                                         ((self.bank_statement_df['Amount'] == soa_amount))
                #                                     ]
                # if not matching_soa.empty:
                #     self.soa_statement_df.loc[soa_statement.name, 'Matched_AD'] = True
                #     match_count += 1
                #     match_found = True
                # if not match_found:
                #     self.soa_statement_df.loc[soa_statement.name, 'Matched_AD'] = False
                self.soa_statement_df.loc[soa_statement.name, 'Matched_TID'] = False
                unmatch_count += 1

        display(f'Matched initial count soa_statement {self.bank_name} ==== {match_count}')
        display(f'Unmatched initial count soa_statement {self.bank_name} ==== {unmatch_count}')
        self.merge_soa_matched_column()
        
    
    @run_phase(phase_number=[1,4])
    def merge_soa_matched_column(self):
        self.soa_statement_df['Matched'] = self.soa_statement_df[['Matched_TID', 'Matched_AD']].any(axis=1)
        # self.soa_statement_df['Matched'] = self.soa_statement_df.apply(
        #     lambda row: self.check_match(row, self.soa_statement_df, self.bank_statement_df)
        #             if not (row['Matched'] and row['Transaction Id']) else True,
        #     axis=1
        # )

        # # if the transaction is matched with amount and date and the same amount transaction was completed in same day then it is consided as not matched
        # # matched_ad_true_rows = self.soa_statement_df[self.soa_statement_df['Matched_AD'] == True]
        # # duplicate_rows = matched_ad_true_rows[matched_ad_true_rows.duplicated(subset=['Date', 'Amount'], keep=False)]
        # # self.soa_statement_df.loc[duplicate_rows.index, 'Matched'] = False

        # # To calculate total match and unmatch after applying the unmatched case after matching using amount and date
        match_count = (self.soa_statement_df['Matched'] == True).sum()
        unmatch_count = (self.soa_statement_df['Matched'] == False).sum()
        display(f'Matched final count soa_statement {self.bank_name}  ==== {match_count}')
        display(f'Unmatched final count soa_statement {self.bank_name}  ==== {unmatch_count}')

    @run_phase(phase_number=[1,4])
    def matching_bank_stmt_with_soa_report(self):
        unmatch_count = 0
        match_count = 0

        for _, bank_statement in self.bank_statement_df.iterrows():
            tid = bank_statement['Transaction Id']
            bank_date = bank_statement['Date']
            bank_amount = bank_statement['Amount']

            # if tid=='nan':
            #     match_found = False
            #     matching_bank = self.soa_statement_df[
            #         (bank_date == self.soa_statement_df['Date']) &
            #         ((bank_amount == self.soa_statement_df['Amount']))
            #     ]

            #     if not matching_bank.empty:
            #         self.bank_statement_df.loc[bank_statement.name, 'Matched_AD'] = True
            #         match_count += 1
            #         match_found = True

            #     if not match_found:
            #         self.bank_statement_df.loc[bank_statement.name, 'Matched_AD'] = False
            #         unmatch_count += 1

            if tid in self.soa_statement_df['Transaction Id'].values:
                self.bank_statement_df.loc[bank_statement.name, 'Matched_TID'] = True
                match_count += 1
            else:
                self.bank_statement_df.loc[bank_statement.name, 'Matched_TID'] = False
                unmatch_count += 1

        display(f'Matched initial count bank_statement{self.bank_name}  ==== {match_count}')
        display(f'Unmatched initial count bank_statement {self.bank_name}  ==== {unmatch_count}')
        self.merge_bank_matched_column()
          

    @run_phase(phase_number=[1,4])
    def merge_bank_matched_column(self):
        self.bank_statement_df['Matched'] = self.bank_statement_df[['Matched_TID', 'Matched_AD']].any(axis=1)
        # self.bank_statement_df['Matched'] = self.bank_statement_df.apply(
        #     lambda row: self.check_match(row, self.bank_statement_df, self.soa_statement_df)
        #                         if not (row['Matched'] and row['Transaction Id']) else True,
        #     axis=1
        # )

        # # matched_ad_true_rows = self.bank_statement_df[self.bank_statement_df['Matched_AD'] == True]
        # # duplicate_rows = matched_ad_true_rows[matched_ad_true_rows.duplicated(subset=['Date', 'Amount'], keep=False)]
        # # self.bank_statement_df.loc[duplicate_rows.index, 'Matched'] = False

        match_count = (self.bank_statement_df['Matched'] == True).sum()
        unmatch_count = (self.bank_statement_df['Matched'] == False).sum()
        display(f'Matched final count bank_statement {self.bank_name}  ==== {match_count}')
        display(f'Unmatched final count bank_statement {self.bank_name}  ==== {unmatch_count}')

    @staticmethod
    @run_phase(phase_number=[1,4])
    def check_match(row, current_df, other_df:pd.DataFrame):
        current_matches = current_df[current_df['Matched_TID'] == False]
        different_matches = other_df[other_df['Matched_TID'] == False]

        current_matches = current_matches[
            (current_matches['Date'] == row['Date']) & 
            (current_matches['Amount'] == row['Amount'])
        ]
        
        different_matches = different_matches[
            (different_matches['Date'] == row['Date']) & 
            (different_matches['Amount'] == row['Amount'])
        ]
        return current_matches.shape[0] == different_matches.shape[0]

    @run_phase(phase_number=[1,4])
    def total_debit_credit_amount_of_bank(self):
        credit = self.bank_statement_df[self.bank_statement_df['Mode'] == 'CR']
        self.total_credit_bank = credit['Amount'].sum()
        display(f'total bank credit amount {self.total_credit_bank}')
        debit = self.bank_statement_df[self.bank_statement_df['Mode'] == 'DR']
        self.total_debit_bank = debit['Amount'].sum()
        display(f'total bank debit amount {self.total_debit_bank}')

    @run_phase(phase_number=[1,4])
    def total_debit_credit_amount_of_soa(self):
        credit = self.soa_statement_df[self.soa_statement_df['Mode'] == 'CR']
        self.credit_amount_soa = credit['Amount'].sum()
        display(f'total soa credit amount {self.credit_amount_soa}')
        debit = self.soa_statement_df[self.soa_statement_df['Mode'] == 'DR']
        self.debit_amount_soa = debit['Amount'].sum()
        display(f'total soa debit amount {self.debit_amount_soa}')

    @run_phase(phase_number=[1,4])
    def extract_number_of_tid_CR_and_DR_from_soa(self):
        soa_stmt_of_dr = self.soa_statement_df[self.soa_statement_df['Mode']== 'DR']
        self.total_tid_of_debit_of_soa = soa_stmt_of_dr['Amount'].count()
        soa_stmt_of_cr = self.soa_statement_df[self.soa_statement_df['Mode']== 'CR']
        self.total_tid_of_credit_of_soa =soa_stmt_of_cr['Amount'].count()

    @run_phase(phase_number=[1,4])
    def extract_number_of_tid_CR_and_DR_from_bank_stmt(self):
        bank_stmt_of_dr = self.bank_statement_df[self.bank_statement_df['Mode']== 'DR']
        self.bank_debit_tid = bank_stmt_of_dr['Amount'].count()
        display(f'bank debit transaction id-->{self.bank_debit_tid}')
        bank_stmt_of_cr = self.bank_statement_df[self.bank_statement_df['Mode']== 'CR']
        self.bank_credit_tid =bank_stmt_of_cr['Amount'].count()
        display(f'bank credit transaction id-->{self.bank_credit_tid}')   

    @run_phase(phase_number=[1,4])
    def debit_credit_amount_matches_tid_of_bank_with_soa(self):
        self.get_umatched_report()
        credit = self.matched_bank_with_soa[self.matched_bank_with_soa['Mode'] == 'CR']
        total_credit_amount_matches_of_tid_with_bank = credit['Amount'].sum()
        display(f'Total credit that matches tid of bank with soa: {total_credit_amount_matches_of_tid_with_bank}')
        debit = self.matched_bank_with_soa[self.matched_bank_with_soa['Mode'] == 'DR']
        total_debit_amount_matches_of_tid_with_bank_to_soa = debit['Amount'].sum()
        display(f'Total debit that matches tid of bank with soa: {total_debit_amount_matches_of_tid_with_bank_to_soa}')

    @run_phase(phase_number=[1,4])
    def debit_credit_amount_of_soa_matched_with_bank(self):
        credit = self.matched_soa_with_bank[self.matched_soa_with_bank['Mode'] == 'CR']
        credit_amount_soa_matched_with_bank = credit['Amount'].sum()
        display(f'credit amout of soa matched with bank {credit_amount_soa_matched_with_bank}')
        debit = self.matched_soa_with_bank[self.matched_soa_with_bank['Mode'] == 'DR']
        debit_amount_soa_matched_with_bank = debit['Amount'].sum()
        display(f'debit amount of soa matched with bank {debit_amount_soa_matched_with_bank}')     

    @run_phase(phase_number=[1,4])
    def write_soa_data(self):
        created_at = datetime.date.today()
        updated_at = created_at
        for soa_index, soa_statement in self.soa_statement_df.iterrows():
            transaction_id = soa_statement['Transaction Id']
            transaction_type = soa_statement['Transaction Type']
            transaction_mode = soa_statement['Mode']
            transaction_amount = soa_statement['Amount']
            transaction_date = soa_statement['Date']
            if soa_statement['Matched'] == True:
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

    @run_phase(phase_number=[1,4])
    def write_bank_data(self):
        created_at = datetime.date.today()
        updated_at = created_at

        for bank_index, bank_statement in self.bank_statement_df.iterrows():
            transaction_id = bank_statement['Transaction Id']
            # transaction_type = bank_statement['Transaction Type']

            transaction_mode = bank_statement['Mode']
            transaction_amount = bank_statement['Amount']
            transaction_date = bank_statement['Date']
            if bank_statement['Matched']==True:
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

    @run_phase(phase_number=[1,2,3,4])
    def get_umatched_report(self):
        self.matched_soa_with_bank = self.soa_statement_df[self.soa_statement_df['Matched']==True]
        self.unmatched_soa_with_bank = self.soa_statement_df[self.soa_statement_df['Matched']==False]  

        self.matched_bank_with_soa = self.bank_statement_df[self.bank_statement_df['Matched']==True]
        self.unmatched_bank_with_soa = self.bank_statement_df[self.bank_statement_df['Matched']==False] 

    @run_phase(phase_number=[1,4])
    def generate_report(self):
        soa_data = {
            'no. of transaction of soa': [self.total_tid_of_credit_of_soa, self.total_tid_of_debit_of_soa],  
            'total amount of transaction of soa': [self.credit_amount_soa, self.debit_amount_soa]     
        }
        bank_data = {
            'no. of transaction of bank': [self.bank_credit_tid, self.bank_debit_tid],   
            'total amount of transaction of bank': [self.total_credit_bank, self.total_debit_bank]     
        }
        self.get_umatched_report()
        rows = ['CR', 'DR']
        df_soa_report = pd.DataFrame(soa_data, index=rows)
        df_bank_report = pd.DataFrame(bank_data, index=rows)
        
        self.unmatched_bank_with_soa.drop(columns=['Matched_TID', 'Matched_AD'], inplace=True)
        self.unmatched_soa_with_bank.drop(columns=['Matched_TID', 'Matched_AD'], inplace=True)
        self.matched_bank_with_soa.drop(columns=['Matched_TID', 'Matched_AD'], inplace=True)
        self.matched_soa_with_bank.drop(columns=['Matched_TID', 'Matched_AD'], inplace=True)

        bank_col_len = len(self.unmatched_soa_with_bank.columns)

        df_soa_report.to_excel(self.excel_writers[0], sheet_name=f'{self.bank_name}_report')
        df_bank_report.to_excel(self.excel_writers[0], sheet_name=f'{self.bank_name}_report', startrow=0, startcol=bank_col_len+2)
        self.unmatched_bank_with_soa.to_excel(self.excel_writers[0], sheet_name=f'{self.bank_name}_report', startrow=df_bank_report.shape[0] + 2, startcol=bank_col_len+2, index=False)
        self.unmatched_soa_with_bank.to_excel(self.excel_writers[0], sheet_name=f'{self.bank_name}_report', startrow=df_soa_report.shape[0] + 2, index=False)

        df_soa_report.to_excel(self.excel_writers[1], sheet_name=f'{self.bank_name}_report')
        df_bank_report.to_excel(self.excel_writers[1], sheet_name=f'{self.bank_name}_report', startrow=0, startcol=bank_col_len+2)
        self.matched_bank_with_soa.to_excel(self.excel_writers[1], sheet_name=f'{self.bank_name}_report', startrow=df_bank_report.shape[0] + 2, startcol=bank_col_len+2, index=False)
        self.matched_soa_with_bank.to_excel(self.excel_writers[1], sheet_name=f'{self.bank_name}_report', startrow=df_soa_report.shape[0] + 2, index=False)


    def generate_commision_report(self):
        # Change name to get from filename and check if Sheet name is always Sheet1
        df = pd.read_excel('jestha.xlsx', sheet_name='Sheet1')
        p_df = df.pivot_table(index='Merchant', columns='Type', values='Charge', aggfunc='sum', margins=True, margins_name='Grand Total')
        p_df.to_excel('random.xlsx', 'jestha') # Change name according to the year

        # Change name to get from filename and check if Sheet name is always Sheet1
        # df1 = pd.read_excel('jestha.xlsx', sheet_name='Sheet1')
        # df1 = df
        v_df = df.pivot_table(index='Type', values=['Charge', 'Ac Fee', 'Iss Fee', 'Comm', 'Nt Fee'], aggfunc='sum')
        grand_total = v_df.agg(['sum'])
        grand_total.index = ['Grand Total']
        v_df = v_df.append(grand_total)
        with pd.ExcelWriter('random.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            v_df.to_excel(writer, sheet_name='jestha', startrow=p_df.shape[0]+2)