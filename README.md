# LinkedIn Scraping with Python

Creates automatically an Excel file containing the personal data and the last job position of all the provided LinkedIn profiles.

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
 
When the installation ends, open the directory `LinkedinScraping` and follow the instructions based on your OS:

#### MacOS
1. Rename the file `configs-mac.txt` into `configs.txt`
2. Open such file and overwrite `username` with your LinkedIn username, and overwrite `password` with your LinkedIn password
3. Save & Close the file
#### Windows
1. Rename the file `configs-windows.txt` into `configs.txt`
2. Open such file and overwrite `username` with your LinkedIn username, and overwrite `password` with your LinkedIn password
3. Save & Close the file
#### Linux
1. Rename the file `configs-linux.txt` into `configs.txt`
2. Open such file and overwrite `username` with your LinkedIn username, and overwrite `password` with your LinkedIn password
3. Save & Close the file


## Running

Open the `profiles.txt` file and insert the URLs of the LinkedIn profiles you want to do the scraping.
For example:
```
https://www.linkedin.com/in/federicohaag/
https://www.linkedin.com/in/someoneelse/
```
**Notice:** Each line must contain **only one** URL

Run `app.py`.

**Important:** A new Google Chrome window will be opened. Please don't lose the focus on it. You can leave the computer but be sure it won't go to sleep mode (for MacOS: [Amphetamine](https://apps.apple.com/it/app/amphetamine/id937984704?mt=12)).

When the Chrome page closes, it means the program ended and you can find the extracted data in the file `results.xlsx`, inside the `LinkedInScraping` folder.

## Customizing

You can customize the code in many ways.

The easy one is changing the order how the data is inserted in the excel file, or renaming the excel file headers.

The harder one is to do scraping of additional data: have a look at the Acknowledgments down here or feel free to reach me out to propose new code.

## Authors

* **Federico Haag** - [LinkedIn](https://www.linkedin.com/in/federicohaag/) - [Medium](https://medium.com/@federicohaag)

## Acknowledgments

* Inspired by: [Repository Link](https://github.com/laxmimerit/LinkedIn-Profile-Scrapper-in-Python)

