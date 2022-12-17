
from datetime import datetime
import pytz, os
from yengine.models import PlaylistItem
# this stream module plays (set audio files) during stream with loop.


def run(real_stream):
    utc = pytz.UTC
    mod_json = {}
    if real_stream.stream.playlist is not None:
        #playlist is set, count stream time
        time_delta = datetime.utcnow().replace(tzinfo=utc).timestamp() - real_stream.stream_realstart_datetime.replace(tzinfo=utc).timestamp()
        # print(time_delta)
        playlist_items = PlaylistItem.objects.filter(playlist = real_stream.stream.playlist).order_by('order')
        times = []
        audios = []
        timing = 0
        for i in playlist_items:
            timing += i.timing
            times.append(timing)
            audios.append(i.audio_file)
        if len(audios) > 0:
            delta_unlooped = time_delta % times[-1]
            print('Stream lasts: ' + str(delta_unlooped))
            for i in range(len(times)):
                if times[i] > delta_unlooped:
                    real_stream.current_audio_file = audios[i]
                    real_stream.save()
                    print('Till next:' + str(times[i] - delta_unlooped))
                    print(audios[i])
                    break

        
    return(True, mod_json)