from datetime import datetime
import pytz

def run(real_stream):
    '''
    Return current day of week
    '''
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    utc = pytz.UTC
    ret_value = WEEKDAYS[datetime.utcnow().replace(tzinfo=utc).weekday()]
    return(True, ret_value)