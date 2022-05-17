import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# READ CONFIG FILE
config_file.read("config.ini")

# ADD NEW SECTION
config_file.add_section("QueueSettings")
# ADD SETTINGS TO FTPSettings SECTION
config_file.set("QueueSettings", "maxQlength", "8")
config_file.set("QueueSettings", "timer", "30")

# SAVE CONFIG FILE
with open(r"config.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'config.ini' created")

# PRINT FILE CONTENT
read_file = open("config.ini", "r")
content = read_file.read()
print("Content of the config file:\n")
print(content)
read_file.flush()
read_file.close()