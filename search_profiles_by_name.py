import time
import xlsxwriter
from selenium import webdriver
from utils import linkedin_login, linkedin_logout, load_configurations

waiting_time_to_load_page = 2
waiting_time_to_load_results = 5

# Loading of configurations
username, password, driver_bin = load_configurations()

# Creation of a new instance of Chrome
browser = webdriver.Chrome(executable_path=driver_bin)

# Doing login on LinkedIn
linkedin_login(browser, username, password)

time.sleep(waiting_time_to_load_page)

results = []
for query in open("profiles_names.txt", "r"):

    best_solution = ['N/A', '', '']

    query = query.split(':::')
    name = query[0]
    graduation_date = query[1]

    try:

        # Clears the search box
        browser.find_element_by_class_name('search-global-typeahead__input').clear()

        time.sleep(1)

        # Search on the search bar the name of the person we are looking for
        browser.find_element_by_class_name('search-global-typeahead__input').send_keys(name.strip())

        time.sleep(waiting_time_to_load_results)

        search_results = browser.find_elements_by_css_selector('.basic-typeahead__triggered-content > div > div')[1:-1]

        i = 0

        while i < len(search_results) and best_solution[2] != 'GRAD_CHECKED':

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

                    if 'Politecnico di Milano' in school_name:

                        edu_info = education.find_element_by_class_name('pv-entity__degree-info').text

                        if 'management' in edu_info.lower() or 'gestionale' in edu_info.lower():
                            is_management = True
                        else:
                            is_management = False

                        best_solution = [browser.current_url, is_management, 'NO_GRAD_CHECK']

                        graduation_year = '20'+graduation_date.split('/')[-1].strip()
                        try:
                            education_dates = education.find_element_by_class_name('pv-entity__dates').text.split(' – ')
                            print(f">{graduation_year},{education_dates[1]}<")
                            if graduation_year == education_dates[1].strip():
                                best_solution = [browser.current_url, is_management, 'GRAD_CHECKED']
                                break
                        except:
                            pass
            i += 1

    except Exception as e:
        print(e)

    results.append(
        [
            query[0],
            best_solution[0],
            best_solution[1],
            best_solution[2]
        ]
    )

    # Keeps the session active over the time
    if len(results) % 50 == 0:
        linkedin_logout(browser)
        time.sleep(120)
        linkedin_login(browser, username, password)

browser.quit()

# Generation of XLS file with profiles data
workbook = xlsxwriter.Workbook('results_profiles_by_name.xlsx')
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
