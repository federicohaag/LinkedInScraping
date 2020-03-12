import time
import xlsxwriter
from bs4 import BeautifulSoup
from selenium import webdriver

from utils import linkedin_login, linkedin_logout, load_configurations, is_url_valid, get_months_between_dates, \
    split_date_range


def get_profile_data(encoded_profile_data, delimiter):
    # this function supports data as:
    #
    #   https://www.linkedin.com/in/federicohaag ==> parse name, email, last job
    #
    #   https://www.linkedin.com/in/federicohaag:::01/01/1730 ==> parse name, email, last job
    #   and also produces a "job history summary" returning if the person was working while studying,
    #   and how fast she/he got a job after the graduation.
    #   As graduation date is used the one passed as parameter, NOT the date it could be on LinkedIn

    profile_data_splitted = encoded_profile_data.split(delimiter)

    profile_linkedin_url = profile_data_splitted[0]
    known_graduation_date = None

    # Set the known graduation date if the input is url:::graduation_date
    if len(profile_data_splitted) == 2:
        known_graduation_date = time.strptime(profile_data_splitted[1].strip(), '%d/%m/%y')

    if not is_url_valid(profile_linkedin_url):
        return get_profile_result('BAD FORMATTED LINK')

    # Setting of the delay (seconds) between operations that need to be sure loading of page is ended
    loading_pause_time = 2

    # Opening of the profile page
    browser.get(profile_linkedin_url)

    # Scraping the Email Address from Contact Info (email)

    # > click on 'Contact info' link on the page
    browser.execute_script(
        "(function(){try{for(i in document.getElementsByTagName('a')){let el = document.getElementsByTagName('a')[i]; "
        "if(el.innerHTML.includes('Contact info')){el.click();}}}catch(e){}})()")
    time.sleep(loading_pause_time)

    # > gets email from the 'Contact info' popup
    try:
        email = browser.execute_script(
            "return (function(){try{for (i in document.getElementsByClassName('pv-contact-info__contact-type')){ let el = "
            "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes('ci-email')){ "
            "return el.children[2].children[0].innerText; } }} catch(e){return '';}})()")

        browser.execute_script("document.getElementsByClassName('artdeco-modal__dismiss')[0].click()")
    except:
        email = 'N/A'

    # Loading the entire page (LinkedIn loads content asynchronously based on your scrolling)
    window_height = browser.execute_script("return window.innerHeight")
    scrolls = 1
    while scrolls * window_height < browser.execute_script("return document.body.offsetHeight"):
        browser.execute_script(f"window.scrollTo(0, {window_height * scrolls});")
        time.sleep(loading_pause_time)
        scrolls += 1

    try:
        browser.execute_script("document.getElementsByClassName('pv-profile-section__see-more-inline')[0].click()")
        time.sleep(loading_pause_time)
    except:
        pass

    # Get all the job positions
    try:
        list_of_job_positions = browser.find_element_by_id('experience-section').find_elements_by_tag_name('li')
    except:
        list_of_job_positions = []

    # Parsing of the page html structure
    soup = BeautifulSoup(browser.page_source, 'lxml')

    # Scraping the Name (using soup)
    name_div = soup.find('div', {'class': 'flex-1 mr5'})
    name_loc = name_div.find_all('ul')
    profile_name = name_loc[0].find('li').get_text().strip()

    # Parsing the job positions
    if len(list_of_job_positions) == 0:

        return get_profile_result(profile_name, email)

    else:

        # Parse job positions to extract relative the data ranges
        job_positions_data_ranges = []
        for job_position in list_of_job_positions:

            # Get the date range of the job position
            try:
                date_range_element = job_position.find_element_by_class_name('pv-entity__date-range')
                date_range_spans = date_range_element.find_elements_by_tag_name('span')
                job_positions_data_ranges.append(date_range_spans[1].text)
            except:
                pass

        # Compute the 'job history' of the profile if the graduation date is provided in profiles_data.txt file
        if not known_graduation_date is None:
            job_history_summary = compute_job_history_summary(job_positions_data_ranges, known_graduation_date)
        else:
            job_history_summary = {
                'had_job_while_studying': 'N/A',
                'had_job_after_graduation': 'N/A',
                'had_job_after_graduation_within_3_months': 'N/A',
                'had_job_after_graduation_within_5_months': 'N/A'
            }

        # Scraping of the last (hopefully current) Job Position
        exp_section = soup.find('section', {'id': 'experience-section'})
        exp_section = exp_section.find('ul')
        div_tags = exp_section.find('div')
        a_tags = div_tags.find('a')

        # Scraping of the last (hopefully current) Job Position - company_name, job_title
        try:
            company_name = a_tags.find_all('p')[1].get_text().strip()
            job_title = a_tags.find('h3').get_text().strip()
            spans = a_tags.find_all('span')
        except:
            company_name = a_tags.find_all('span')[1].get_text().strip()
            job_title = exp_section.find('ul').find('li').find_all('span')[2].get_text().strip()
            spans = exp_section.find('ul').find('li').find_all('span')

        # Scraping of last (hopefully current) Job Position - location
        location = ''
        next_span_is_location = False
        for span in spans:
            if next_span_is_location:
                location = span.get_text().strip()
                break
            if span.get_text().strip() == 'Location':
                next_span_is_location = True

        # Scraping of last (hopefully current) Job Position - location - splitting it into 'City' and 'Country'
        city = 'N/A'
        country = 'N/A'
        if ',' in location:
            try:
                city = location.split(',')[0]
                country = location.split(',')[-1]
            except:
                pass

        # Scraping of Industry related to last (hopefully current) Job Position
        company_url = a_tags.get('href')
        try:
            browser.get('https://www.linkedin.com' + company_url)
            industry = browser.execute_script("return document.getElementsByClassName("
                                              "'org-top-card-summary-info-list__info-item')[0].innerText")
        except:
            industry = 'N/A'

        return get_profile_result(profile_name, email, company_name, job_title, city, country, location, industry,
                                  job_history_summary)


