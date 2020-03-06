import time
import xlsxwriter
from utils import linkedin_login, linkedin_logout, load_configurations, did_study_in_polimi

waiting_time_to_load = 5

# Loading of configurations
username, password, browser = load_configurations()

# Doing login on LinkedIn
linkedin_login(browser, username, password)

results = []
for query in open("profiles_names.txt", "r"):

    # Keeps the session active over the time
    if len(results) > 100 and len(results) % 100 == 0:
        linkedin_logout(browser)
        linkedin_login(browser, username, password)

    try:
        # Search on the search bar the name of the person we are looking for
        browser.find_element_by_class_name('search-global-typeahead__input').send_keys(query.strip())
        time.sleep(waiting_time_to_load)
        # Click on the first result (could be the search list, not the profile)
        browser.find_elements_by_css_selector('.basic-typeahead__triggered-content > div > div')[1].click()
        time.sleep(waiting_time_to_load)
        # Clears the search box
        browser.find_element_by_class_name('search-global-typeahead__input').clear()

        url = browser.current_url

        if 'search' in url:
            # The previous 'click' was on 'See results' and not on a profile (==> no profiles found)
            url = 'NOT FOUND ON LINKEDIN'
        else:
            # ACCEPTANCE CONDITIONS

            # Checks if the contact studied in Politecnico di Milano.
            if not did_study_in_polimi(browser):
                url = 'NO POLIMI'
    except:
        url = 'N/A'

    results.append([query, url])

browser.quit()

# Generation of XLS file with profiles data
workbook = xlsxwriter.Workbook('results_profiles_by_name.xlsx')
worksheet = workbook.add_worksheet()
xls_row = 0
for r in results:
    worksheet.write(xls_row, 0, r[0])
    worksheet.write(xls_row, 1, r[1])
    xls_row += 1
workbook.close()


