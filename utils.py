import json
import re
import time


class AuthenticationException(Exception):
    """"""
    pass


class ScrapingException(Exception):
    """"""
    pass


class HumanCheckException(Exception):
    """Human Check from Linkedin"""
    pass


class CannotProceedScrapingException(Exception):
    """Human Check from Linkedin during an headless mode execution"""
    pass


class Location:
    def __init__(self, location: str):
        self.location = location
        self.city = ''
        self.country = ''

        if ',' in location:
            try:
                self.city = location.split(',')[0].strip()
                self.country = location.split(',')[-1].strip()
            except:
                pass

    def reprJSON(self):
        return dict(location=self.location, city=self.city, country=self.country)


class Company:
    def __init__(self, name: str, industry: str, employees: str):
        self.name = name
        self.industry = industry
        self.employees = employees

    def reprJSON(self):
        return dict(name=self.name, industry=self.industry, employees=self.employees)


class Job:
    def __init__(self, position: str, company: Company, location: Location, date_range: str):
        self.position = position
        self.company = company
        self.location = location
        self.date_range = date_range

    def reprJSON(self):
        return dict(position=self.position, company=self.company, location=self.location, date_range=self.date_range)


class Profile:
    def __init__(self, name: str, email: str, skills: [str], jobs: [Job]):
        self.name = name
        self.email = email
        self.skills = skills
        self.jobs = jobs

    def reprJSON(self):
        return dict(name=self.name, email=self.email, skills=self.skills, jobs=self.jobs)


class ScrapingResult:
    def __init__(self, linkedin_url: str, profile: Profile):
        self.linkedin_url = linkedin_url
        self.profile = profile

    def reprJSON(self):
        return dict(linkedin_url=self.linkedin_url, profile=self.profile)

    def is_error(self):
        return self.profile is None

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


def is_url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def get_months_between_dates(date1, date2):
    if date1 < date2:
        diff = date2 - date1
    elif date1 > date2:
        diff = date1 - date2
    else:
        return 0

    return diff.days // 30


def wait_for_loading():
    time.sleep(2)


def wait_for_scrolling():
    time.sleep(1)
