import datetime


def age(dob):
    today = datetime.date.today()
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        return today.year - dob.year - 1
    return today.year - dob.year
