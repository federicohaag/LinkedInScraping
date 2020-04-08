# LinkedIn Scraping with Python

Creates an Excel file containing personal data and last job position of specified people.

If you know the graduation date of the person, you can also specify it in the input file to obtain statistics about how fast he/she got a job after graduation.

Scraping can be currently done only providing the LinkedIn profile url of the target person. If you dont have yet the LinkedIn profile url, you can make it to be searched automatically (see below).

Doubts? Reach me out on [LinkedIn](https://www.linkedin.com/in/federicohaag/).

## Prerequisites

You must have installed in your machine (higher versions are fine):
* Google Chrome v.80
* Python 3.8


## Installing

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

1. Download the whole repository.
2. Place the directory `LinkedinScraping` in your python environment.
3. From inside the directory `LinkedinScraping` run the following:
```
pip install -r requirements.txt
```
 
When the installation ends, open the directory `LinkedinScraping` and run the `configurator.py` following the instructions.
If it's the first time, set the configuration as suggested by the messages that will be printed by the configurator.
In any time in the future you can easily re-run the configuration to change for example name of input / output files or delimiters.

I understand the request for LinkedIn username and password could be scary, unfortunately it is necessary. I can guarantee you such information is stored only locally: no personal data is sent to me or anywhere else, except obviously to the Linkedin page to perform the login. You are free to check the code to be sure of this.

## Executing

Every time you execute a scraping, a new Google Chrome window will be opened. **Please don't lose the focus on it.**

You can leave alone the computer but be sure it won't enter sleep mode (for MacOS: [Amphetamine](https://apps.apple.com/it/app/amphetamine/id937984704?mt=12)).

If for any reason the computer enter sleep mode, or you loose the focus on the window, the script will keep on but won't scrap any data. Hence, be really carefull if at the end of the scraping process you end up with profiles that seem to have no data: it may have been this case.

### Human Check by LinkedIn ###

If you scrape consequentially a lot of profiles (hundreds) and especially during not common hours time, LinkedIn may prompt you a Captcha to check you are not a bot. No panic! The script will detect it (please wait for it) and will ask you loud (**check your speakers are on**) to perform the check.

After you complete the check, check that you are viewing the page at `https://www.linkedin.com/feed/`. If not, please immediatly navigate there. The script will detect it and will restart. No data should be loss.


## Running Scraping by Profile URL

Open the file `profiles_data.txt` and insert the URLs of the LinkedIn profiles you want to do the scraping.

**Notice:** Each line must contain **only one** URL

If you want also the graduation statistics, append to the url the graduation date with format DD/MM/YY, using the `:::` delimiter.

Run `scrap_profiles.py`.

### Examples

Only LinkedIn URL:
```
https://www.linkedin.com/in/federicohaag/
https://www.linkedin.com/in/someoneelse/
```

LinkedIn URL and KnownGraduationDate:
```
https://www.linkedin.com/in/federicohaag/:::01/10/2018
https://www.linkedin.com/in/someoneelse/:::01/10/2018
```

When the Chrome page closes, it means the program ended.
You can find inside the `LinkedInScraping` folder the extracted data in the results file `results_profiles.xlsx`.
The file name will contain concatenated the current timestamp if the configuration was set as suggested.

## Running Search for profile url by name

Open the input file `profiles_names.txt` and insert data as follows:
```
FirstName:::LastName:::KnownUniversity:::KnownCourse:::KnownGraduationDate
```

Run `scrap_profiles_by_name.py`.

### Input structure:
* `FirstName` and `LastName` are required. If not provided the code will break.
* `KnownUniversity` [optional] can be a single name or a sequence of names using `,` as delimiter.
* `KnownCourse` [optional] can be a single name or a sequence of names using `,` as delimiter.
* `KnownGraduationDate` [optional] has to be formatted as DD/MM/YY.

The script will do its best to find a LinkedIn Profile that is consistent with the specified information.

**Notice:** The optional parameters has to be inserted in order. This means that you can insert in a row just `FirstName:::LastName`, you can insert just `FirstName:::LastName:::KnownUniversity`, but you can not insert something like `FirstName:::LastName:::KnownCourse`.

### Example:
Let's say you want to look for Federico Haag profile, you know he is a student of Politecnico di Milano but you don't know if he studies computer science or management engineering. You also know he graduated around the 01/10/2018 (only the year is relevant).
Here is what guarantee you the best match.
```
Federico:::Haag:::Politecnico di Milano:::Computer Science,Management:::01/10/2018
```

### Results schema:
* **Education Checked** is `TRUE` if the university & course information of the found LinkedIn Profile are consistent with the provided ones.
* **Checked Status** can be `GRAD_CHECKED` if the graduation year of the found LinkedIn Profile is consistent with the provided one, `NO_GRAD_CHECK` otherwise.

## Common problems in Running

Running for the first time one of the two py scripts you may get an error message similar to the following:
```selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary```.
If this happens, please replace the code lines containing:
```
browser = webdriver.Chrome(executable_path=config.get('system', 'driver'))
```
with the following:
```
options = webdriver.ChromeOptions()
options.binary_location = r"<YOUR_CHROME_PATH>\chrome.exe" 
browser = webdriver.Chrome(executable_path=config.get('system', 'driver'), chrome_options=options)
```
Please consider that `<YOUR_CHROME_PATH>` has to be replaced with the actual path to your chrome.exe executable in Windows or the chrome folder in Linux.

## Customizing

You can customize the configurations easily re-running `configurator.py`.

You can also customize the code in many ways:
*The easy one is changing the order how the data is inserted in the excel file, or renaming the excel file headers.
*The harder one is to do scraping of additional data: have a look at the Acknowledgments down here or feel free to reach me out to propose new code.

## Authors

* **Federico Haag** - [LinkedIn](https://www.linkedin.com/in/federicohaag/) - [Medium](https://medium.com/@federicohaag)

## Acknowledgments

* Inspired by: [Repository Link](https://github.com/laxmimerit/LinkedIn-Profile-Scrapper-in-Python)

## Disclaimer

The repository is intended to be used as a reference to learn more on Python and to perform scraping for personal usage. Every country has different and special regulations on usage of personal information, so I strongly recommend you to check your national legislation before using / sharing / selling / elaborating the scraped information. I decline any responsibility on the usage of scraped information. Cloning this repository and executing the included scripts you declare and confirm the responsibility of the scraped data usage is totally up on you.