# Returns a data structure that is agreed with the excel builder.
def get_profile_result(profile_name, email, company_name='N/A', job_title='N/A', city='N/A', country='N/A',
                       location='N/A', industry='N/A', job_history_summary=None):

    if job_history_summary is None:
        job_history_summary = {
            'had_job_while_studying': 'N/A',
            'had_job_after_graduation': 'N/A',
            'had_job_after_graduation_within_3_months': 'N/A',
            'had_job_after_graduation_within_5_months': 'N/A'
        }
    return [
        profile_name,
        email,
        [
            company_name, job_title, [city, country, location], industry
        ],
        [
            job_history_summary['had_job_while_studying'],
            job_history_summary['had_job_after_graduation'],
            job_history_summary['had_job_after_graduation_within_3_months'],
            job_history_summary['had_job_after_graduation_within_5_months']
        ]
    ]


# Returns a 'summary' of the job history of the person with reference to the known graduation_date
def compute_job_history_summary(job_positions_data_ranges, graduation_date):
    had_job_while_studying = False
    had_job_after_graduation = False
    had_job_after_graduation_within_3_months = False
    had_job_after_graduation_within_5_months = False

    for date_range in job_positions_data_ranges:

        # Split the date range into the two initial and ending date
        initial_date, end_date = split_date_range(date_range)

        # Checking if was working while studying
        if initial_date <= graduation_date:
            if end_date >= graduation_date:
                had_job_while_studying = True
            else:
                if get_months_between_dates(earlier_date=end_date, later_date=graduation_date) <= 20:
                    had_job_while_studying = True
        else:
            had_job_after_graduation = True
            if get_months_between_dates(earlier_date=graduation_date, later_date=initial_date) <= 3:
                had_job_after_graduation_within_3_months = True
            else:
                if get_months_between_dates(earlier_date=graduation_date, later_date=initial_date) <= 5:
                    had_job_after_graduation_within_5_months = True

    return {
        'had_job_while_studying': had_job_while_studying,
        'had_job_after_graduation': had_job_after_graduation,
        'had_job_after_graduation_within_3_months': had_job_after_graduation_within_3_months,
        'had_job_after_graduation_within_5_months': had_job_after_graduation_within_5_months
    }


# Loading of configurations
username, password, driver_bin = load_configurations()

# Creation of a new instance of Chrome
browser = webdriver.Chrome(executable_path=driver_bin)

# Doing login on LinkedIn
linkedin_login(browser, username, password)

# Loading of Profiles data - see: get_profile_data()
profiles_data = []
for profile_data in open("profiles_data.txt", "r"):

    profiles_data.append(get_profile_data(profile_data, delimiter=':::'))

    # Keeps the session active: every 100 profiles do logout and then login after 10 seconds
    if len(profiles_data) % 100 == 0:
        linkedin_logout(browser)
        time.sleep(10)
        linkedin_login(browser, username, password)

# Closing the Chrome instance
browser.quit()

# Generation of XLS file with profiles data
workbook = xlsxwriter.Workbook('results_profiles.xlsx')
worksheet = workbook.add_worksheet()

headers = ['Name', 'Email', 'Company', 'Job Title', 'City', 'Country', 'Full Location', 'Industry',
           'Working while studying', 'Found job after graduation', 'Found job within 3 months',
           'Found job within 5 months']

# Set the headers of xls file
for h in range(len(headers)):
    worksheet.write(0, h, headers[h])

# Insert the data in the xls file
for i in range(len(profiles_data)):
    profile_data = profiles_data[i]
    xls_row = i + 1

    if profile_data is None:
        continue

    # Mapping of profile data based on previous declared headers
    worksheet.write(xls_row, 0, profile_data[0])
    worksheet.write(xls_row, 1, profile_data[1])
    worksheet.write(xls_row, 2, profile_data[2][0])
    worksheet.write(xls_row, 3, profile_data[2][1])
    worksheet.write(xls_row, 4, profile_data[2][2][0])
    worksheet.write(xls_row, 5, profile_data[2][2][1])
    worksheet.write(xls_row, 6, profile_data[2][2][2])
    worksheet.write(xls_row, 7, profile_data[2][3])
    worksheet.write(xls_row, 8, profile_data[3][0])
    worksheet.write(xls_row, 9, profile_data[3][1])
    worksheet.write(xls_row, 10, profile_data[3][2])
    worksheet.write(xls_row, 11, profile_data[3][3])

workbook.close()
