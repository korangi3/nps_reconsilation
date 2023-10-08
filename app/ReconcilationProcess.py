from qrlib.QRProcess import QRProcess
from qrlib.QRDecorators import run_item
from qrlib.QRRunItem import QRRunItem
from ReconcilationFactoryComponent import ReconcileFactory
from DatabaseComponent import sqlite, SOA_Report, Bank_Report
from qrlib.QRUtils import display
import datetime
import shutil
import os
from EmailComponent import send_email
import time
from Constants import PHASE_1RECONCILIATION_REPORT

class ReconcilationProcess(QRProcess):

    def __init__(self):
        super().__init__()
        self.reconcile_factory = ReconcileFactory()
        self.register(self.reconcile_factory)
        self.data = []
        self.sqlite = sqlite()
        

    @run_item(is_ticket=True, post_success=False)
    def before_run(self, *args, **kwargs):
        self.start_time = datetime.datetime.now()
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        
        

        self.data = ["Reconciling"]
        self.sqlite.create_table()
        self.reconcile_factory.get_excel_writers()
        self.reconcile_factory.getReconcileFactoryObject()
       
        
        

    @run_item(is_ticket=False, post_success=False)
    def before_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

    @run_item(is_ticket=True)
    def execute_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        self.reconcile_factory.run_factory()
        run_item.report_data["test"] = args[0]

    @run_item(is_ticket=False, post_success=False)
    def after_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

    @run_item(is_ticket=False, post_success=False)
    def after_run(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        self.end_time = datetime.datetime.now()
        
        def removing_files():
            bank_dir = os.listdir(f'{os.getcwd()}/output/BANK STMT PHASE 4')
            soa_dir = os.listdir(f'{os.getcwd()}/output/SOA STMT PHASE 4')
            print(bank_dir, soa_dir)
            display(bank_dir)
            display(soa_dir)
            display(len(bank_dir))
            display(len(soa_dir))
            for _ in bank_dir:
                os.remove(f'{os.getcwd()}/output/BANK STMT PHASE 4/{_}')
                
            for _ in soa_dir:
                os.remove(f'{os.getcwd()}/output/SOA STMT PHASE 4/{_}')
                
        def move_files():
            current_directory = os.getcwd()
            parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
            today = str(datetime.datetime.date(datetime.datetime.now()))

            new_dir_path = os.path.join(parent_directory, today)
            try:
                os.mkdir(new_dir_path)
            except:
                pass
            file_to_move1 = PHASE_1RECONCILIATION_REPORT.RECONCILIATION_Matched_REPORT_PATH
            file_to_move2 = PHASE_1RECONCILIATION_REPORT.RECONCILIATION_UnMatched_REPORT_PATH
            shutil.move(file_to_move1, new_dir_path)
            time.sleep(10)
            shutil.move(file_to_move2, new_dir_path)
            time.sleep(10)
            # try:
            #     os.remove(PHASE_1RECONCILIATION_REPORT.RECONCILIATION_Matched_REPORT_PATH)
            #     os.remove(PHASE_1RECONCILIATION_REPORT.RECONCILIATION_UnMatched_REPORT_PATH)
            # except:
            #     pass
           
        try:        
            # removing_files()
            move_files()
        except:
            pass
        
        # try:
        #     send_email()
        # except Exception as e:
        #     display('Could not send email.')
        #     display(e)

    def execute_run(self):
        for x in self.data:
            # self.before_run_item(x)
            self.execute_run_item(x)
            # self.after_run_item(x)
