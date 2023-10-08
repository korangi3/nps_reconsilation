from qrlib.QRBot import QRBot
from ReconcilationProcess import ReconcilationProcess
from ScrapingComponent import Scraping_process
import os


def removing_files():
    bank_dir = os.listdir(f'{os.getcwd()}/output/BANK STMT PHASE 4')
    soa_dir = os.listdir(f'{os.getcwd()}/output/SOA STMT PHASE 4')
    print(bank_dir, soa_dir)
    for _ in bank_dir:
        os.remove(f'{os.getcwd()}/output/BANK STMT PHASE 4/{_}')
        
    for _ in soa_dir:
        os.remove(f'{os.getcwd()}/output/SOA STMT PHASE 4/{_}')

class Bot(QRBot):

    def __init__(self):
        super().__init__()
        
        # try:
        #     removing_files()
        # except:
        #     pass
        self.scrap = Scraping_process()
        

        self.process = ReconcilationProcess()
        

    def start(self):
        self.setup_platform_components()
        

        self.scrap.open_website()
        self.scrap.sign_in()
        # self.scrap.soa_stmt_scraping()
        self.scrap.bank_statement_scraping()
        self.scrap.open_website_of_NIBL()
        self.scrap.sign_in_NIBL()
        self.scrap.NIBL_bank_statement_scraping()
        self.scrap.open_website_of_RBB()
        self.scrap.sign_in_RBB()
        self.scrap.RBB_bank_statement_scraping()
        
        # try:
        #     self.scrap.open_website_of_OUTLOOK_EMAIL()
        #     self.scrap.sign_in_to_Outlook_Email()
        #     self.scrap.bank_statement_scraping_through_email()
        # except:
        #     pass
            
        self.process.before_run()
        self.process.execute_run()

    def teardown(self):
        self.process.after_run()
