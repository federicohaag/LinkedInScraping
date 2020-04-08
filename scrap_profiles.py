from datetime import datetime
import time
import xlsxwriter
from configparser import ConfigParser
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display
from utils import linkedin_login, is_url_valid, get_months_between_dates, \
    split_date_range, boolean_to_string_xls, date_to_string_xls, HumanCheckException, message_to_user, get_options, \
    linkedin_logout


class JobHistorySummary:
    def __init__(self, had_job_while_studying=None, had_job_after_graduation=None,
                 had_job_after_graduation_within_3_months=None, had_job_after_graduation_within_5_months=None,
                 had_job_after_graduation_within_6_months=None, date_first_job_after_beginning_university=None,
                 date_first_job_after_ending_university=None, jobs_now=None, first_job_ever_date=None, jobs=None):
        self.had_job_while_studying = had_job_while_studying
        self.had_job_after_graduation = had_job_after_graduation
        self.had_job_after_graduation_within_3_months = had_job_after_graduation_within_3_months
        self.had_job_after_graduation_within_5_months = had_job_after_graduation_within_5_months
        self.had_job_after_graduation_within_6_months = had_job_after_graduation_within_6_months
        self.date_first_job_after_beginning_university = date_first_job_after_beginning_university
        self.date_first_job_after_ending_university = date_first_job_after_ending_university
        self.jobs_now = jobs_now
        self.first_job_ever_date = first_job_ever_date

        if jobs_now is None:
            self.more_than_a_job_now = None
            self.is_currently_unemployed = None
        else:
            self.more_than_a_job_now = jobs_now > 1
            self.is_currently_unemployed = jobs_now == 0

        if jobs is None:
            self.never_had_jobs = False
        else:
            self.never_had_jobs = len(jobs) == 0


class Location:
    def __init__(self, city='N/A', country='N/A', location='N/A'):
        self.full_string = location
        self.city = city
        self.country = country

    def parse_string(self, location):
        self.full_string = location
        if ',' in location:
            # TODO: Probably useless try - except. To be checked.
            try:
                self.city = location.split(',')[0]
                self.country = location.split(',')[-1]
            except:
                pass


class Company:
    def __init__(self, name='N/A', industry='N/A'):
        self.name = name
        self.industry = industry


class Job:
    def __init__(self, company=Company(), position='N/A', location=Location()):
        self.company = company
        self.position = position
        self.location = location

    def __set__(self, instance, value):
        self.instance = value


class Profile:
    def __init__(self, profile_name, email, skills, current_job=Job(), job_history_summary=JobHistorySummary()):
        self.profile_name = profile_name
        self.email = email
        self.skills = skills
        self.current_job = current_job
        self.jobs_history = job_history_summary


class ScrapingResult:
    def __init__(self, arg):
        if isinstance(arg, Profile):
            self.profile = arg
            self.message = None
        else:
            self.profile = None
            self.message = arg

    def is_error(self):
        return self.profile is None


# TODO: find out what is the type of exception that can be fired to do specific except (and not general ones like now)
def scrap_profile(profile_to_scrap, delimiter: str) -> ScrapingResult:
    # This function supports data as:
    #
    #   https://www.linkedin.com/in/federicohaag ==> parse name, email, last job
    #
    #   https://www.linkedin.com/in/federicohaag:::01/01/1730 ==> parse name, email, last job
    #   and also produces a "job history summary" returning if the person was working while studying,
    #   and how fast she/he got a job after the graduation.
    #   As graduation date is used the one passed as parameter, NOT the date it could be on LinkedIn

    if delimiter in profile_to_scrap:
        profile_data = profile_to_scrap.split(delimiter)
        profile_linkedin_url = profile_data[0]
        profile_known_graduation_date = datetime.strptime('/'.join(profile_data[1].strip().split("/")[1:]), '%m/%y')
    else:
        profile_linkedin_url = profile_to_scrap
        profile_known_graduation_date = None

    if not is_url_valid(profile_linkedin_url):
        return ScrapingResult('BadFormattedLink')

    # Scraping of the profile may fail due to human check forced by LinkedIn
    try:
        return get_profile_data(profile_linkedin_url, profile_known_graduation_date)
    except HumanCheckException:

        print("Human")

        linkedin_logout(browser)

        linkedin_login(browser, config.get('linkedin', 'username'), config.get('linkedin', 'password'))

        while browser.current_url != 'https://www.linkedin.com/feed/':

            message_to_user('Please execute manual check', config)

            time.sleep(30)

        return scrap_profile(profile_to_scrap, delimiter)


