import sys
import time
from configparser import ConfigParser

import xlsxwriter
from pyvirtualdisplay import Display
from selenium import webdriver
from utils import linkedin_login, message_to_user, get_browser_options

waiting_time_to_load_page = 1
waiting_time_to_load_results = 5

# Loading of configurations
config = ConfigParser()
config.read('config.ini')

if config.get('system', 'os') == 'linux':
    display = Display(visible=0, size=(800, 800))
    display.start()

headless_option = len(sys.argv) >= 2 and sys.argv[1] == 'HEADLESS'

# Creation of a new instance of Chrome
browser = webdriver.Chrome(executable_path=config.get('system', 'driver'), options=get_browser_options(headless_option, config))

# Doing login on LinkedIn
linkedin_login(browser, config.get('linkedin', 'username'), config.get('linkedin', 'password'))

message_to_user('Starting reading Linkedin profiles')

results = []
for query in open(config.get('profiles_data_by_name', 'input_file_name'), "r"):

    query = query.split(config.get('profiles_data_by_name', 'delimiter'))

    first_name = query[0]

    last_name = query[1]

    try:
        university = query[2].split(',')
    except:
        university = None

    try:
        course = query[3].split(',')
    except:
        course = None

    try:
        graduation_date = query[4]
    except:
        graduation_date = None

    education_constraints = {
        'course': course,
        'university': university
    }

    if len(first_name.split(" ")) > 1:
        first_name = first_name.split(" ")[0]

    if len(last_name.split(" ")) > 1:
        last_name = last_name.split(" ")[0]

    name = first_name + " " + last_name

    needToLoop = True

    while needToLoop:

        best_solution = ['N/A', '', '']

        try:
            # Clears the search box
            browser.find_element_by_class_name('search-global-typeahead__input').clear()

            time.sleep(1)

            # Search on the search bar the name of the person we are looking for
            browser.find_element_by_class_name('search-global-typeahead__input').send_keys(name.strip())

            time.sleep(waiting_time_to_load_results)

            search_results = browser.find_elements_by_css_selector('.basic-typeahead__triggered-content > div > div')[1:-1]

            i = 0

            while i < len(search_results) and not (best_solution[1] is True and best_solution[2] == 'GRAD_CHECKED'):

                if i > 0:
                    # Clears the search box
                    browser.find_element_by_class_name('search-global-typeahead__input').clear()

                    time.sleep(1)

                    # Search on the search bar the name of the person we are looking for
                    browser.find_element_by_class_name('search-global-typeahead__input').send_keys(name.strip())

                    time.sleep(waiting_time_to_load_results)

                    search_results = browser.find_elements_by_css_selector(
                        '.basic-typeahead__triggered-content > div > div')[1:-1]

                search_results[i].click()

                time.sleep(waiting_time_to_load_page)

                if 'com/in/' in browser.current_url:

                    # Loading the entire page (LinkedIn loads content asynchronously based on your scrolling)
                    window_height = browser.execute_script("return window.innerHeight")
                    scrolls = 1
                    while scrolls * window_height < browser.execute_script("return document.body.offsetHeight"):
                        browser.execute_script(f"window.scrollTo(0, {window_height * scrolls});")
                        time.sleep(waiting_time_to_load_page)
                        scrolls += 1

                    try:
                        educations = browser.find_element_by_id('education-section').find_elements_by_tag_name('li')
                    except:
                        educations = []

                    for education in educations:
                        try:
                            school_name = education.find_element_by_class_name('pv-entity__school-name').text
                        except:
                            school_name = ''

                        if education_constraints['university'] is None:
                            continue

                        if any(x in school_name for x in education_constraints['university']):

                            edu_info = education.find_element_by_class_name('pv-entity__degree-info').text

                            education_checked = False
                            if education_constraints['course'] is not None:
                                if any(x in edu_info.lower() for x in education_constraints['course']):
                                    education_checked = True

                            # Check if the graduation year known is equal to the one specified in LinkedIn
                            grad_check = 'NO_GRAD_CHECK'
                            if graduation_date is not None:
                                graduation_year = '20' + graduation_date.split('/')[-1].strip()
                                try:
                                    education_dates = education.find_element_by_class_name('pv-entity__dates').text.split(' – ')
                                    if graduation_year == education_dates[1].strip():
                                        grad_check = 'GRAD_CHECKED'
                                except:
                                    pass

                            if (best_solution[1] is False and education_checked is True) \
                                    or best_solution[1] == '' \
                                    or (best_solution[2] == 'NO_GRAD_CHECK' and grad_check == 'GRAD_CHECKED')\
                                    or best_solution[2] == '':
                                best_solution = [browser.current_url, education_checked, grad_check]
                i += 1

            needToLoop = False

        except Exception as e:
            if 'Unable to locate element: {"method":"css selector","selector":".search-global-typeahead__input"}' in e.__str__():
                needToLoop = True

                message_to_user('Please execute manual check')

                time.sleep(10)
            else:
                needToLoop = False

    results.append(
        [
            name,
            best_solution[0],
            best_solution[1],
            best_solution[2]
        ]
    )

browser.quit()

# Generation of XLS file with profiles data

output_file_name = config.get('profiles_data_by_name', 'output_file_name')
if config.get('profiles_data_by_name', 'append_timestamp') == 'Y':
    output_file_name_splitted = output_file_name.split('.')
    output_file_name = "".join(output_file_name_splitted[0:-1]) + "_" + str(int(time.time())) + "." + output_file_name_splitted[-1]

workbook = xlsxwriter.Workbook(output_file_name)
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, 'Name')
worksheet.write(0, 1, 'Linkedin Profile URL')
worksheet.write(0, 2, 'Education Checked')
worksheet.write(0, 3, 'Checked Status')
xls_row = 1
for r in results:
    worksheet.write(xls_row, 0, r[0])
    worksheet.write(xls_row, 1, r[1])
    worksheet.write(xls_row, 2, r[2])
    worksheet.write(xls_row, 3, r[3])
    xls_row += 1
workbook.close()

message_to_user('Search of profiles ended.')