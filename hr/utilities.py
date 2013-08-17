from __future__ import division
import locale, datetime, traceback

# eventually make this more dynamic
def convert_to_usd_money(currency, money):
    if currency == 'usd':
        return money
    if currency == 'eur':
        return money * 1.32
    if currency == 'gdp':
        return money * 1.62
    if currency == 'cny':
        return money * .16
    if currency == 'brl':
        return money * .49
    if currency == 'hkd':
        return money * .13
    if currency == 'sgd':
        return money * .82
    if currency == 'cad':
        return money
    if currency == 'nzd':
        return money * .82
    if currency == 'aud':
        return money * 1.04

    return money


def money_formatted(currency, money):
    unknown_currency = False

    if (currency == 'usd'):
        locale.setlocale(locale.LC_ALL, 'en_US')
    elif (currency == 'eur'):
        locale.setlocale(locale.LC_ALL, 'fr_FR')
    elif (currency == 'gbp'):
        locale.setlocale(locale.LC_ALL, 'en-GB')
    elif (currency == 'cny'):
        locale.setlocale(locale.LC_ALL, 'zh-CN')
    elif (currency == 'brl'):
        locale.setlocale(locale.LC_ALL, 'pt-BR')
    elif (currency == 'hkd'):
        locale.setlocale(locale.LC_ALL, 'zh-HK')
    elif (currency == 'sgd'):
        locale.setlocale(locale.LC_ALL, 'zh-SG')
    elif (currency == 'cad'):
        locale.setlocale(locale.LC_ALL, 'en-CA')
    elif (currency == 'nzd'):
        locale.setlocale(locale.LC_ALL, 'en-NZ')
    elif (currency == 'aud'):
        locale.setlocale(locale.LC_ALL, 'en-AU')
    else:
        unknown_currency = True
        locale.setlocale(locale.LC_ALL, 'en_US')

    rf = locale.currency(money, grouping=True) + " " + currency.upper()

    if unknown_currency:
        rf = rf[1:]

    return rf


def money_formatted_micro(currency, money):
    rf = money_formatted(currency, money)
    return rf[:-7]


def quarterly_start_date(year, quarter):
    if quarter == 1:
        return datetime.datetime(int(year), 1, 1)
    if quarter == 2:
        return datetime.datetime(int(year), 4, 1)
    if quarter == 3:
        return datetime.datetime(int(year), 7, 1)
    if quarter == 4:
        return datetime.datetime(int(year), 10, 1)


def quarterly_end_date(year, quarter):
    if quarter == 1:
        return datetime.datetime(int(year), 4, 1)
    if quarter == 2:
        return datetime.datetime(int(year), 7, 1)
    if quarter == 3:
        return datetime.datetime(int(year), 10, 1)
    if quarter == 4:
        return datetime.datetime(int(year) + 1, 1, 1)


def monthly_start_date(year, month):
    return datetime.datetime(int(year), month, 1)


def monthly_end_date(year, month):
    month = month + 1
    #if month == 4 or month == 9 or month == 6 or month == 11:
    #    return datetime.datetime(int(year),month,1)
    #elif month == 2:
    #    if year == 2012 or year == 2016 or year == 2020:
    #        return datetime.datetime(int(year),month,1)
    #    else:
    #        return datetime.datetime(int(year),month,1)
    if month == 13:
        return datetime.datetime(int(year) + 1, 1, 1)
    else:
        return datetime.datetime(int(year), month, 1)


def revised_end_date(end_date):
    if end_date.day == 1:
        return end_date

    if end_date.month == 12 and end_date.day == 31:
        return datetime.datetime(end_date.year + 1, 1, 1)
    if end_date.day == 30 and (
                    end_date.month == 4 or end_date.month == 6 or end_date.month == 9 or end_date.month == 11):
        return datetime.datetime(end_date.year, end_date.month + 1, 1)
    if end_date.month == 2 and (
                end_date.year == 2012 or end_date.year == 2016 or end_date.year == 2020) and end_date.day == 29:
        return datetime.datetime(end_date.year, 3, 1)
    if end_date.month == 2 and end_date.day == 28:
        return datetime.datetime(end_date.year, 3, 1)
    if end_date.day == 31:
        return datetime.datetime(end_date.year, end_date.month + 1, 1)
    return datetime.datetime(end_date.year, end_date.month, end_date.day + 1)


def utilization_per_month(year, month, start_date, end_date, utilization_over_period):
    end_date = revised_end_date(end_date)

    length = 0
    if start_date < monthly_start_date(year, month):
        if end_date >= monthly_end_date(year, month):
            length = abs((monthly_end_date(year, month) - monthly_start_date(year, month)).days)
        elif end_date > monthly_start_date(year, month):
            length = abs((end_date - monthly_start_date(year, month)).days)
    elif start_date < monthly_end_date(year, month):
        if end_date >= monthly_end_date(year, month):
            length = abs((monthly_end_date(year, month) - start_date).days)
        elif end_date > monthly_start_date(year, month):
            length = abs((end_date.date() - start_date.date()).days)
    if length == abs((monthly_end_date(year, month) - monthly_start_date(year, month)).days):
        return utilization_over_period
    elif length == 0:
        return 0
    else:
        monthly_length = abs((monthly_end_date(year, month) - monthly_start_date(year, month)).days)
        return (length / monthly_length) * utilization_over_period


