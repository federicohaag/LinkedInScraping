import datetime


def split_date_range(date_range):
    try:
        dates = date_range.split(' – ')
        begin = parse_date(dates[0])
        end = parse_date(dates[1])
    except IndexError:
        begin = parse_date(date_range.strip())
        end = begin

    return [begin, end]


def parse_date(date_str):
    if date_str == 'Present':
        return datetime.today()

    try:
        date = datetime.strptime(date_str, '%b %Y')
        return date
    except ValueError:
        try:
            date = datetime.strptime(date_str, '%Y')
            return date
        except ValueError:
            return None