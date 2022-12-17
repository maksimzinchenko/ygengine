## select music by command from light chat by its audio code in playlist 

from yengine.models import RealStream, StreamPhase, PlaylistItem
from util_functions import answer_functions, voice_functions
import datetime
import pytz


def camVoices(message):
    cams = ['!track1', '!track2', '!track3']
    return answer_functions.answer_function_multi(message, cams)


def run(real_stream):

    selections = {}

    playlist_items = PlaylistItem.objects.filter(playlist = real_stream.current_stream_phase.playlist).order_by('order')

    for i in range(playlist_items.count()):
        selections[playlist_items[i].audio_code] = i

    answers_list = list(selections.keys())

    def answer_function(message):
        return answer_functions.answer_function_multi(message, answers_list)


    # selections = {
    #     '!track1': 1,
    #     '!track2': 2,
    #     '!track3': 3,
    # }

    current_audio = real_stream.current_audio_file

    time_interval = 3

    minimum_voices = 0

    utc = pytz.UTC
    now = datetime.datetime.utcnow().replace(tzinfo=utc)

    time_delta = now - datetime.timedelta(minutes=time_interval)

    if now.second % 1 == 0:
        # count voice every 5s second of every minute
        # voices for last 3 minutes play game
        answers = voice_functions.multiCanChangeVoiceCountAllVoiceLastVoice(real_stream, time_delta, answer_function)
        print(answers[0])
        if len(answers[0]) > 0:
            if len(answers[0][0]) > 1:
                print('many music')
                new_answer = answers[0][0][0]
            else:
                print('one music')
                new_answer = answers[0][0][0]
            print(new_answer)
            print("Голосов" + str(answers[1][new_answer]))
            # find current playing position 
            playlist_items = PlaylistItem.objects.filter(playlist = real_stream.current_stream_phase.playlist).order_by('order')
            selected_item = playlist_items[selections.get(new_answer)]
            if answers[1][new_answer] > minimum_voices:
                print('Changing audio to track ' + new_answer)
                real_stream.current_audio_file = selected_item.audio_file
                real_stream.save()
    
    mod_json = {}

    return(True, mod_json)