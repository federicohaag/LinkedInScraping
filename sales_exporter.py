import sys
import time
from configparser import ConfigParser

import xlsxwriter
from pyvirtualdisplay import Display
from selenium import webdriver

from utils import get_browser_options, linkedin_login, message_to_user

loading_scroll_time = 1

print('Insert the sales search url')
print("> ", end="")
searchurl= input()

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

print('Starting salesnav export...')

browser.get(searchurl)
time.sleep(5)

print('Calculating pages...')

# Loading the entire page (LinkedIn loads content asynchronously based on your scrolling)
window_height = browser.execute_script("return window.innerHeight")
scrolls = 1
while scrolls * window_height < browser.execute_script("return document.body.offsetHeight"):
    browser.execute_script(f"window.scrollTo(0, {window_height * scrolls});")
    time.sleep(loading_scroll_time)
    scrolls += 1

number_of_pages = browser.execute_script("lis = document.getElementsByClassName('search-results__pagination-list')[0].children; max = lis[lis.length-1].innerText.split('… ')[1]*1; return max;")
links = []

for i in range(number_of_pages):

    current_page = i+1
    print(f'Parsing page {current_page}...')
    # Loading the entire page (LinkedIn loads content asynchronously based on your scrolling)
    window_height = browser.execute_script("return window.innerHeight")
    scrolls = 1
    while scrolls * window_height < browser.execute_script("return document.body.offsetHeight"):
        browser.execute_script(f"window.scrollTo(0, {window_height * scrolls});")
        time.sleep(loading_scroll_time)
        scrolls += 1

    list_of_links = browser.execute_script("els = document.getElementsByClassName('result-lockup__name'); u=[]; for(i=0; i<els.length; i++){u.push(els[i].children[0].href)} return u;")

    links.extend(list_of_links)

    if current_page >= number_of_pages:
        continue

    browser.execute_script("lis = document.getElementsByClassName('search-results__pagination-list')[0].children; for (i=0; i<lis.length; i++){if(lis[i].innerText*1=="+str(current_page+1)+"){lis[i].children[0].click()}}")

    time.sleep(5)

linkedin_urls = []

for link in links:
    browser.get(link)
    time.sleep(2)
    linkedin_url = browser.execute_script('return (function(){n = document.documentElement.innerHTML.indexOf("https://www.linkedin.com/in/"); url = ""; i=0; while(true){s = document.documentElement.innerHTML[n+i]; if(s==","){url = url.split(""); url.pop(); return url.join("");} else { url = url + s; i++;}}})();')
    linkedin_urls.append(linkedin_url)

workbook = xlsxwriter.Workbook('salesnav_results.xlsx')
worksheet = workbook.add_worksheet()

headers = ['Linkedin URL']

worksheet.write(0, 0, 'Linkedin URL')

i = 1
for linkedin_url in linkedin_urls:
    worksheet.write(i, 0, linkedin_url)
    i += 1

workbook.close()