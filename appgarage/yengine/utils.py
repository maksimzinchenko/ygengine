import requests, importlib
from datetime import datetime

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from appgarage.settings import MEDIA_FOLDER


def is_valid_url(url):
        '''Method for testing if string is valid URL'''
        val = URLValidator()
        try:
            val(url)
        except ValidationError:
            print('Error validating url: ' + url)
            return False
        return True

def load_content_by_url(url, timeout=10):
    '''Method for loading html page from URL'''
    session = requests.Session()
    request_result = session.get(url, timeout=timeout)
    return request_result

def load_run_module(module_name, MODULE_TYPE, modules_list=[]):
    for model in modules_list:
        importlib.import_module(model)
    module_full_name = MEDIA_FOLDER + MODULE_TYPE + module_name
    infoblock_module = importlib.import_module(module_full_name)
    result, value = infoblock_module.run(None)
    if result:
        return value
    else:
        return None

def get_current_datetime():
    return datetime.utcnow().replace(tzinfo=utc)
