import os
import re
import time


def linkedin_logout(browser):
    browser.get('https://www.linkedin.com/m/logout')


def linkedin_login(browser, username, password):
    browser.get('https://www.linkedin.com/uas/login')

    username_input = browser.find_element_by_id('username')
    username_input.send_keys(username)

    password_input = browser.find_element_by_id('password')
    password_input.send_keys(password)
    try:
        password_input.submit()
    except:
        pass


class Configuration:
    def __init__(self, username, password, driver_bin, number_of_profile_to_relogin, waiting_time_to_relogin, relogin_waiting_url, profile_data_delimiter, input_file, output_file):
        self.username = username
        self.password = password
        self.driver_bin = driver_bin
        self.number_of_profile_to_relogin = number_of_profile_to_relogin
        self.waiting_time_to_relogin = waiting_time_to_relogin
        self.relogin_waiting_url = relogin_waiting_url
        self.profile_data_delimiter = profile_data_delimiter
        self.input_file = input_file
        self.output_file = output_file


def load_configurations() -> Configuration:

    with open('configs.txt', 'r') as configs_file:
        username = configs_file.readline().strip()
        password = configs_file.readline().strip()
        driver = configs_file.readline().strip()

        number_of_profile_to_relogin = int(configs_file.readline().strip())
        waiting_time_to_relogin = int(configs_file.readline().strip())
        relogin_waiting_url = configs_file.readline().strip()
        profile_data_delimiter = configs_file.readline().strip()
        input_file = configs_file.readline().strip()
        output_file = configs_file.readline().strip()

    # Building of the path to Chrome driver executable file
    driver_bin = os.path.join(os.path.abspath(os.path.dirname(__file__)), driver)

    config = Configuration(username, password, driver_bin, number_of_profile_to_relogin, waiting_time_to_relogin, relogin_waiting_url, profile_data_delimiter, input_file, output_file)

    return config


def is_url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def split_date_range(date_range):
    try:
        dates = date_range.split(' – ')
        begin = parse_date(dates[0])
        end = parse_date(dates[1])
    except IndexError:
        begin = parse_date(date_range.strip())
        end = begin

    return [begin, end]


def get_today_date():
    return time.strptime(time.strftime('%d %m %y'), '%d %m %y')


def parse_date(date_str):
    if date_str == 'Present':
        return get_today_date()

    try:
        date = time.strptime(date_str, '%b %Y')
        return date
    except ValueError:
        try:
            date = time.strptime(date_str, '%Y')
            return date
        except ValueError:
            return None


def get_months_between_dates(earlier_date, later_date):
    return (time.mktime(later_date) - time.mktime(earlier_date)) // 2592000


def boolean_to_string_xls(boolean_value):
    if boolean_value is None:
        return 'N/A'

    return 'X' if boolean_value else ''


def date_to_string_xls(date):
    if date is None:
        return 'N/A'

    return time.strftime("%b-%y", date)