def days_employed_per_year(year, start_date, end_date):
    end_date = revised_end_date(end_date)

    start_year = datetime.datetime(int(year), 1, 1)
    end_year = datetime.datetime(int(year) + 1, 1, 1)
    if start_date < start_year:
        if end_date is None or end_date > end_year:
            return abs((end_year - start_year).days)
        else:
            return abs((end_date - start_year).days)
    else:
        if end_date is None or end_date > end_year:
            return abs((end_year - start_date).days)
        else:
            return abs((end_date - start_date).days)


def quarterly_salary(year, user, start_date, end_date, kind="total", allocation=100):
    end_date = revised_end_date(end_date)

    salary_per_quarter = [0, 0, 0, 0]

    salary_per_day = []
    day_counter = datetime.datetime(int(year), 1, 1)

    year_length = 365
    if year == 2012 or year == 2016 or year == 2020:
        year_length = 366

    for x in range(0, year_length):
        if day_counter >= start_date and day_counter < end_date:
            latest_date = None
            temp_salary = 0
            for salary in user.salary_history:
                if ((latest_date is None or salary.start_date >= latest_date) and salary.start_date <= day_counter):
                    latest_date = salary.start_date
                    if kind == "total":
                        temp_salary = salary.salary * (1 + user.account.benefits_and_bonus / 100) * (allocation / 100)
                    elif kind == "billable":
                        temp_salary = salary.salary * (1 + user.account.benefits_and_bonus / 100) * (
                        salary.percent_billable / 100)
                    elif kind == "non-billable":
                        temp_salary = salary.salary * (1 + user.account.benefits_and_bonus / 100) * (
                        (100 - salary.percent_billable) / 100)
            salary_per_day.append(temp_salary / year_length)
        else:
            salary_per_day.append(0)

        day_counter += datetime.timedelta(days=1)

    # fix this for correct number of days per quarter... factoring in leap year
    if year == 2012 or year == 2016 or year == 2020:
        for x in range(0, 91):
            salary_per_quarter[0] += salary_per_day[x]
        for x in range(91, 181):
            salary_per_quarter[1] += salary_per_day[x]
        for x in range(181, 274):
            salary_per_quarter[2] += salary_per_day[x]
        for x in range(274, 366):
            salary_per_quarter[3] += salary_per_day[x]

    else:
        for x in range(0, 90):
            salary_per_quarter[0] += salary_per_day[x]
        for x in range(90, 180):
            salary_per_quarter[1] += salary_per_day[x]
        for x in range(180, 273):
            salary_per_quarter[2] += salary_per_day[x]
        for x in range(273, 365):
            salary_per_quarter[3] += salary_per_day[x]

    return salary_per_quarter


def quarterly_money(year, start_date, end_date, money_per_day, actuals=None, kind=None):
    end_date = revised_end_date(end_date)

    money_per_quarter = [0, 0, 0, 0]
    is_actual = [0, 0, 0, 0]
    y = 0
    days_lost = 0

    if actuals == []:
        actuals = None

    for x in range(1, 5):
        try:
            length = 0

            if actuals is not None:
                for actual in actuals:
                    if actual.quarter_end_date == quarterly_end_date(year, x):
                        money_per_quarter[y] = actual.revenue
                        is_actual[y] = actual.revenue
                        if y > 0 and is_actual[0] == 0:
                            money_per_quarter[0] = 0
                        if y > 1 and is_actual[1] == 0:
                            money_per_quarter[1] = 0
                        if y > 2 and is_actual[2] == 0:
                            money_per_quarter[2] = 0

                            #days_lost = days_lost + 1

            is_the_past = False
            if kind is not None and kind.startswith('ghost'):
                if start_date < datetime.datetime.now():
                    start_date = datetime.datetime.now()
                    is_the_past = True

            if start_date > end_date:
                length = 0
            elif start_date < quarterly_start_date(year, x):
                if end_date > quarterly_end_date(year, x):
                    #length = abs((quarterly_end_date(year,x) - quarterly_start_date(year,x)).days) + 1
                    length = abs((quarterly_end_date(year, x) - quarterly_start_date(year, x)).days)
                elif end_date == quarterly_end_date(year, x):
                    length = abs((quarterly_end_date(year, x) - quarterly_start_date(year, x)).days)
                elif end_date > quarterly_start_date(year, x):
                    length = abs((end_date - quarterly_start_date(year, x)).days)
            elif start_date < quarterly_end_date(year, x):
                if end_date > quarterly_end_date(year, x):
                # length = abs((quarterly_end_date(year,x) - start_date).days) + 1
                    length = abs((quarterly_end_date(year, x) - start_date).days)
                elif end_date == quarterly_end_date(year, x):
                    length = abs((quarterly_end_date(year, x) - start_date).days)
                elif end_date > quarterly_start_date(year, x):
                    length = abs((end_date.date() - start_date.date()).days)

            #if kind is not None and kind.endswith("salary") and y == 0 and is_the_past == False:
            #    days_lost = 1
            if money_per_quarter[y] == 0:
                #money_per_quarter[y] = (length + days_lost) * money_per_day
                #days_lost = 0
                money_per_quarter[y] = (length + days_lost) * money_per_day

            y = y + 1
        except:
            traceback.print_exc()
            money_per_quarter[y] = 0
            y = y + 1

    return money_per_quarter