# LinkedIn Scraping with Python

Creates an Excel file containing personal data and last job position of specified people.

If you know the graduation date of the person, you can also specify it in the input file to obtain statistics about how fast he/she got a job after graduation.

Scraping can be currently done only providing the LinkedIn profile url of the target person. If you dont have yet the LinkedIn profile url, you can make it to be searched automatically (see below).

Doubts? Reach me out on [LinkedIn](https://www.linkedin.com/in/federicohaag/).

If this code solves you a real problem, I would be grateful if you would consider a donation to enable me in keep on developing such codes. [Donate here](https://www.paypal.me/FedericoHaag).

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
 4. Run `LinkedinScraping\configurator.py` following the prompted instructions.
 

If it's the first time, set the configuration as suggested by the messages that will be printed by the configurator.
In any time in the future you can easily re-run the configuration to change for example name of input / output files or delimiters.

I understand the request for LinkedIn username and password could be scary, unfortunately it is necessary. I can guarantee you such information is stored only locally: no personal data is sent to me or anywhere else, except obviously to the Linkedin page to perform the login. You are free to check the code to be sure of this.

## Executing

There are two ways you can run the code: headless execution and normal one.

In both cases, be careful (especially when you scrap a lot of profiles) because your computer may enter sleep mode. In sleep mode the scraping could not work. For MacOS I suggest [Amphetamine](https://apps.apple.com/it/app/amphetamine/id937984704?mt=12).

### Headless execution
In this mode the script will do scraping without opening a real Chrome window.

**Pros:** In this way you can keep on doing your regular business on your computer.

**Cons:** If you scrap many profiles (more than hundreds) and/or in unusual times (in the night) LinkedIn may prompt a Captcha to check that you are not a human. If this happens, there is no way for you to fill in the Captcha and all the work done by the script will be wasted as the only way out is to kill the python process.

To run in headless mode:
```
python scrap_profiles.py HEADLESS
```

### Normal execution
In this mode the script will do scraping opening a real Chrome window.

**Pros:** In this case you will be able - if prompted - to satisfy the Captcha check and to proceed the scraping. The python script is trained on this situation and will perfectly manage it alerting you.

**Cons:** Be aware that if you choose this mode you can not loose the focus on the window, otherwise no data will be scraped.

To run in normal mode:
```
python scrap_profiles.py
```

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

### Selenium WebDriverException
In case you get an error message similar to the following:
```
selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary
```
please run again `configurator.py` and be sure to specify a correct path to your chrome.exe executable in Windows or the chrome folder in Linux.

### Human check freezing the scraping
It may happen that while scraping the script will warn you about the need to perform a Human Check (a Google Captcha) even if it's not prompted for real.

This happens when you inserted in the input file a Profile URL which is not correctly formatted.

Here some tips:
* The profile URL should always end with `/`
* Open a browser window and navigate to such URL. Wait for the page to load. Is the URL currently in the browser navigation bar the same as the one you initially inserted? If not, you should insert in the input file the one you see now at the navigation bar.

## Customizing

You can customize the configurations easily re-running `configurator.py`.

You can also customize the code in many ways:
*The easy one is changing the order how the data is inserted in the excel file, or renaming the excel file headers.
*The harder one is to do scraping of additional data: have a look at the Acknowledgments down here or feel free to reach me out to propose new code.

## Authors

* **Federico Haag** - [LinkedIn](https://www.linkedin.com/in/federicohaag/) - [Medium](https://medium.com/@federicohaag)

If this code solves you a real problem, I would be grateful if you would consider a donation to enable me in keep on developing such codes. [Donate here](https://www.paypal.me/FedericoHaag).

## Acknowledgments

* Inspired by: [Repository Link](https://github.com/laxmimerit/LinkedIn-Profile-Scrapper-in-Python)

## Disclaimer

The repository is intended to be used as a reference to learn more on Python and to perform scraping for personal usage. Every country has different and special regulations on usage of personal information, so I strongly recommend you to check your national legislation before using / sharing / selling / elaborating the scraped information. I decline any responsibility on the usage of scraped information. Cloning this repository and executing the included scripts you declare and confirm the responsibility of the scraped data usage is totally up on you.
