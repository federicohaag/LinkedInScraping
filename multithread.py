import sys
import time
import xlsxwriter
from configparser import ConfigParser

from profile_scraper import ProfileScraper
from utils import boolean_to_string_xls, date_to_string_xls, message_to_user, chunks

# Loading of configurations
config = ConfigParser()
config.read('config.ini')

headless_option = len(sys.argv) >= 2 and sys.argv[1] == 'HEADLESS'

entries = []
for entry in open(config.get('profiles_data', 'input_file_name'), "r"):
    entries.append(entry)

if len(entries) == 0:
    print("Please provide an input.")
    sys.exit(0)

if headless_option:
    grouped_entries = chunks(entries, len(entries) // int(config.get('system', 'max_threads')))
else:
    grouped_entries = entries

if len(grouped_entries) > 1:
    print(f"Starting {len(grouped_entries)} parallel scrapers.")

scrapers = []
for entries in grouped_entries:
    scrapers.append(ProfileScraper(entries, config, headless_option))

for scraper in scrapers:
    scraper.start()

for scraper in scrapers:
    scraper.join()

scraping_results = []
for scraper in scrapers:
    scraping_results.extend(scraper.results)

# Generation of XLS file with profiles data
output_file_name = config.get('profiles_data', 'output_file_name')
if config.get('profiles_data', 'append_timestamp') == 'Y':
    output_file_name_splitted = output_file_name.split('.')
    output_file_name = "".join(output_file_name_splitted[0:-1]) + "_" + str(int(time.time())) + "." + \
                       output_file_name_splitted[-1]

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

if any(scraper.interrupted for scraper in scrapers):
    message_to_user("The scraping didnt end correctly due to Human Check. The excel file was generated but it will contain some entries reporting an error string.", config)
else:
    message_to_user('Scraping successfully ended', config)
