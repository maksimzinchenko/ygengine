from unittest import result
from django.forms import models
from yengine.models import RealStream, StreamPhase,OBSScene, ChatMessage
import datetime
import pytz

def keywithmaxval(d):
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

def run(real_stream):
    selections = {
        'cam1': 'S1',
        'cam2': 'S2',
        'cam3': 'S3',
    }

    results = []

    voices = {}

    time_interval = 2

    out = {}

    # multiplier = 60

    # divider = time_interval * multiplier

    mod_json = {}
    # mod_json['see'] = real_stream.real_stream_name
    utc = pytz.UTC
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    if now.minute % time_interval == 0:
    # if True:
        # count chat voices every 2 minutes and show scene from selections
        # command in chat is !cam1
        time_delta = now - datetime.timedelta(minutes=time_interval)
        voice_set = ChatMessage.objects.filter(real_stream = real_stream, message_datetime__gte = time_delta).order_by('message_datetime')

        for voice in voice_set:
            answer_list = []
            for answer in selections.keys():
                if '!' + answer in voice.message:
                    answer_list.append(answer)

            if voices.get(voice.chat_user.id, None) == None:
                voices[voice.chat_user.id] = []

            old_answers_list = voices[voice.chat_user.id]
            for answer in answer_list:
                if answer in old_answers_list:
                    old_answers_list.remove(answer)
                    old_answers_list.append(answer)
                else:
                    old_answers_list.append(answer)
            voices[voice.chat_user.id] = old_answers_list
        results =[]
        for i in voices.keys():
            results.append(voices[i])
        results = sum(results, [])
        for i in selections.keys():
            num = results.count(i)
            out[i] = num
        
        mod_json['results'] = out
        print(keywithmaxval(out))
        
        real_stream.current_obs_scene = OBSScene.objects.get(obs_scene_name = selections[keywithmaxval(out)])
        real_stream.save()

        
    else:
        pass
        # print('here1')
        # real_stream.current_obs_scene = OBSScene.objects.get(obs_scene_name = 'S1')
        # real_stream.save() 
    return(True, mod_json)