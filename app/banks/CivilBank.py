from utils.Utils import run_phase
from ReconcileAbstract import Reconcile
from Constants import Banks_FILEPATH, SOA_FILEPATH
from qrlib.QRUtils import display
import pandas as pd
import numpy as np
import datetime

class CivilBank(Reconcile):
    """
    A class for reconciling bank statements with statements of account (SOA). Inherits from the Reconcile class.
    """

    bank_amount_column = 'AMOUNT'
    bank_date_column = 'POST DATE'
    bank_description_column = 'TRANS. REF. NO.'

    def __init__(self, bank_name, excelwriter):
        """
        Initializes the CivilBank instance.

        Args:
            bank_name (str): Name of the bank.
            excelwriter: Excel writer object for generating reports.
        """
        super().__init__(bank_name, excelwriter)
        self.bank_statement_df = pd.read_excel(Banks_FILEPATH.CIVIL_BANK_FILE, skiprows=3)
        self.soa_statement_df = pd.read_csv(SOA_FILEPATH.CIVIL_SOA_FILE, encoding='latin-1')

    def main(self):
        """
        Executes the main reconciliation process by calling individual methods step by step.
        """
        self.preprocessing_bank_stmt()
        self.extracting_tid_from_bank_stmt()
        self.bank_data_standardization()
        self.soa_data_standardization()
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
        """
        Preprocesses the bank statement data by removing invalid rows and cleaning amount values.
        """
        self.bank_statement_df = self.bank_statement_df.loc[
            self.bank_statement_df[self.bank_description_column].notna()
            ]
        self.bank_statement_df[self.bank_amount_column] = self.bank_statement_df[
            self.bank_amount_column
            ].replace(to_replace=["'", ','], value='', regex=True)
        
        if self.bank_statement_df[self.bank_amount_column].dtype == 'object':
            self.bank_statement_df[self.bank_amount_column] = pd.to_numeric(
                self.bank_statement_df[self.bank_amount_column]
                )

    @run_phase(phase_number=1)
    def extracting_tid_from_bank_stmt(self):
        """
        Extracts transaction IDs from bank statement data.
        """
        self.bank_statement_df['Transaction Id'] = np.nan
        self.bank_statement_df['Transaction Id'] = self.bank_statement_df['Transaction Id'].astype(str)
        display(f'total_tid {self.bank_statement_df["Transaction Id"].count()}')

    @run_phase(phase_number=1)
    def bank_data_standardization(self):
        """
        Standardizes bank statement data by converting dates, renaming columns, and determining transaction mode.
        """
        self.bank_statement_df['Date'] = pd.to_datetime(self.bank_statement_df['POST DATE']).dt.date
        self.bank_statement_df.rename(columns={self.bank_amount_column: 'Amount'}, inplace=True)
        self.bank_statement_df['Mode'] = self.bank_statement_df['Amount'].apply(
            lambda amount: 'DR' if amount < 0 else 'CR'
            )

    @run_phase(phase_number=1)
    def soa_data_standardization(self):
        """
        Standardizes SOA data by converting dates using the convert_soa_date_format method.
        """
        self.soa_statement_df['Date'] = self.soa_statement_df['Date'].apply(self.convert_soa_date_format)

    @staticmethod
    @run_phase(phase_number=1)
    def convert_soa_date_format(date_str):
        """
        Converts a date string from one format to another.

        Args:
            date_str (str): Date string to be converted.

        Returns:
            str: Converted date string.
        """
        if not isinstance(date_str, str):
            date_str = str(date_str)
        try:
            date_str = date_str.split()[0]
            parsed_date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
            return parsed_date.strftime('%d/%m/%Y')
        except Exception as e:
            return np.nan