def get_profile_data(profile_linkedin_url, known_graduation_date):
    global industries_dict

    # Setting of the delay (seconds) between operations that need to be sure loading of page is ended
    loading_pause_time = 2
    loading_scroll_time = 1

    # Opening of the profile page
    browser.get(profile_linkedin_url)

    if not str(browser.current_url).strip() == profile_linkedin_url.strip():
        print(browser.current_url)
        print(profile_linkedin_url)
        if browser.current_url == 'https://www.linkedin.com/in/unavailable/':
            return ScrapingResult('ProfileUnavailable')
        else:
            raise HumanCheckException

    # Scraping the Email Address from Contact Info (email)

    # > click on 'Contact info' link on the page
    browser.execute_script(
        "(function(){try{for(i in document.getElementsByTagName('a')){let el = document.getElementsByTagName('a')[i]; "
        "if(el.innerHTML.includes('Contact info')){el.click();}}}catch(e){}})()")
    time.sleep(loading_pause_time)

    # > gets email from the 'Contact info' popup
    try:
        email = browser.execute_script(
            "return (function(){try{for (i in document.getElementsByClassName('pv-contact-info__contact-type')){ let "
            "el = "
            "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
            "'ci-email')){ "
            "return el.children[2].children[0].innerText; } }} catch(e){return '';}})()")

        browser.execute_script("document.getElementsByClassName('artdeco-modal__dismiss')[0].click()")
    except:
        email = 'N/A'

    # Loading the entire page (LinkedIn loads content asynchronously based on your scrolling)
    window_height = browser.execute_script("return window.innerHeight")
    scrolls = 1
    while scrolls * window_height < browser.execute_script("return document.body.offsetHeight"):
        browser.execute_script(f"window.scrollTo(0, {window_height * scrolls});")
        time.sleep(loading_scroll_time)
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

    # Get job experiences (two different positions in Company X is considered one job experience)
    try:
        job_experiences = browser.find_elements_by_class_name('pv-profile-section__card-item-v2')
    except:
        job_experiences = []

    # Parsing of the page html structure
    soup = BeautifulSoup(browser.page_source, 'lxml')

    # Scraping the Name (using soup)
    try:
        name_div = soup.find('div', {'class': 'flex-1 mr5'})
        name_loc = name_div.find_all('ul')
        profile_name = name_loc[0].find('li').get_text().strip()
    except:
        return ScrapingResult('ERROR IN SCRAPING NAME')

    #Parsing skills
    try:
        browser.execute_script("document.getElementsByClassName('pv-skills-section__additional-skills')[0].click()")
        time.sleep(loading_pause_time)
    except:
        pass

    try:
        skills = browser.execute_script("return (function(){els = document.getElementsByClassName('pv-skill-category-entity');results = [];for (var i=0; i < els.length; i++){results.push(els[i].getElementsByClassName('pv-skill-category-entity__name-text')[0].innerText);}return results;})()")
    except:
        skills = []

    print(skills)

    # Parsing the job positions
    if len(list_of_job_positions) > 0:

        # Parse job positions to extract relative the data ranges
        job_positions_data_ranges = []
        for job_position in list_of_job_positions:

            # Get the date range of the job position
            try:
                date_range_element = job_position.find_element_by_class_name('pv-entity__date-range')
                date_range_spans = date_range_element.find_elements_by_tag_name('span')
                date_range = date_range_spans[1].text

                job_positions_data_ranges.append(date_range)
            except:
                pass

        # Compute the 'job history' of the profile if the graduation date is provided in profiles_data.txt file
        job_history_summary = compute_job_history_summary(known_graduation_date, job_positions_data_ranges,
                                                          job_experiences)

        # Scraping of the last (hopefully current) Job
        exp_section = soup.find('section', {'id': 'experience-section'})
        exp_section = exp_section.find('ul')
        div_tags = exp_section.find('div')
        a_tags = div_tags.find('a')

        # Scraping of the last (hopefully current) Job - company_name, job_title
        try:
            current_job_company_name = a_tags.find_all('p')[1].get_text().strip()
            current_job_title = a_tags.find('h3').get_text().strip()

            spans = a_tags.find_all('span')
        except:
            current_job_company_name = a_tags.find_all('span')[1].get_text().strip()
            current_job_title = exp_section.find('ul').find('li').find_all('span')[2].get_text().strip()

            spans = exp_section.find('ul').find('li').find_all('span')

        current_job_company_name = current_job_company_name.replace('Full-time', '').replace('Part-time', '').strip()

        # Scraping of last (hopefully current) Job - location
        location = Location()
        next_span_is_location = False
        for span in spans:
            if next_span_is_location:
                location.parse_string(span.get_text().strip())
                break
            if span.get_text().strip() == 'Location':
                next_span_is_location = True

        # Scraping of Industry related to last (hopefully current) Job
        company_url = a_tags.get('href')
        if company_url not in industries_dict:
            try:
                browser.get('https://www.linkedin.com' + company_url)
                industries_dict[company_url] = browser.execute_script("return document.getElementsByClassName("
                                                                      "'org-top-card-summary-info-list__info-item')["
                                                                      "0].innerText")
            except:
                industries_dict[company_url] = 'N/A'

        current_job_company_industry = industries_dict[company_url]

        company = Company(
            name=current_job_company_name,
            industry=current_job_company_industry
        )
        current_job = Job(
            position=current_job_title,
            company=company,
            location=location
        )
        profile = Profile(profile_name, email, skills, current_job, job_history_summary)

    else:
        profile = Profile(profile_name, email, skills)

    return ScrapingResult(profile)


