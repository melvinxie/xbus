from bisect import bisect_left
from django.utils import simplejson
from google.appengine.ext import db

def get_day(now):
    # TODO: JP holidays
    if (now.month == 8 and 14 <= now.day <= 16 or
        now.month == 12 and now.day >= 29 or
        now.month == 1 and now.day <= 4 or
        now.weekday == 6):
        return 'holiday'
    elif now.weekday == 5:
        return 'saturday'
    else:
        return 'weekday'

def duration(start, end):
    return divmod(end[0] * 60 + end[1] - start[0] * 60 - start[1], 60)

class TimeTable(db.Model):
    station_id = db.IntegerProperty()
    route_key = db.StringProperty()
    name = db.StringProperty()
    content = db.TextProperty()

    @property
    def timetable(self):
        try:
            return getattr(self, 'cached_timetable')
        except AttributeError:
            value = simplejson.loads(self.content)
            setattr(self, 'cached_timetable', value)
            return value

    def time_list(self, day):
        time_list = []
        for h, minutes in self.timetable[day].iteritems():
            hour = int(h)
            for minute in minutes:
                time_list.append((hour, minute))
        return sorted(time_list)

    def next_time(self, now, day):
        time_list = self.time_list(day)
        try:
            return time_list[bisect_left(time_list, (now.hour, now.minute))]
        except IndexError:
            pass

"""
    # Test only
    @classmethod
    def get_by_key_name(cls, key_name):
        t = {"holiday": {"11": [3, 23, 43], "10": [3, 23, 43], "13": [3, 23,
            43], "12": [3, 23, 43], "15": [3, 23, 43], "14": [3, 23, 43], "17":
            [3, 23, 43], "16": [3, 23, 43], "19": [3, 21, 39, 58], "18": [3, 23,
                43], "22": [17, 42], "23": [5], "20": [18, 38, 58], "7": [22,
                    57], "6": [46], "9": [21, 43], "8": [27, 58], "21": [17, 34,
                        52]}, "weekday": {"11": [8, 23, 38, 53], "10": [8, 23,
                            38, 53], "13": [8, 23, 38, 53], "12": [8, 23, 38,
                                53], "15": [8, 23, 38, 53], "14": [8, 23, 38,
                                    53], "17": [8, 23, 38, 53], "16": [8, 23,
                                        38, 53], "19": [3, 21, 39, 58], "18":
                                    [8, 23, 43], "22": [17, 42], "23": [5],
                                    "20": [18, 38, 58], "7": [6, 23, 37, 52],
                                    "6": [46], "9": [9, 20, 32, 44, 56], "8":
                                    [5, 18, 30, 39, 49, 59], "21": [17, 34,
                                        52]}, "saturday": {"11": [3, 23, 43],
                                            "10": [3, 23, 43], "13": [3, 23,
                                                43], "12": [3, 23, 43], "15":
                                            [3, 23, 43], "14": [3, 23, 43],
                                            "17": [3, 23, 43], "16": [3, 23,
                                                43], "19": [3, 21, 39, 58],
                                            "18": [3, 23, 43], "22": [17, 42],
                                            "23": [5], "20": [18, 38, 58], "7":
                                            [17, 37, 57], "6": [46], "9": [3,
                                                21, 43], "8": [12, 27, 45],
                                            "21": [17, 34, 52]}}
        return TimeTable(name='Test', content=simplejson.dumps(t))
    """
