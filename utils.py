import configparser
import re
import time

import pyttsx3


class HumanCheckException(Exception):
    """Human Check from Linkedin"""
    pass


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


def message_to_user(message, config):
    print(message)

    if config.get('system', 'speak') == 'Y':
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()