from datetime import datetime
from Constants import Phase_Constants
from qrlib.QRUtils import display
import os
import html

def get_report_file_path():
    return os.path.join(os.getcwd(), 'output', f'Status-Report-{datetime.today().now().date()}.csv')

def encode_text(text):
    return html.escape(text)

class PassFunc:
    @staticmethod
    def __call__(*args, **kwargs):
        pass

def run_phase(phase_number):
    def decorator(method):
        if isinstance(phase_number,int):
            if not Phase_Constants.CURRENT_PHASE_NUMBER==phase_number:
                display('method skipped')
                return PassFunc()
            display(f'Method in Phase {Phase_Constants.CURRENT_PHASE_NUMBER}.')
            return method
        elif isinstance(phase_number,list):
            if not Phase_Constants.CURRENT_PHASE_NUMBER in phase_number:
                display('method skipped')
                return PassFunc()
            display(f'Method in Phase {Phase_Constants.CURRENT_PHASE_NUMBER}.')
            return method
        else:
            display('method skipped')
            return PassFunc()
    return decorator

def has_run_phase_decorator(method):
    if hasattr(method, '__closure__'):
        for closure in method.__closure__:
            if hasattr(closure.cell_contents, '__name__') and closure.cell_contents.__name__ == 'run_phase':
                return True
    return False
