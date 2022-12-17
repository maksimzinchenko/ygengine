from django.forms import models
from yengine.models import RealStream, StreamPhase,OBSScene
import datetime
import pytz

def run(real_stream):
    mod_json = {}
    # mod_json['see'] = real_stream.real_stream_name
    utc = pytz.UTC
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    if now.minute % 2 == 0:
        print('here2')
        real_stream.current_obs_scene = OBSScene.objects.get(obs_scene_name = 'S2')
        real_stream.save()
    else:
        print('here1')
        real_stream.current_obs_scene = OBSScene.objects.get(obs_scene_name = 'S1')
        real_stream.save() 
    return(True, mod_json)