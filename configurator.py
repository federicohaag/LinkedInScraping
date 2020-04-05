import os
from configparser import ConfigParser
from sys import platform

config = ConfigParser()

config.add_section('system')
config.add_section('linkedin')
config.add_section('profiles_data')
config.add_section('profiles_data_by_name')

if platform.lower() == "linux":
    driver = 'Linux/chromedriver'
elif platform.lower() == "darwin":
    driver = 'MacOS/chromedriver'
elif platform.lower() == "windows":
    driver = 'Windows/chromedriver.exe'
else:
    this_os = ""
    while this_os not in ["Linux", "MacOS", "Windows"]:
        print("Insert 'Linux' or 'MacOS' or 'Windows' based on this OS.")
        print("> ", end="")
        this_os = input()
    if this_os == "Linux":
        driver = 'Linux/chromedriver'
    elif this_os == "MacOS":
        driver = 'MacOS/chromedriver'
    else:
        driver = 'Windows/chromedriver.exe'

config.set('system', 'driver', os.path.join(os.path.abspath(os.path.dirname(__file__)), driver))

print("Insert linkedin username.")
print("> ", end="")
config.set('linkedin', 'username', input())

print("Insert linkedin password.")
print("> ", end="")
config.set('linkedin', 'password', input())

print("Insert the name of the .txt file that contains people profile urls.")
print("Notice: It doesn't matter if it doesn't exist right now.")
print("Suggested: profiles_data.txt")
print("> ", end="")
input_file_name = input()
config.set('profiles_data', 'input_file_name', input_file_name)
with open(input_file_name, "w"):
    pass

print("Insert the delimiter used between profile url and graduation date. If no graduation dates are present, "
      "just insert a random string.")
print("Suggested: :::")
print("> ", end="")
config.set('profiles_data', 'delimiter', input())

print("Insert the name of the .xlsx file that will contain the results of the scraping by profile url.")
print("Suggested: results_profiles.xlsx")
print("> ", end="")
config.set('profiles_data', 'output_file_name', input())

print("Do you want to append to it the timestamp in order to prevent to overwrite past results?")
print("Y for yes, N for no")
print("Suggested: Y")
print("> ", end="")
config.set('profiles_data', 'append_timestamp', input())

print("Insert the file name containing people names.")
print("Notice: It doesn't matter if it doesn't exist right now.")
print("Suggested: profiles_names.txt")
print("> ", end="")
input_file_name = input()
config.set('profiles_data_by_name', 'input_file_name', input_file_name)
with open(input_file_name, "w"):
    pass

print("Insert the delimiter used between people first name, last name, graduation date.")
print("Suggested: :::")
print("> ", end="")
config.set('profiles_data_by_name', 'delimiter', input())

print("Insert the name of the .xlsx file that will contain the results of the scraping by profile names.")
print("Suggested: results_profiles_by_name.xlsx")
print("> ", end="")
config.set('profiles_data_by_name', 'output_file_name', input())

print("Do you want to append to it the timestamp in order to prevent to overwrite past results?")
print("Y for yes, N for no")
print("Suggested: Y")
print("> ", end="")
config.set('profiles_data_by_name', 'append_timestamp', input())

with open('config.ini', 'w') as f:
    config.write(f)

print("")
print("You can now do scraping.")
print("To scrape profile by url: execute scrap_profiles.py")
print("To search profiles by name: execute search_profiles_by_name.py")