# Returns a 'summary' of the job history of the person with reference to the known graduation_date
def compute_job_history_summary(graduation_date, job_positions_data_ranges, job_experiences) -> JobHistorySummary:

    jobs_now = 0

    for job_experience in job_experiences:
        found_present = False
        for d_range in job_experience.find_elements_by_class_name('pv-entity__date-range'):
            found_present = found_present or ('present' in d_range.text.lower())

        jobs_now += 1 if found_present else 0

    summary = JobHistorySummary(
        had_job_after_graduation=False,
        had_job_after_graduation_within_3_months=False,
        had_job_after_graduation_within_5_months=False,
        had_job_after_graduation_within_6_months=False,
        had_job_while_studying=False,
        jobs_now=jobs_now,
        jobs=job_experiences
    )

    if graduation_date is not None and len(job_positions_data_ranges) > 0:

        beginning_of_university = datetime.fromtimestamp(datetime.timestamp(graduation_date) - 63072000)
        three_months_after_graduation_date = datetime.fromtimestamp(datetime.timestamp(graduation_date) + 7776000)
        five_months_after_graduation_date = datetime.fromtimestamp(datetime.timestamp(graduation_date) + 12960000)
        six_months_after_graduation_date = datetime.fromtimestamp(datetime.timestamp(graduation_date) + 15552000)

        for date_range in job_positions_data_ranges:

            # Split the date range into the two initial and ending date
            initial_date, end_date = split_date_range(date_range)

            if summary.first_job_ever_date is None:
                summary.first_job_ever_date = initial_date
            else:
                if initial_date < summary.first_job_ever_date:
                    summary.first_job_ever_date = initial_date

            # Checking if was working while studying
            if beginning_of_university <= initial_date <= graduation_date:
                summary.had_job_while_studying = True

            if initial_date >= beginning_of_university:

                if summary.date_first_job_after_beginning_university is None:
                    summary.date_first_job_after_beginning_university = initial_date
                else:
                    if initial_date < summary.date_first_job_after_beginning_university:
                        summary.date_first_job_after_beginning_university = initial_date

            if initial_date <= graduation_date <= end_date:
                summary.had_job_after_graduation = True

            if initial_date > graduation_date:
                if summary.date_first_job_after_ending_university is None:
                    summary.date_first_job_after_ending_university = initial_date
                else:
                    if initial_date < summary.date_first_job_after_ending_university:
                        summary.date_first_job_after_ending_university = initial_date

            if initial_date <= three_months_after_graduation_date <= end_date:
                summary.had_job_after_graduation_within_3_months = True

            if initial_date <= five_months_after_graduation_date <= end_date:
                summary.had_job_after_graduation_within_5_months = True

            if initial_date <= six_months_after_graduation_date <= end_date:
                summary.had_job_after_graduation_within_6_months = True

    return summary


