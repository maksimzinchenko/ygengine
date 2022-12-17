import pytz
from django.utils import timezone
import importlib

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from appgarage.settings import MEDIA_FOLDER, INFOBLOCK_MODULES_PATH

from .models import Infoblock, RealStream, ChatBackMessage

def index(request):
    '''Some abstract scene S2 and update time 10 sec'''
    data = {
        'updateInterval': 10,
        'currentScene': 'S2'
    }
    return JsonResponse(data, safe=False)

def timenow(request):
    '''Return current date and time'''
    return JsonResponse({
        'datenow': str(timezone.now())
    }, safe=False)


def infoblock(request, infoblock_key):
    '''
    Search infoblock by infoblock_key.
    If found, execute it's run method
    and return result in of execution if not None
    or return block_value field value
    '''
    data = {}
    data['block_value'] = 'Not found'

    infoblock = Infoblock.objects.filter(block_key = infoblock_key).first()
    if not infoblock is None:
        if not infoblock.infoblock_module is None:
            module_name = infoblock.infoblock_module.module_name
            if not module_name is None:
                module_full_name = MEDIA_FOLDER + INFOBLOCK_MODULES_PATH + module_name
                infoblock_module = importlib.import_module(module_full_name)
                result, value = infoblock_module.run(None)
                if result:
                    data['block_value'] = value
        else:
            data['block_value'] = infoblock.block_value
    return JsonResponse(data, safe=False)

def infoblock_stream(request, block_key, stream_key):
    '''Run infoblock for real stream with stream key'''
    data = {}
    data['block_value'] = 'Not found'
    real_stream = RealStream.objects.filter(stream_key=stream_key)
    block = Infoblock.objects.filter(block_key = block_key)
    if block.count() > 0:
        if block[0].infoblock_module is not None:
            if not block[0].infoblock_module.module_name is None:
                #infoblock_module = __import__('infoblock_modules.' + block[0].infoblock_module.module_name)
                module_full_name = MEDIA_FOLDER + INFOBLOCK_MODULES_PATH + block[0].infoblock_module.module_name
                infoblock_module = importlib.import_module(module_full_name)
                #infoblock_mod = getattr(infoblock_module, block[0].infoblock_module.module_name)
                result, value = infoblock_module.run(real_stream)
                if not result[0]:
                    data['block_value'] = value
        else:
            data['block_value'] = block[0].block_value
    return JsonResponse(data, safe=False)

def audio(request, stream_key):
    '''Get real stream by key and current audio'''
    data = {
        'updateInterval': 10,
        'found': False,
        'active': False
    }
    real_stream = RealStream.get_last_real_stream_by_stream_key(stream_key=stream_key)
    if real_stream:
        data = real_stream.get_real_stream_audio(data=data)


    print(data)
    return JsonResponse(data, safe=False)

@csrf_exempt
def back_chat(request, video_id):
    data = {}
    data['video_id'] = video_id
    real_stream = RealStream.objects.filter(video_id=video_id).first()
    if real_stream is not None:
        chat_messages = ChatBackMessage.objects.filter(real_stream = real_stream, proccessed = False)
        if chat_messages.count() > 0:
            current_message = chat_messages[0]
            data['has_message'] = True
            data['message'] = current_message.message
            current_message.proccessed = True
            current_message.save()
        else:
            data['has_message'] = False
    else:
        data['has_message'] = False

    return JsonResponse(data, safe=False)

def stream(request, stream_key):
    '''Return active and online real stream with stream_key (for OBS script request)'''
    data = {
        'updateInterval': 10,
        'found': False,
        'active': False,
        'finished': False,
        'currentScene': 'S0_default'
    }
    real_stream = RealStream.get_last_real_stream_by_stream_key(stream_key=stream_key)
    if real_stream:
        data['found'] = True
        data['updateInterval'] = real_stream.stream.default_obs_request_interval
        if real_stream.online:
            data['active'] = True
            if real_stream.has_current_obs_scene():
                data['currentScene'] = real_stream.current_obs_scene.obs_scene_name
                if real_stream.not_finished() and real_stream.has_current_stream_phase():
                    data['updateInterval'] = real_stream.current_stream_phase.obs_request_interval
            else:
                if real_stream.stream.has_default_obs_scene():
                    data['currentScene'] = real_stream.stream.default_obs_scene.obs_scene_name
        data['finished'] = real_stream.is_finished()
    return JsonResponse(data, safe=False)



def sync(request, stream_key):
    '''Sync task for engine'''
    data = {
        'updateInterval': 10,
        'found': False,
        'activate': False,
    }
    real_stream = RealStream.get_last_real_stream_by_stream_key(stream_key=stream_key)
    if not real_stream:
        return JsonResponse(data, safe=False)
    else:
        data['found'] = True
        data['updateInterval'] = real_stream.stream.default_sync_request_interval
        if real_stream.is_finished():
            data['finished'] = real_stream.is_finished()
            return JsonResponse(data, safe=False)
        
        if real_stream.get_stream_begins_in() > 0:
            data['activate'] = real_stream.online
            data['finished'] = real_stream.is_finished()
            data['will_start_sec'] = real_stream.get_stream_begins_in()
            return JsonResponse(data, safe=False)
        elif (real_stream.stream_realstart_datetime is None) and (not real_stream.online) and (real_stream.activate):
            real_stream.initRealStream()
        
        if real_stream.online and real_stream.current_stream_phase.enable_API_chat and real_stream.get_video__and_chat_id():
            real_stream.load_API_chat()

        data['updateInterval'] = real_stream.stream.default_sync_request_interval
        data['activate'] = real_stream.activate
        data['online'] = real_stream.online

        if real_stream.online and (real_stream.current_stream_phase is not None):
            data = real_stream.process_real_stream(data=data)
    return JsonResponse(data, safe=False)