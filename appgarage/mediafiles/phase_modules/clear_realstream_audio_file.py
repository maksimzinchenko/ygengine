
from datetime import datetime
import pytz, os
from yengine.models import PlaylistItem
# this phase module clear current real stream audio file.


def run(real_stream):
    utc = pytz.UTC
    real_stream.current_audio_file = None
    real_stream.save()
    mod_json = {}
    return(True, mod_json)