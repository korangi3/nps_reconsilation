import os
import datetime

current_directory = os.getcwd()

parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
today = str(datetime.datetime.date(datetime.datetime.now()))
fll_path = os.path.join(parent_directory, today)
print(fll_path)
# import shutil

# current_directory = os.getcwd()
# parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
# today = str(datetime.datetime.date(datetime.datetime.now()))

# new_dir_path = os.path.join(parent_directory, today)
# print(new_dir_path)
# try:
#     os.rmdir(f'{new_dir_path}')
#     print('here')
#     os.mkdir(new_dir_path)
# except:
#     os.mkdir(new_dir_path)
# import time

# time.sleep(10)
# print(f'{os.getcwd()}\\chromedriver.exe')
# os.rmdir(new_dir_path)

# def move_files():
#     current_directory = os.getcwd()
#     parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
#     today = str(datetime.datetime.date(datetime.datetime.now()))

#     new_dir_path = os.path.join(parent_directory, today)
#     try:
#         os.mkdir(new_dir_path)
#     except:
#         pass

#     file_to_move1 = f'{os.getcwd()}\\output\\Reconciliation_Matched_report.xlsx'
#     file_to_move2 = f'{os.getcwd()}\\output\\Reconciliation_Unmatched_report.xlsx'
#     shutil.move(file_to_move1, new_dir_path)
#     shutil.move(file_to_move2, new_dir_path)
# move_files()    
