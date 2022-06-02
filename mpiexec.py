import configparser
import os

# get configurations from config file
config_file = configparser.ConfigParser()
# read config file
config_file.read("config.ini")
n_proc = int(config_file['Processors']["n_proc"])

prompt = "mpiexec -np n_proc python calculations.py"

os.system('cmd /c prompt')