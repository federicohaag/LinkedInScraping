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


def load_configurations():
    configurations = open('configs.txt', 'r')
    username = configurations.readline()
    password = configurations.readline()
    driver = configurations.readline()
    configurations.close()

    # Building of the path to Chrome driver executable file
    driver_bin = os.path.join(os.path.abspath(os.path.dirname(__file__)), driver)

    return [username, password, driver_bin]


def did_study_in_polimi(browser):
    if len(browser.find_elements_by_class_name('pv-top-card--experience-list-item')) > 1:
        if 'Politecnico di Milano' in browser.find_elements_by_class_name('pv-top-card--experience-list-item')[1].text:
            return True

    window_height = browser.execute_script("return window.innerHeight")
    i = 1

    while i < 6:
        browser.execute_script(f"window.scrollTo(0, {window_height * i});")
        time.sleep(5)

        try:
            if 'Politecnico di Milano' in browser.find_element_by_id('education-section').text:
                return True
        except:
            pass

        i += 1
    return False


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
        end = time.strptime(time.strftime('%d %m %y'), '%d %m %y')

    return [begin, end]


def parse_date(date_str):
    if date_str == 'Present':
        return time.strptime(time.strftime('%d %m %y'), '%d %m %y')

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
