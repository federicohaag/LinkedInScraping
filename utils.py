import os
import re

from selenium import webdriver


def linkedin_logout(browser):
    browser.get('https://www.linkedin.com/m/logout')


def linkedin_login(browser,username,password):
    browser.get('https://www.linkedin.com/uas/login')

    username_input = browser.find_element_by_id('username')
    username_input.send_keys(username)

    password_input = browser.find_element_by_id('password')
    password_input.send_keys(password)
    try:
        password_input.submit()
    except:
        pass


def load_configurations():
    configurations = open('configs.txt', 'r')
    username = configurations.readline()
    password = configurations.readline()
    driver = configurations.readline()
    configurations.close()

    # Building of the path to Chrome driver executable file
    driver_bin = os.path.join(os.path.abspath(os.path.dirname(__file__)), driver)

    # Creation of a new instance of Chrome
    browser = webdriver.Chrome(executable_path=driver_bin)

    return [username, password, browser]


def is_polimi(browser):
    try:
        if 'Politecnico di Milano' in browser.find_elements_by_class_name('pv-top-card--experience-list-item')[1].text:
            return True
        else:
            return False
    except:
        return False


def check_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None