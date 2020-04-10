import datetime

from utils_dates import split_date_range


class JobHistorySummary:
    def __init__(self, graduation_date=None, job_positions_data_ranges=None, job_experiences=None):

        self.had_job_while_studying = False
        self.had_job_after_graduation_within_3_months = False
        self.had_job_after_graduation_within_5_months = False
        self.had_job_after_graduation_within_6_months = False
        self.date_first_job_after_beginning_university = None
        self.date_first_job_after_ending_university = None
        self.first_job_ever_date = None
        self.jobs_now = 0

        if job_experiences is None:
            job_experiences = []

        if job_positions_data_ranges is None:
            job_positions_data_ranges = []

        for job_experience in job_experiences:
            found_present = False
            for d_range in job_experience.find_elements_by_class_name('pv-entity__date-range'):
                found_present = found_present or ('present' in d_range.text.lower())

            self.jobs_now += 1 if found_present else 0

        if graduation_date is not None and len(job_positions_data_ranges) > 0:

            beginning_of_university = datetime.fromtimestamp(
                datetime.timestamp(graduation_date) - 24 * 60 * 60 * 365 * 2)
            three_months_after_graduation_date = datetime.fromtimestamp(
                datetime.timestamp(graduation_date) + 24 * 60 * 60 * 365 * (3 / 12))
            five_months_after_graduation_date = datetime.fromtimestamp(
                datetime.timestamp(graduation_date) + 24 * 60 * 60 * 365 * (5 / 12))
            six_months_after_graduation_date = datetime.fromtimestamp(
                datetime.timestamp(graduation_date) + 24 * 60 * 60 * 365 * (6 / 12))

            for date_range in job_positions_data_ranges:

                # Split the date range into the two initial and ending date
                initial_date, end_date = split_date_range(date_range)
                end_date = datetime.fromtimestamp(datetime.timestamp(end_date) + 24 * 60 * 60 * 31)

                if self.first_job_ever_date is None:
                    self.first_job_ever_date = initial_date
                else:
                    if initial_date < self.first_job_ever_date:
                        self.first_job_ever_date = initial_date

                # Checking if was working while studying
                if beginning_of_university <= initial_date <= graduation_date:
                    self.had_job_while_studying = True

                if initial_date >= beginning_of_university:

                    if self.date_first_job_after_beginning_university is None:
                        self.date_first_job_after_beginning_university = initial_date
                    else:
                        if initial_date < self.date_first_job_after_beginning_university:
                            self.date_first_job_after_beginning_university = initial_date

                if initial_date <= graduation_date <= end_date:
                    self.had_job_after_graduation = True

                if initial_date > graduation_date:
                    if self.date_first_job_after_ending_university is None:
                        self.date_first_job_after_ending_university = initial_date
                    else:
                        if initial_date < self.date_first_job_after_ending_university:
                            self.date_first_job_after_ending_university = initial_date

                if initial_date <= three_months_after_graduation_date <= end_date:
                    self.had_job_after_graduation_within_3_months = True

                if initial_date <= five_months_after_graduation_date <= end_date:
                    self.had_job_after_graduation_within_5_months = True

                if initial_date <= six_months_after_graduation_date <= end_date:
                    self.had_job_after_graduation_within_6_months = True

        self.more_than_a_job_now = self.jobs_now > 1
        self.is_currently_unemployed = self.jobs_now == 0

        self.never_had_jobs = len(job_experiences) == 0
