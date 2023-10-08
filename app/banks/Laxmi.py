from ReconcileAbstract import Reconcile
from qrlib.QRUtils import display
from Constants import Banks_FILEPATH
from Constants import SOA_FILEPATH
# from Constants import PHASE1_LWT_FILEPATH, PHASE1_FT_FILEPATH
from xlsxwriter import Workbook
from utils.Utils import run_phase
import pandas as pd
import numpy as np
import re

class LaxmiBank(Reconcile):    
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
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.LAXMI_BANK_FILE,)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.Laxmi_SOA_FILE, encoding='latin-1')
        # self.lwt_merchant_df = pd.read_excel(PHASE1_LWT_FILEPATH.LWT_FILE,)
        # self.ft_merchant_df = pd.read_csv(PHASE1_FT_FILEPATH.LAXMI_FT_FILE, encoding='latin-1')

    @run_phase(phase_number=4)
    def get_phase4_df(self):
        try:
            self.bank_statement_df = pd.read_excel(Banks_FILEPATH.LAXMI_BANK_FILE, skiprows= 1)
            self.soa_statement_df = pd.read_csv(SOA_FILEPATH.Laxmi_SOA_FILE, encoding='latin-1')
        except:
            self.proceed = False

    def main(self):
        if self.proceed:
            self.preprocessing_bank_stmt()
            self.preprocessing_bank_stmt_phase_4()
            self.preprocessing_soa_stmt()
            self.preprocessing_ft_stmt()
            self.updated_standardize_bank_stmt()
            self.updated_standardize_bank_stmt_phase_4()
            self.extracting_tid_from_bank_stmt()
            self.extracting_tid_from_bank_stmt_phase_4()
            self.matching_bank_stmt_with_soa_report()
            self.matching_soa_report_with_bank_stmt()
            self.update_soa_report_with_merchant_id()
            self.matching_soa_report_with_bank_stmt_with_merchant_id()
            self.matching_bank_stmt_with_soa_report_with_merchant_id()
            self.total_debit_credit_amount_of_soa()
            self.total_debit_credit_amount_of_bank()
            self.debit_credit_amount_matches_tid_of_bank_with_soa()
            self.debit_credit_amount_of_soa_matched_with_bank()
            self.extract_number_of_tid_CR_and_DR_from_soa()
            self.extract_number_of_tid_CR_and_DR_from_bank_stmt()
            # self.write_soa_data()
            # self.write_bank_data()
            self.generate_report()
        else:
            display('No data for laxmi')

    @run_phase(phase_number=1)
    def preprocessing_ft_stmt(self):
        self.ft_merchant_df['Merchant Transaction Id'] = self.ft_merchant_df['Merchant Transaction Id'].str.strip("'").dropna()

    @run_phase(phase_number=1)
    def preprocessing_bank_stmt(self):
        '''
        This method cleans and formats the bank statement DataFrame and convert the date column to standard format to match with soa.
        '''
        self.bank_statement_df = self.bank_statement_df[~self.bank_statement_df['TRAN_PARTICULAR'].str.contains('TRTR')]
        self.bank_statement_df = self.bank_statement_df[~self.bank_statement_df['TRAN_PARTICULAR'].str.contains('TRRR')]
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['TRAN_DATE'],format='%Y-%m-%d')

    @run_phase(phase_number=1)
    def updated_standardize_bank_stmt(self):
        self.bank_statement_df[['Mode', 'Amount']] = self.bank_statement_df.apply(self.standard_format, axis=1)    

    @run_phase(phase_number=1)
    def update_soa_report_with_merchant_id(self):
        '''
        This method updates the SOA report with merchant IDs from LWT(Load Wallet Transaction) and FT(FundTransfer) data.
        '''
        display(f'columns of merchants are: {self.lwt_merchant_df.columns}')
        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']
            if wallet_item['Transaction Type'] == 'LoadWallet':
                lwt_merchant_tid_row = self.lwt_merchant_df[self.lwt_merchant_df['LoadWalletTransactionId'] == wallet_tid]
                if lwt_merchant_tid_row.empty:
                    continue
                lwt_merchant_tid = lwt_merchant_tid_row.iloc[0]['MerchantTransactionId']
                self.soa_statement_df.at[wallet_index, 'Transaction Id'] = lwt_merchant_tid
                
            elif wallet_item['Transaction Type'] == 'FundTransfer':
                ft_merchant_tid_row = self.ft_merchant_df[self.ft_merchant_df['Transaction Detail Id'] == wallet_tid]
                if ft_merchant_tid_row.empty:
                    continue
                ft_merchant_tid = ft_merchant_tid_row.iloc[0]['Merchant Transaction Id']
                self.soa_statement_df.at[wallet_index, 'Transaction Id'] = ft_merchant_tid
            
    @run_phase(phase_number=1)
    def matching_soa_report_with_bank_stmt_with_merchant_id(self):
        '''
        This method matches transactions in SOA report with bank statement transactions using merchant IDs.
        '''
        lwt_bank_df = self.bank_statement_df[self.bank_statement_df['TRAN_PARTICULAR'].str.contains('IMEPAY') & ~self.bank_statement_df['TRAN_PARTICULAR'].str.contains('TRFO|TRFB')]['TRAN_PARTICULAR']
        ft_bank_df = self.bank_statement_df[self.bank_statement_df['TRAN_PARTICULAR'].str.contains('IMEPAY') & self.bank_statement_df['TRAN_PARTICULAR'].str.contains('TRFO|TRFB')]['TRAN_PARTICULAR']

        for wallet_index, wallet_item in self.soa_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']

            if self.soa_statement_df.at[wallet_index, 'Matched']:
                continue

            matching_bank = self.bank_statement_df[
                    (self.bank_statement_df['Transaction Id'] == wallet_tid)
                ]
            
            if not matching_bank.empty:
                self.soa_statement_df.at[wallet_index, 'Matched'] = True

        match_count = (self.soa_statement_df['Matched'] == True).sum()
        unmatch_count = (self.soa_statement_df['Matched'] == False).sum()
        display(f'Matched final count soa_statement after getting merchant id ==== {match_count}')
        display(f'Unmatched final count soa_statement after getting merchant id ==== {unmatch_count}') 

    @run_phase(phase_number=1)
    def matching_bank_stmt_with_soa_report_with_merchant_id(self):
        '''
        This method matches bank statement transactions with SOA report transactions using merchant IDs.
        '''
        lwt_soa_df = self.soa_statement_df[self.soa_statement_df['Transaction Type'].str.contains('LoadWallet', na=False)]['Transaction Id']
        ft_soa_df = self.soa_statement_df[self.soa_statement_df['Transaction Type'].str.contains('FundTransfer', na=False)]['Transaction Id']

        for wallet_index, wallet_item in self.bank_statement_df.iterrows():
            wallet_tid = wallet_item['Transaction Id']
            if str(wallet_tid)=='nan':
                continue
            if self.bank_statement_df.at[wallet_index, 'Matched']:
                continue

            matching_bank_lw = self.soa_statement_df[
                    (self.soa_statement_df['Transaction Type'] == 'LoadWallet') &
                    (self.soa_statement_df['Transaction Id'] == wallet_tid)
                ]
            matching_bank_ft = self.soa_statement_df[
                    (self.soa_statement_df['Transaction Type'] == 'FundTransfer') &
                    (self.soa_statement_df['Transaction Id'] == wallet_tid)
                ]

            if not (matching_bank_lw.empty and matching_bank_ft.empty):
                self.bank_statement_df.at[wallet_index, 'Matched'] = True

        match_count = (self.bank_statement_df['Matched'] == True).sum()
        unmatch_count = (self.bank_statement_df['Matched'] == False).sum()
        display(f'Matched final count bank_statement after getting merchant id  ==== {match_count}')
        display(f'Unmatched final count bank_statement after getting merchant id ==== {unmatch_count}')

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        '''
        This method extracts transaction IDs from various patterns in bank statement column like 'TRAN PARTICULAR'.
        '''
        for index, row in self.bank_statement_df.iterrows():
            row_particular = row['TRAN_PARTICULAR']
            if row_particular == np.nan or row_particular=='nan' or row_particular==None:
                continue
            # if "WT" in str(row['Desc2']):
            #     id = str(row['Desc2']).replace('/WT','')
            #     id = id.split()
            #     id =  id[0].replace("10000000", "")
            #     self.bank_statement_df.at[index, 'Transaction Id'] = id
            if ('connectIPS' in row_particular):
                tid = row_particular.split('/')[-1]
                self.bank_statement_df.loc[index,'Transaction Id'] = tid
            elif ',' in row_particular:
                value = row_particular.split(',')[-1]
                id = re.sub(r'10*', '', value, count=1)
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                
            elif 'IMEPAY' in str(row_particular) and not('TRFO' in str(row_particular) or 'TRFB' in str(row_particular)):
                id_text_list = row_particular.split('-')
                for id in id_text_list:
                    if not re.match(r'^202', id):
                        continue
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
                    # display(f'merchant transaction id in the index  {index} is === {id}')

            elif 'IMEPAY' in str(row_particular) and (('TRFO' in str(row_particular)) or ('TRFB' in str(row_particular))):
                id_text_list = row_particular.split('-')
                for id in id_text_list:
                    if not re.match(r'^202', id):
                        continue
                    self.bank_statement_df.loc[index, 'Transaction Id'] = id
                    # display(f'merchant transaction id in the index  {index} is === {id}')
            else:
                continue
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=1)
    def standard_format(self,row):
        '''
          Determine transaction mode and amount from bank statement data.

        Parameters:
            row (Series): A row of bank statement data.

        Returns:
            Series: Mode (CR/DR) and amount.
        '''
        if row['DR'] > 0:
            mode = 'DR'
            amount = row['DR']
        elif row['CR'] > 0:
            mode = 'CR'
            amount = row['CR']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
    
    @run_phase(phase_number=4)
    def preprocessing_bank_stmt_phase_4(self):
        """
        Drop unnecessary rows and standardize column names.
        """
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['Date'], format="%Y-%m-%dT%H:%M:%S").dt.date
        self.bank_statement_df = self.bank_statement_df[self.bank_statement_df['Ac.Number']=='14242431110001']

    run_phase(phase_number=4)
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
            display(row['Desc1'], row['Desc2'])
            if "NPS-IF-" in str(row['Desc1']):
                id = row['Desc1']
                # id = id[0]
                
                index_10000 = id.index('NPS-IF-')
                id = id[index_10000:index_10000+14]
                id =  id.replace("NPS-IF-", "")
                
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
                # id = re.findall(r'[0-9]{7}', str(row['Desc2']))
                # if not id:
                #     continue
                # self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                # continue
            elif "WT10000" in str(row['Desc1']):
                str_wt = str(row['Desc1']).split('/')[0]
                id = str_wt[-5:]
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
            
            elif "FTMS-" in str(row['Desc1']):
                id = row['Desc1']
                # id = id[0]
                
                index_10000 = id.index('FTMS-')
                id = id[index_10000:index_10000+11]
                id =  id.replace("FTMS-", "")
                
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
                # id = re.findall(r'[0-9]{6}', str(row['Desc2']))
                # if not id:
                #     continue
                # self.bank_statement_df.loc[index, 'Transaction Id'] = id[0]
                # continue
            elif "10000" in str(row['Desc2']):
                id = row['Desc1']
                # id = id[0]
                
                index_10000 = id.index('10000')
                id = id[index_10000:index_10000+12]
                id =  id.replace("10000", "")
                
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                continue
                # id = re.findall(r'10*[0-9]{7}', str(row['Desc2']))
                # if not id:
                #     continue
                # id =  id[0].replace("10000", "")
                # self.bank_statement_df.loc[index, 'Transaction Id'] = id
            elif "10000" in str(row['Desc1']):
                id = row['Desc1']
                # id = id[0]
                
                index_10000 = id.index('10000')
                id = id[index_10000:index_10000+12]
                id =  id.replace("10000", "")
                
                self.bank_statement_df.loc[index, 'Transaction Id'] = id
                
                # id = re.findall(r'10*[0-9]{7}', str(row['Desc1']))
                # if not id:
                #     continue
                # id =  id[0].replace("10000", "")
                # self.bank_statement_df.loc[index, 'Transaction Id'] = id
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
            amount = row['Amount']
        elif row['Txn Type'] == 'C':
            mode = 'CR'
            amount = row['Amount']
        else:
            mode = None
            amount = None
        return pd.Series([mode, amount], index=['Mode', 'Amount'])
