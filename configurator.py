from configparser import ConfigParser

config = ConfigParser()

config.add_section('system')
config.add_section('linkedin')
config.add_section('profiles_data')
config.add_section('profiles_data_by_name')

print("Welcome to the configuration process.")

linkedin_username = ""
while linkedin_username == "":
    print("Insert linkedin username.")
    print("> ", end="")
    linkedin_username = input()
config.set('linkedin', 'username', linkedin_username)

linkedin_password = ""
while linkedin_password == "":
    print("Insert linkedin password.")
    print("> ", end="")
    linkedin_password = input()
config.set('linkedin', 'password', linkedin_password)

print("Insert the name of the .txt file that contains people profile urls.")
print("Notice: It doesn't matter if it doesn't exist right now.")
print("Leave blank for default option (profiles_data.txt)")
print("> ", end="")
input_file_name = input()
input_file_name = input_file_name if not input_file_name == "" else "profiles_data.txt"
config.set('profiles_data', 'input_file_name', input_file_name)
with open(input_file_name, "w"):
    pass

print("Insert the name of the .xlsx file that will contain the results of the scraping by profile url.")
print("Leave blank for default option (results_profiles.xlsx)")
print("> ", end="")
output_file_name = input()
output_file_name = output_file_name if not output_file_name == "" else "results_profiles.xlsx"
config.set('profiles_data', 'output_file_name', output_file_name)

print("Do you want to append to it the timestamp in order to prevent to overwrite past results?")
print("Y for yes, N for no")
print("Leave blank for default option (Y)")
print("> ", end="")
append_timestamp = input()
append_timestamp = append_timestamp if not append_timestamp == "" else "Y"
config.set('profiles_data', 'append_timestamp', append_timestamp)

with open('config.ini', 'w') as f:
    config.write(f)

print("")
print("Configuration completed. You can now do scraping.")
print("To scrape profile by url: execute do_scraping.py")
print("To search profiles by name: execute search_profiles_by_name.py")