# Loading of configurations
config = ConfigParser()
config.read('config.ini')

# Linux-specific code needed to open a new window of Chrome
if config.get('system', 'os') == 'linux':
    display = Display(visible=0, size=(800, 800))
    display.start()

# Creation of a new instance of Chrome
browser = webdriver.Chrome(executable_path=config.get('system', 'driver'), options=get_options(config))

message_to_user('Starting Linkedin Scraping', config)

# Doing login on LinkedIn
linkedin_login(browser, config.get('linkedin', 'username'), config.get('linkedin', 'password'))

scraping_results = []
start_time = time.time()
industries_dict = {}  # Store all the industries scraped to speed up the scraping process

number_of_profiles = sum(1 for profile_data in open(config.get('profiles_data', 'input_file_name'), "r"))

count = 1
for profile_data in open(config.get('profiles_data', 'input_file_name'), "r"):

    # Print statistics about ending time of the script

    ending_in = time.strftime("%H:%M:%S",
                              time.gmtime(((time.time() - start_time) / count) * (number_of_profiles - count)))
    print(f"Scraping profile {count} / {number_of_profiles} - {ending_in} left")

    # Scrap profile
    try:
        scraping_result: ScrapingResult = scrap_profile(profile_data, config.get('profiles_data', 'delimiter'))
        scraping_results.append(scraping_result)
    except:
        scraping_results.append(ScrapingResult('GenericError'))

    count += 1

# Closing the Chrome instance
browser.quit()

# Generation of XLS file with profiles data

output_file_name = config.get('profiles_data', 'output_file_name')
if config.get('profiles_data', 'append_timestamp') == 'Y':
    output_file_name_splitted = output_file_name.split('.')
    output_file_name = "".join(output_file_name_splitted[0:-1]) + "_" + str(int(time.time())) + "." + output_file_name_splitted[-1]

workbook = xlsxwriter.Workbook(output_file_name)
worksheet = workbook.add_worksheet()

headers = ['Name', 'Email', 'Skills', 'Company', 'Industry', 'Job Title', 'City', 'Country',
            'DATE FIRST JOB EVER', 'DATE FIRST JOB AFTER BEGINNING POLIMI', 'DATE FIRST JOB AFTER ENDING POLIMI',
           'JOB WITHIN 3 MONTHS', 'JOB WITHIN 5 MONTHS', 'JOB WITHIN 6 MONTHS', 'JOB WHILE STUDYING',
           'MORE THAN ONE JOB POSITION', 'NOT CURRENTLY EMPLOYED', 'NEVER HAD JOBS']

# Set the headers of xls file
for h in range(len(headers)):
    worksheet.write(0, h, headers[h])

for i in range(len(scraping_results)):

    scraping_result = scraping_results[i]

    if scraping_result.is_error():
        data = ['Error_' + scraping_result.message] * len(headers)
    else:
        p = scraping_result.profile
        data = [
            p.profile_name,
            p.email,
            ",".join(p.skills),
            p.current_job.company.name,
            p.current_job.company.industry,
            p.current_job.position,
            p.current_job.location.city,
            p.current_job.location.country,
            date_to_string_xls(p.jobs_history.first_job_ever_date),
            date_to_string_xls(p.jobs_history.date_first_job_after_beginning_university),
            date_to_string_xls(p.jobs_history.date_first_job_after_ending_university),
            boolean_to_string_xls(p.jobs_history.had_job_after_graduation_within_3_months),
            boolean_to_string_xls(p.jobs_history.had_job_after_graduation_within_5_months),
            boolean_to_string_xls(p.jobs_history.had_job_after_graduation_within_6_months),
            boolean_to_string_xls(p.jobs_history.had_job_while_studying),
            boolean_to_string_xls(p.jobs_history.more_than_a_job_now),
            boolean_to_string_xls(p.jobs_history.is_currently_unemployed),
            boolean_to_string_xls(p.jobs_history.never_had_jobs)
        ]

    for j in range(len(data)):
        worksheet.write(i + 1, j, data[j])

workbook.close()

print(f"Scraping ended at {time.strftime('%H:%M:%S', time.gmtime(time.time()))}")
print(f"Parsed {number_of_profiles} profiles in {time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}")

message_to_user('Scraping Ended', config)
