import datetime


def parseDate(train_date):
    week_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    month_name = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    y, m, d = map(int, train_date.split("-"))
    weekday = datetime.datetime(y, m, d).weekday()
    # Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
    return "{0} {1} {2} {3} 00:00:00 GMT+0800 (中国标准时间)".format(week_name[weekday], month_name[m - 1], d, y)
