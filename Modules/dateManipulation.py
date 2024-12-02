from datetime import datetime, date, timedelta

def is_month(string):
    try:
        datetime.strptime(string, "%B")
        return True
    except ValueError:
        return False

def find_next_month(current_month):
    # Parsing the input month string to a datetime object
    current_date = datetime.strptime(current_month, "%B")

    # Adding one month to the current date
    next_month_date = current_date + timedelta(days=31)

    # Formatting the next month as a string
    next_month = next_month_date.strftime("%B")

    return next_month

def find_last_month(current_month):
    # Parsing the input month string to a datetime object
    current_date = datetime.strptime(current_month, "%B")

    # Subtracting one month from the current date
    last_month_date = current_date - timedelta(days=31)

    # Formatting the last month as a string
    last_month = last_month_date.strftime("%B")

    return last_month

def eliminateSufixes(dates):
    for sufix in ["st","nd","th","rd"]:
        for date in range(len(dates)):
            dateParts = dates[date].split()
            for unit in range(len(dateParts)):
                if dateParts[unit][0].isdigit():
                    dateParts[unit] = dateParts[unit].replace(sufix,"")
            dates[date] = " ".join(dateParts)
    return dates

def parseDate(date):
    date = date.split(" ")
    toret = {}

    for i in date:
        if i.isnumeric() and int(i) <= 31:
            toret["day"] = int(i)

        elif is_month(i):
            toret["month"] = i

        elif i.isnumeric() and int(i) >= 2021:
            toret["year"] = int(i)
    return toret

def filldates(start,end):

    if "day" not in start and "day" not in end:
        print("Problem; no days")

    if "month" not in start or "month" not in end:

        if "month" not in start and "month" not in end:
            print("Problem; no months")

        elif "month" not in start:
            if end["day"] >= start["day"]:
                start["month"] = end["month"]
            else:
                start["month"] = find_last_month(end["month"])


        elif "month" not in end:
            if end["day"] >= start["day"]:
                end["month"] = start["month"]
            else:
                end["month"] = find_next_month(start["month"])


    if "year" not in start or "year" not in end:
        monthStart = datetime.strptime(start["month"], "%B").month
        monthEnd = datetime.strptime(end["month"], "%B").month

        if "year" not in start and "year" not in end:
            # We have to put something so it doesn"t fail
            start["year"] = 2000
            end["year"] = 2000
            print("Problem; no year")

        elif "year" not in start:
            if monthEnd >= monthStart:
                start["year"] = end["year"]
            else:
                start["year"] = end["year"]-1

        elif "year" not in end:
            if monthEnd >= monthStart:
                end["year"] = start["year"]
            else:
                end["year"] = start["year"]+1

    return start,end

def formattingDates(release_dates):
    formattedDates = []
    for date_range in release_dates:

        if len(date_range.split(" - ")) == 1:
            start = date_range.split(" - ")[0]
            formattedStart = datetime.strptime(start, "%B %d %Y")
            formattedStart = formattedStart.strftime("%Y-%m-%d")
            formattedEnd = formattedStart

        else:
            start = date_range.split(" - ")[0]
            end = date_range.split(" - ")[1]

            start = parseDate(start)
            end = parseDate(end)

            start,end = filldates(start,end)

            formattedStart = "{month} {day} {year}".format(year=start["year"], month=start["month"], day=start["day"])
            formattedStart = datetime.strptime(formattedStart, "%B %d %Y")
            formattedStart = formattedStart.strftime("%Y-%m-%d")

            formattedEnd = "{month} {day} {year}".format(year=end["year"], month=end["month"], day=end["day"])
            formattedEnd = datetime.strptime(formattedEnd, "%B %d %Y")
            formattedEnd = formattedEnd.strftime("%Y-%m-%d")

        formattedDates.append({"start":formattedStart,"end":formattedEnd})

    return formattedDates
