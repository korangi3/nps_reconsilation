import gevent
import requests
import csv
import os, pandas as pd
from qrlib.QREnv import QREnv
from utils.sources import sources
from robot.libraries.BuiltIn import BuiltIn
from qrlib.QRComponent import QRComponent
from qrlib.QRUtils import display
from app.utils import Utils
from gevent.pool import Pool
import gevent
from queue import Queue
from Constants import PHASE_1RECONCILIATION_REPORT
from gevent import monkey
monkey.patch_all()


class ReconcileFactory(QRComponent):
    threads = 4

    def __init__(self):
        self.factory_instances_functions = []
        self.excel_writers = None

    def get_excel_writers(self):
        unmatched_output_file_path = PHASE_1RECONCILIATION_REPORT.RECONCILIATION_UnMatched_REPORT_PATH
        matched_output_file_path = PHASE_1RECONCILIATION_REPORT.RECONCILIATION_Matched_REPORT_PATH
        matchedexcel_writer = pd.ExcelWriter(matched_output_file_path, engine='xlsxwriter')
        unmatchedexcel_writer = pd.ExcelWriter(unmatched_output_file_path, engine='xlsxwriter')
        self.excel_writers = [unmatchedexcel_writer, matchedexcel_writer]

    def getReconcileFactoryObject(self):
        for source in sources:
            if (source['instance'] is None) or (source['name'] is None):
                continue
            
            mapped_source = {
                "name":source['name'],
                "instance":source['instance']
            }
            factory_instance = mapped_source.get("instance")
            self.factory_instances_functions.append(factory_instance(source['name'], self.excel_writers).main)
        
    def run_factory(self):
        pool = Pool(self.threads)
        [pool.spawn(factory_instance_function) for factory_instance_function in self.factory_instances_functions]
        pool.join()
        self.excel_writers[0].close()
        self.excel_writers[1].close()
