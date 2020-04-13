import traceback
from threading import Thread

from pyvirtualdisplay import Display

from job_history_summary import JobHistorySummary
from utils import Profile, Location, Job, Company, CannotProceedScrapingException
from datetime import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from utils import linkedin_login, is_url_valid, HumanCheckException, message_to_user, get_browser_options, linkedin_logout


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


class ProfileScraper(Thread):

    def __init__(self, identifier, entries, config, headless_option):

        Thread.__init__(self)

        self._id = identifier

        print(f"Scraper #{self._id}: Setting up the browser environment...")

        self.entries = entries

        self.results = []

        # Linux-specific code needed to open a new window of Chrome
        if config.get('system', 'os') == 'linux':
            self.display = Display(visible=0, size=(800, 800))
            self.display.start()

        # Creation of a new instance of Chrome
        self.browser = webdriver.Chrome(executable_path=config.get('system', 'driver'),
                                        options=get_browser_options(headless_option, config))

        self.industries_dict = {}

        self.config = config

        self.headless_option = headless_option

        self.interrupted = False

    def parse_entry(self, entry, delimiter: str):
        # This function supports data as:
        #
        #   https://www.linkedin.com/in/federicohaag ==> parse name, email, last job
        #
        #   https://www.linkedin.com/in/federicohaag:::01/01/1730 ==> parse name, email, last job
        #   and also produces a "job history summary" returning if the person was working while studying,
        #   and how fast she/he got a job after the graduation.
        #   As graduation date is used the one passed as parameter, NOT the date it could be on LinkedIn

        if delimiter in entry:
            profile_data = entry.split(delimiter)
            profile_linkedin_url = profile_data[0]
            profile_known_graduation_date = datetime.strptime(profile_data[1].strip(), '%d/%m/%y')
        else:
            profile_linkedin_url = entry
            profile_known_graduation_date = None

        return profile_linkedin_url, profile_known_graduation_date

    def scrap_profile(self, profile_linkedin_url, profile_known_graduation_date):

        if not is_url_valid(profile_linkedin_url):
            return ScrapingResult('BadFormattedLink')

        # Scraping of the profile may fail due to human check forced by LinkedIn
        try:

            # Setting of the delay (seconds) between operations that need to be sure loading of page is ended
            loading_pause_time = 2
            loading_scroll_time = 1

            # Opening of the profile page
            self.browser.get(profile_linkedin_url)

            if not str(self.browser.current_url).strip() == profile_linkedin_url.strip():
                if self.browser.current_url == 'https://www.linkedin.com/in/unavailable/':
                    return ScrapingResult('ProfileUnavailable')
                else:
                    raise HumanCheckException

            # Scraping the Email Address from Contact Info (email)

            # > click on 'Contact info' link on the page
            self.browser.execute_script(
                "(function(){try{for(i in document.getElementsByTagName('a')){let el = document.getElementsByTagName('a')[i]; "
                "if(el.innerHTML.includes('Contact info')){el.click();}}}catch(e){}})()")
            time.sleep(loading_pause_time)

            # > gets email from the 'Contact info' popup
            try:
                email = self.browser.execute_script(
                    "return (function(){try{for (i in document.getElementsByClassName('pv-contact-info__contact-type')){ let "
                    "el = "
                    "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
                    "'ci-email')){ "
                    "return el.children[2].children[0].innerText; } }} catch(e){return '';}})()")

                self.browser.execute_script("document.getElementsByClassName('artdeco-modal__dismiss')[0].click()")
            except:
                email = 'N/A'

            # Loading the entire page (LinkedIn loads content asynchronously based on your scrolling)
            window_height = self.browser.execute_script("return window.innerHeight")
            scrolls = 1
            while scrolls * window_height < self.browser.execute_script("return document.body.offsetHeight"):
                self.browser.execute_script(f"window.scrollTo(0, {window_height * scrolls});")
                time.sleep(loading_scroll_time)
                scrolls += 1

            try:
                self.browser.execute_script(
                    "document.getElementsByClassName('pv-profile-section__see-more-inline')[0].click()")
                time.sleep(loading_pause_time)
            except:
                pass

            # Get all the job positions
            try:
                job_positions = self.browser.find_element_by_id('experience-section').find_elements_by_tag_name('li')
            except:
                job_positions = []

            # Parsing of the page html structure
            soup = BeautifulSoup(self.browser.page_source, 'lxml')

            # Scraping the Name (using soup)
            try:
                name_div = soup.find('div', {'class': 'flex-1 mr5'})
                name_loc = name_div.find_all('ul')
                profile_name = name_loc[0].find('li').get_text().strip()
            except:
                return ScrapingResult('ERROR IN SCRAPING NAME')

            # Parsing skills
            try:
                self.browser.execute_script(
                    "document.getElementsByClassName('pv-skills-section__additional-skills')[0].click()")
                time.sleep(loading_pause_time)
            except:
                pass

            try:
                skills = self.browser.execute_script(
                    "return (function(){els = document.getElementsByClassName('pv-skill-category-entity');results = [];for (var i=0; i < els.length; i++){results.push(els[i].getElementsByClassName('pv-skill-category-entity__name-text')[0].innerText);}return results;})()")
            except:
                skills = []

            # Parsing the job positions
            if len(job_positions) > 0:

                # Parse job positions to extract relative the data ranges
                job_positions_data_ranges = []
                for job_position in job_positions:

                    # Get the date range of the job position
                    try:
                        date_range_element = job_position.find_element_by_class_name('pv-entity__date-range')
                        date_range_spans = date_range_element.find_elements_by_tag_name('span')
                        date_range = date_range_spans[1].text

                        job_positions_data_ranges.append(date_range)
                    except:
                        pass

                # Scraping of the last (hopefully current) Job
                exp_section = soup.find('section', {'id': 'experience-section'})
                exp_section = exp_section.find('ul')
                div_tags = exp_section.find('div')
                a_tags = div_tags.find('a')

                # Scraping of the last Job - company_name, job_title
                try:
                    last_job_company_name = a_tags.find_all('p')[1].get_text().strip()
                    last_job_title = a_tags.find('h3').get_text().strip()

                    spans = a_tags.find_all('span')
                except:
                    last_job_company_name = a_tags.find_all('span')[1].get_text().strip()
                    last_job_title = exp_section.find('ul').find('li').find_all('span')[2].get_text().strip()

                    spans = exp_section.find('ul').find('li').find_all('span')

                last_job_company_name = last_job_company_name.replace('Full-time', '').replace('Part-time', '').strip()

                # Scraping of last Job - location
                last_job_location = Location()
                next_span_is_location = False
                for span in spans:
                    if next_span_is_location:
                        last_job_location.parse_string(span.get_text().strip())
                        break
                    if span.get_text().strip() == 'Location':
                        next_span_is_location = True

                # Scraping of Industry related to last Job
                last_job_company_url = a_tags.get('href')
                if last_job_company_url not in self.industries_dict:
                    try:
                        self.browser.get('https://www.linkedin.com' + last_job_company_url)
                        self.industries_dict[last_job_company_url] = self.browser.execute_script(
                            "return document.getElementsByClassName("
                            "'org-top-card-summary-info-list__info-item')["
                            "0].innerText")
                    except:
                        self.industries_dict[last_job_company_url] = 'N/A'

                last_job_company_industry = self.industries_dict[last_job_company_url]

                last_job = Job(
                    position=last_job_title,
                    company=Company(
                        name=last_job_company_name,
                        industry=last_job_company_industry
                    ),
                    location=last_job_location
                )

                return ScrapingResult(
                    Profile(
                        profile_name,
                        email,
                        skills,
                        last_job,
                        JobHistorySummary(
                            profile_known_graduation_date,
                            job_positions_data_ranges
                        )
                    )
                )

            else:
                return ScrapingResult(
                    Profile(profile_name, email, skills)
                )

        except HumanCheckException:

            if self.headless_option:
                raise CannotProceedScrapingException

            linkedin_logout(self.browser)

            linkedin_login(self.browser, self.config.get('linkedin', 'username'),
                           self.config.get('linkedin', 'password'))

            while self.browser.current_url != 'https://www.linkedin.com/feed/':
                message_to_user('Please execute manual check', self.config)

                time.sleep(30)

            return self.scrap_profile(profile_linkedin_url, profile_known_graduation_date)

    def run(self):

        delimiter = self.config.get('profiles_data', 'delimiter')

        print(f"Scraper #{self._id}: Executing LinkedIn login...")

        # Doing login on LinkedIn
        linkedin_login(self.browser, self.config.get('linkedin', 'username'), self.config.get('linkedin', 'password'))

        start_time = time.time()

        count = 0

        for entry in self.entries:

            count += 1

            # Print statistics about ending time of the script
            if count > 1:
                time_left = ((time.time() - start_time) / count) * (len(self.entries) - count + 1)
                ending_in = time.strftime("%H:%M:%S", time.gmtime(time_left))
            else:
                ending_in = "Unknown time"

            print(f"Scraper #{self._id}: Scraping profile {count} / {len(self.entries)} - {ending_in} left")

            try:
                linkedin_url, known_graduation_date = self.parse_entry(entry, delimiter)
                scraping_result = self.scrap_profile(linkedin_url, known_graduation_date)
                self.results.append(scraping_result)

            except CannotProceedScrapingException:
                self.results.append(ScrapingResult('TerminatedDueToHumanCheckError'))
                self.interrupted = True
                break

            except:
                with open("errlog.txt", "a") as errlog:
                    traceback.print_exc(file=errlog)
                self.results.append(ScrapingResult('GenericError'))

        # Closing the Chrome instance
        self.browser.quit()

        end_time = time.time()
        elapsed_time = time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))

        print(f"Scraper #{self._id}: Parsed {count} / {len(self.entries)} profiles in {elapsed_time}")
