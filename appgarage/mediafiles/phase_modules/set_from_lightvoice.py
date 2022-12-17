from yengine.models import RealStream, StreamPhase,OBSScene
from util_functions import answer_functions, voice_functions
import datetime
import pytz


def camVoices(message):
    cams = ['!cam1', '!cam2', '!cam3']
    return answer_functions.answer_function_multi(message, cams)


def run(real_stream):
    selections = {
        '!cam1': 'S1',
        '!cam2': 'S2',
        '!cam3': 'S3',
    }

    current_scene = real_stream.current_obs_scene.obs_scene_name

    time_interval = 3

    minimum_voices = 0

    utc = pytz.UTC
    now = datetime.datetime.utcnow().replace(tzinfo=utc)

    time_delta = now - datetime.timedelta(minutes=time_interval)

    if now.second % 1 == 0:
        # count voice every 5s second of every minute
        # voices for last 3 minutes play game
        answers = voice_functions.multiCanChangeVoiceCountAllVoiceLastVoice(real_stream, time_delta, camVoices)
        print(answers[0])
        if len(answers[0]) > 0:
            if len(answers[0][0]) > 1:
                print('many cams')
                new_answer = answers[0][0][0]
            else:
                print('one cam')
                new_answer = answers[0][0][0]
            print(new_answer)
            print("Голосов" + str(answers[1][new_answer]))
            if current_scene != selections.get(new_answer) and answers[1][new_answer] > minimum_voices:
                print('Changing OBS scene to ' + new_answer)
                real_stream.current_obs_scene = OBSScene.objects.get(obs_scene_name = selections.get(new_answer, 'S1'))
                real_stream.save()
    
    mod_json = {}

    return(True, mod_json)