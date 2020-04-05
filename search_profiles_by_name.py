import time
from configparser import ConfigParser

import pyttsx3
import xlsxwriter
from selenium import webdriver
from utils import linkedin_login

waiting_time_to_load_page = 1
waiting_time_to_load_results = 5

# Loading of configurations
config = ConfigParser()
config.read('config.ini')

# Creation of a new instance of Chrome
browser = webdriver.Chrome(executable_path=config.get('system', 'driver'))

# Doing login on LinkedIn
linkedin_login(browser, config.get('linkedin', 'username'), config.get('linkedin', 'password'))

engine = pyttsx3.init()
engine.say('Avvio lettura profili Linkedin')

results = []
for query in open(config.get('profiles_data_by_name', 'input_file_name'), "r"):

    query = query.split(config.get('profiles_data_by_name', 'delimiter'))
    first_name = query[0]
    last_name = query[1]
    graduation_date = query[2]

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

                        if 'Politecnico di Milano' in school_name or ('Polytechnic' in school_name and 'Milan' in school_name):

                            edu_info = education.find_element_by_class_name('pv-entity__degree-info').text

                            if 'management' in edu_info.lower() or 'gestionale' in edu_info.lower() or 'finance' in edu_info.lower() or 'managment' in edu_info.lower():
                                is_management = True
                            else:
                                is_management = False

                            grad_check = 'NO_GRAD_CHECK'

                            graduation_year = '20' + graduation_date.split('/')[-1].strip()
                            try:
                                education_dates = education.find_element_by_class_name('pv-entity__dates').text.split(' – ')
                                if graduation_year == education_dates[1].strip():
                                    grad_check = 'GRAD_CHECKED'
                            except:
                                pass

                            if (best_solution[1] is False and is_management is True) \
                                    or best_solution[1] == '' \
                                    or (best_solution[2] == 'NO_GRAD_CHECK' and grad_check == 'GRAD_CHECKED')\
                                    or best_solution[2] == '':
                                best_solution = [browser.current_url, is_management, grad_check]
                i += 1

            needToLoop = False

        except Exception as e:
            if 'Unable to locate element: {"method":"css selector","selector":".search-global-typeahead__input"}' in e.__str__():
                needToLoop = True
                engine.say('Necessario controllo umano')
                engine.runAndWait()
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
worksheet.write(0, 1, 'Linkedin')
worksheet.write(0, 2, 'Is Management')
worksheet.write(0, 3, 'Checked Status')
xls_row = 1
for r in results:
    worksheet.write(xls_row, 0, r[0])
    worksheet.write(xls_row, 1, r[1])
    worksheet.write(xls_row, 2, r[2])
    worksheet.write(xls_row, 3, r[3])
    xls_row += 1
workbook.close()
