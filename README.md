# LinkedIn Scraping with Python

Creates an Excel file containing: personal data and last job position.

If you know the graduation date of the person, you can also specify it in the input file to obtain statistics about how fast he/she got a job after graduation.
Scraping can be done only providing LinkedIn profile url of the target person.
If the LinkedIn profile url is unknown to you, you can make it to be searched automatically (see below).

Doubts? Reach me out on Linkedin. Find contact info at the end of the README.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You must have installed in your machine:
* Google Chrome v.80
* Python 3.8


### Installing

1. Download the whole repository.
2. Place the directory `LinkedinScraping` in your python environment.
3. From inside the directory `LinkedinScraping` run the following:
```
pip install -r requirements.txt
```
 
When the installation ends, open the directory `LinkedinScraping` and run the `configurator.py` following the instructions.
If it's the first time, set the configuration as suggested by the messages that will be printed by the configurator.
In any time in the future you can easily re-run the configuration to change name of files or delimiters.

I understand the request for LinkedIn username and password could be scary, unfortunately it is necessary. However such information are stored only locally. No personal data is sent to me or anywhere else, except to the Linkedin page to perform the login. Obviously you are free to check the code to be sure of this.

## Running

Open the file `profiles_data.txt`.
Insert the URLs of the LinkedIn profiles you want to do the scraping.
For example:
```
https://www.linkedin.com/in/federicohaag/
https://www.linkedin.com/in/someoneelse/
```
**Notice:** Each line must contain **only one** URL

If you want also the graduation statistics, append to the url the graduation date with format DD/MM/YY, using the `:::` delimiter.
For example:
```
https://www.linkedin.com/in/federicohaag/:::01/10/2018
https://www.linkedin.com/in/someoneelse/:::01/10/2018
```

Run `scrap_profiles.py`.

**Important:** A new Google Chrome window will be opened. Please don't lose the focus on it. You can leave the computer but be sure it won't go to sleep mode (for MacOS: [Amphetamine](https://apps.apple.com/it/app/amphetamine/id937984704?mt=12)).

When the Chrome page closes, it means the program ended.
You can find inside the `LinkedInScraping` folder the extracted data in the results file `results_profiles.xlsx`.
The file name will contain concatenated the current timestamp if the configuration was set as suggested.

## Search for profile url by name

Open the input file `profiles_names.txt` and insert data as follows:
`FirstName:::LastName:::KnownGraduationDate`
You can customize the delimiter.
At the moment is not possible to perform a research without specifying the `KnownGraduationDate`. I understand this could be a limit. As soon as possible I will make it optional.

Run `scrap_profiles_by_name.py`.

You can find inside the `LinkedInScraping` folder the extracted data in the results file `results_profiles_by_name.xlsx`.
The file name will contain concatenated the current timestamp if the configuration was set as suggested.

## Customizing

You can customize the configurations easily re-running `configurator.py`.

You can also customize the code in many ways.

The easy one is changing the order how the data is inserted in the excel file, or renaming the excel file headers.

The harder one is to do scraping of additional data: have a look at the Acknowledgments down here or feel free to reach me out to propose new code.

## Authors

* **Federico Haag** - [LinkedIn](https://www.linkedin.com/in/federicohaag/) - [Medium](https://medium.com/@federicohaag)

## Acknowledgments

* Inspired by: [Repository Link](https://github.com/laxmimerit/LinkedIn-Profile-Scrapper-in-Python)

