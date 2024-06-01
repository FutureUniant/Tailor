import time
import datetime


class Timer:
    @classmethod
    def get_timestamp(cls, integer=True, string=True):
        timestamp = time.time()
        if integer:
            timestamp = int(timestamp)
        if string:
            timestamp = str(timestamp)
        return timestamp

    @classmethod
    def get_format_time(cls, format="%Y%m%d%H%M%S"):
        curr_time = datetime.datetime.now()
        timestamp = datetime.datetime.strftime(curr_time, format)
        return str(timestamp)


# _FORMAT_TIME = Timer.get_format_time()
# _TIMESTAMP = Timer.get_timestamp(integer=False, string=False)
# _TIMESTAMP_INT = Timer.get_timestamp(integer=True, string=False)
# _TIMESTAMP_STR = Timer.get_timestamp()
