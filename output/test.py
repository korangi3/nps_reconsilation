import os
import datetime
import shutil
# Get the current directory
current_directory = os.getcwd()
print("Current Directory:", current_directory)
print(os.path.abspath(os.pardir))
# Navigate one step back in the directory
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
print("Parent Directory:", parent_directory)

today = str(datetime.datetime.date(datetime.datetime.now()))

new_dir_path = os.path.join(parent_directory, today)
print(new_dir_path)
os.mkdir(new_dir_path)
