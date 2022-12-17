from django.db import models
from appgarage.settings import MEDIA_URL, MEDIA_FOLDER, GAME_MODULES_PATH, PHASE_MODULES_PATH, STREAM_MODULES_PATH
import os, pytz, requests, re, importlib
from bs4 import BeautifulSoup
from tinytag import TinyTag
from datetime import datetime
from django.utils.dateparse import parse_datetime
import configparser
import datetime as dt

from django.urls import reverse

from .utils import is_valid_url, load_content_by_url, get_current_datetime

utc = pytz.UTC

class OBSScene(models.Model):
    """
    OBS scenes wich can be used for phase creation
    """
    obs_scene_name = models.CharField(verbose_name='Scene name in OBS', max_length=255)
    obs_scene_description = models.TextField(verbose_name='Scene description')
    obs_scene_structure = models.TextField(verbose_name='Scene structure content')

    def __str__(self):
        return str(self.pk) + ' : ' + self.obs_scene_name

class GameChannel(models.Model):
    """
    Game channel holds Youtube channel id wich is used to get live video chat id
    """
    channel_name = models.CharField(
        verbose_name='Channel name or owner', max_length=255, default='Default Channel')
    channel_id = models.CharField(
        verbose_name='Channel ID from URL', max_length=255, blank=True)
    channel_url = models.CharField(
        verbose_name='Channel URL', max_length=255, blank=True)
    test_video = models.CharField(
        verbose_name='Any video for getting channel id', max_length=255, blank=True)
    rtmp_key = models.CharField(verbose_name='RTMP key for stream translation', max_length=255, blank=True)

    def fill_channelId_by_video(self):
        ''' Fill channelid by video url'''
        if not self.test_video is None:
            channelId = self.request_channelId_by_video()
            if not channelId is None:
                self.channel_id = channelId
                self.save()
                return (True, 'Channel ID ' + channelId + ' successfully received!')
        return (False, 'Something went wrong during channel id search...')

    def fill_channel_name_by_video(self):
        ''' Fill channel name by video url'''
        if not self.test_video is None:
            channel_name = self.request_channel_name_by_video()
            if not channel_name is None:
                self.channel_name = channel_name
                self.save()
                return (True, 'Channel name ' + channel_name + ' successfully received!')
        return (False, 'Something went wrong during channel name search...')

    def fill_channelId_by_channel(self):
        ''' Fill channelid by channel url'''
        if not self.channel_url is None:
            channelId = self.request_channelId_by_channel()
            if not channelId is None:
                self.channel_id = channelId
                self.save()
                return (True, 'Channel ID ' + channelId + ' successfully received!')
        return (False, 'Something went wrong during channel id search...')

    def fill_channel_name_by_channel(self):
        ''' Fill channel name by channel url'''
        if not self.channel_url is None:
            channel_name = self.request_channel_name_by_channel()
            if not channel_name is None:
                self.channel_name = channel_name
                self.save()
                return (True, 'Channel name ' + channel_name + ' successfully received!')
        return (False, 'Something went wrong during channel name search...')

    def request_channelId_by_video(self):
        ''' Method for getting channel Id by video url'''
        if is_valid_url(self.test_video):
            return self._extract_channel_id_from_html(load_content_by_url(self.test_video))

    def request_channel_name_by_video(self):
        ''' Method for getting channel name by video url'''
        if is_valid_url(self.test_video):
            return self._extract_channel_name_from_html(load_content_by_url(self.test_video))
    
    def request_channel_name_by_channel(self):
        ''' Method for getting channel Id by video url'''
        if is_valid_url(self.channel_url):
            return self._extract_channel_name_from_html(load_content_by_url(self.channel_url))

    def _extract_channel_name_from_html(self, html_content):
        '''Util method for search and return chanel name from html content'''
        soup = BeautifulSoup(html_content.content, "html.parser")
        meta_tag = soup.find('link', {'itemprop':'name'})
        return meta_tag['content']
    
    def _extract_channel_id_from_html(self, html_content):
        '''Util method for search and return meta with channelId from html source'''
        soup = BeautifulSoup(html_content.content, "html.parser")
        meta_tag = soup.find('meta', {'itemprop':'channelId'})
        return meta_tag['content']

    def get_active_streams_by_channel(self):
        '''Return active streams of channel'''
        pass
         

    def __str__(self):
        return self.channel_name + ' : ' + self.channel_url

class ChannelLiveStream(models.Model):
    channel = models.ForeignKey(GameChannel, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=255)
    video_title = models.CharField(max_length=255)
    published_at = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)

    @staticmethod
    def clear_channel_streams(channel=None):
        ChannelLiveStream.objects.filter(channel=channel).delete()

class AudioGenre(models.Model):
    """
    Audio genre. Just for selections by filter
    """
    genre_name = models.CharField(verbose_name='Genre', default='', blank=True, max_length=255)

    def __str__(self):
        return self.genre_name

class AudioFile(models.Model):
    '''
    Audio file entity
    '''
    audio_file_name = models.CharField(verbose_name='Audio file name', blank=True, max_length=255)
    audio_file = models.FileField(upload_to='media', null=True, blank=True)
    timing = models.IntegerField(verbose_name="Time in seconds", default=0)
    genre = models.ForeignKey(AudioGenre, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def save(self, *args, **kwargs):
        super(AudioFile, self).save(*args, **kwargs)
        if self.audio_file:
            self.audio_file_name = os.path.basename(self.audio_file.path)
            filepath = MEDIA_FOLDER + MEDIA_URL + self.audio_file_name
            tag = TinyTag.get(filepath)
            self.timing = int(tag.duration)
            super(AudioFile, self).save(*args, **kwargs)
        else:
            self.audio_file_name = None
            self.timing = 0
            super(AudioFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.audio_file_name + ': ' + str(self.timing) + ' sec'

class PlayList(models.Model):
    playlist_name = models.CharField(verbose_name='Playlist name', max_length=255)
    playlist_items = models.ManyToManyField(AudioFile, through='PlaylistItem')

    def __str__(self):
        return self.playlist_name

class PlaylistItem(models.Model):
    audio_file = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    playlist = models.ForeignKey(PlayList, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    timing = models.IntegerField(verbose_name="Time in seconds", default=0)
    audio_code = models.CharField(verbose_name='Code name', max_length=255, default="", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.timing is None or self.timing == 0:
            super(PlaylistItem, self).save(*args, **kwargs)
            filepath = MEDIA_FOLDER + MEDIA_URL + self.audio_file.audio_file_name
            tag = TinyTag.get(filepath)
            self.timing = int(tag.duration)
        super(PlaylistItem, self).save(*args, **kwargs)


class ChatUser(models.Model):
    '''Youtube API user from chat'''
    displayName = models.CharField(max_length=255, default='')
    channelId = models.CharField(max_length=255, default='')
    channelUrl = models.CharField(max_length=255, default='')
    profileImageUrl = models.CharField(max_length=255, default='')
    photo_id = models.CharField(max_length=255, default='')
    register_date = models.DateTimeField(auto_now_add=True)
    banned = models.BooleanField(verbose_name="User banned", default=False)

    def __str__(self):
        return self.displayName

class LightChatUser(models.Model):
    '''JS chrome extension chat parser user'''
    displayName = models.CharField(max_length=255, default='')
    profileImageUrl = models.CharField(max_length=255, default='')
    photo_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    register_date = models.DateTimeField(auto_now_add=True)
    chat_user = models.ForeignKey(ChatUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    banned = models.BooleanField(verbose_name="User banned", default=False)

    def __str__(self):
        return self.displayName

    class Meta:
        unique_together = ('displayName', 'profileImageUrl')
        indexes = [models.Index(fields=['displayName', 'profileImageUrl']),]

class GameModule(models.Model):
    '''Module with game logic'''
    module_name = models.CharField(max_length=255, default='', blank=True, null=True)
    module_file = models.FileField(upload_to='game_modules', null=True, blank=True, default=None)
    module_description = models.CharField(max_length=255, default='', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(GameModule, self).save(*args, **kwargs)
        if self.module_file:
            self.module_name = os.path.splitext(os.path.basename(self.module_file.path))[0]
            super(GameModule, self).save(*args, **kwargs)
        else:
            self.module_name = None
            super(GameModule, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.module_name) + ': ' + str(self.module_description)

class GameType(models.Model):
    '''Game type description by params'''
    MOVE_SELECTION_CHOICE = (
        ('SNF', 'Single move. No change. Count first'),
        ('SCL', 'Single move. Can change. Count last'),
        ('MNF', 'Multi move. No change. Count first'),
        ('MCL', 'Multi move. Can change. Count last'),
        ('MCLA', 'Multi move. Can add. Count last'),
    )
    gametype_name = models.CharField(max_length=255, default='')
    module_items = models.ManyToManyField(GameModule, through='GameModuleProps')
    reg_change = models.BooleanField(default=False, verbose_name="Enable change registration")
    multi_move = models.BooleanField(default=False, verbose_name="Enable multi moves or disable")
    first_move = models.BooleanField(default=False, verbose_name="Enable first count move or last")
    move_change = models.BooleanField(default=False, verbose_name="Enable change move option")
    move_choice_option = models.CharField(max_length=4, choices=MOVE_SELECTION_CHOICE, default="SNF")
    
    
    
    def __str__(self):
        return self.gametype_name

class GameModuleProps(models.Model):
    '''Game modules list with order of execution'''
    game_module = models.ForeignKey(GameModule, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    phase = models.ForeignKey(GameType, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

class StreamModule(models.Model):
    '''Modules for run during stream'''
    module_name = models.CharField(max_length=255, default='', blank=True, null=True)
    module_file = models.FileField(upload_to='stream_modules', null=True, blank=True, default=None)
    module_description = models.CharField(max_length=255, default='', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super(StreamModule, self).save(*args, **kwargs)
        if self.module_file:
            self.module_name = os.path.splitext(os.path.basename(self.module_file.path))[0]
            super(StreamModule, self).save(*args, **kwargs)
        else:
            self.module_name = None
            super(StreamModule, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.module_name) + ': ' + str(self.module_description)

class PhaseModule(models.Model):
    '''Modules for run during stream phase'''
    module_name = models.CharField(max_length=255, default='', blank=True, null=True)
    module_file = models.FileField(upload_to='phase_modules', null=True, blank=True, default=None)
    module_description = models.CharField(max_length=255, default='', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(PhaseModule, self).save(*args, **kwargs)
        if self.module_file:
            self.module_name = os.path.splitext(os.path.basename(self.module_file.path))[0]
            super(PhaseModule, self).save(*args, **kwargs)
        else:
            self.module_name = None
            super(PhaseModule, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.module_name) + ': ' + str(self.module_description)

class InfoblockModule(models.Model):
    '''MOdule for run when infoblock request'''
    module_name = models.CharField(max_length=255, default='', blank=True, null=True)
    module_file = models.FileField(upload_to='infoblock_modules', null=True, blank=True, default=None)
    module_description = models.CharField(max_length=255, default='', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(InfoblockModule, self).save(*args, **kwargs)
        # filepath = self.audio_file.path
        # # print(filepath)
        if self.module_name is None:
            self.module_name = os.path.splitext(os.path.basename(self.module_file.path))[0]
            #self.module_name = os.path.basename(self.module_file.path)
            super(InfoblockModule, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.module_name) + ': ' + str(self.module_description)


class Stream (models.Model):
    '''Stream template'''
    stream_name = models.CharField(verbose_name='Stream name', max_length=255, default='Name')
    game_channel = models.ForeignKey(GameChannel, verbose_name='Game stream channel', blank=True, null=True, on_delete=models.CASCADE)
    stream_modules = models.ManyToManyField(StreamModule, through='StreamModuleProps')
    playlist = models.ForeignKey(PlayList, verbose_name='Stream playlist', on_delete=models.SET_NULL, null=True, blank=True)
    default_obs_scene = models.ForeignKey(OBSScene, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    default_obs_request_interval = models.IntegerField(verbose_name='Default stream update interval in OBS in sec', default=5)
    default_sync_request_interval = models.IntegerField(verbose_name='Default sync timer update interval in sec', default=5)
    enable_light_chat = models.BooleanField(default=False, verbose_name="Use light chat for scan")

    def __str__(self):
        return self.game_channel.channel_name + ' : ' + self.stream_name

    def has_default_obs_scene(self):
        return not self.default_obs_scene is None

    def process_stream_modules(self, real_stream, data):
        if self.stream_modules.count() > 0:
            all_stream_modules = self.stream_modules.filter().order_by('streammoduleprops__order')
            for s_module in all_stream_modules:
                module_full_name = MEDIA_FOLDER + STREAM_MODULES_PATH + s_module.module_name
                stream_mod = importlib.import_module(module_full_name)
                result, value = stream_mod.run(real_stream)
                data['stream_module_' + str(s_module.module_name)] = value
                if not result:
                    #if module return false, when select next phase or module will change phase by itself
                    # nextPhase = phases.filter(order__gt = currentPhase.order)
                    # if nextPhase.count() > 0:
                    #     nextPhase = nextPhase.first()
                    #     currentPhase = nextPhase
                    #     real_stream.current_stream_phase = nextPhase
                    #     real_stream.start_phase_datetime = datetime.utcnow().replace(tzinfo=utc)
                    #     real_stream.current_obs_scene = nextPhase.phase_obs_scene
                    #     real_stream.current_phase_games_count = 0
                    #     real_stream.save()
                    # else:
                    #     real_stream.activate = False
                    #     real_stream.save()
                    #     data['finished'] = True
                    if 'updateInterval' in result[1]:
                        data['updateInterval'] = result[1]['updateInterval']
                    
                    return data
        return data

class StreamPhase(models.Model):
    '''Stream template phase'''
    is_game_phase = models.BooleanField(
        verbose_name='Is game Phase', default=False)
    phase_modules = models.ManyToManyField(PhaseModule, through='PhaseModuleProps')
    game_type = models.ForeignKey(
        GameType, verbose_name='Game type if it is game phase', blank=True, null=True, on_delete=models.CASCADE)
    max_games_count = models.IntegerField(
        verbose_name='Maximum number of stream phase games', default=0)
    phase_time = models.IntegerField(verbose_name='Time in seconds', default=0)
    phase_stream = models.ForeignKey(
        Stream, verbose_name='Stream', null=True, on_delete=models.CASCADE)
    phase_obs_scene = models.ForeignKey(OBSScene, verbose_name='Phase scene', on_delete=models.SET_NULL, null=True, blank=True)
    order = models.IntegerField(default=0)
    obs_request_interval = models.IntegerField(
        verbose_name='Scene update interval in OBS in sec', default=10)
    sync_request_interval = models.IntegerField(verbose_name='Sync timer update interval in sec', default=5)
    enable_API_chat = models.BooleanField(default=False, verbose_name='Scan chat messages over YouTube API')
    chat_request_interval = models.IntegerField(verbose_name='Chat API update interval in sec', default=30)
    playlist = models.ForeignKey(PlayList, verbose_name='Stream phase playlist', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.phase_stream) + ' phase[' + str(self.order) + '] - ' + str(self.phase_obs_scene)

    def get_stream_phases_by_phase(self):
        return StreamPhase.objects.filter(phase_stream=self.phase_stream).order_by('order')

    def get_next_phases(self):
        return self.get_stream_phases_by_phase().filter(order__gt = self.order)

    def get_next_phase(self):
        return self.get_stream_phases_by_phase().filter(order__gt = self.order).first()
    

class StreamModuleProps(models.Model):
    '''List of stream modules to run with order'''
    stream_module = models.ForeignKey(StreamModule, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

class PhaseModuleProps(models.Model):
    '''List of stream phase modules to run with order'''
    phase_module = models.ForeignKey(PhaseModule, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    phase = models.ForeignKey(StreamPhase, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

class ChatMessagesBuffer(models.Model):
    '''Buffer messages with loaded data from YouTube chat API'''
    real_stream = models.ForeignKey('RealStream', verbose_name='Real stream', on_delete=models.CASCADE, default=None, null=True, blank=True)
    proccessed = models.BooleanField(default=False)
    messages = models.TextField(verbose_name='JSON response from Youtube API')
    record_datetime = models.DateTimeField(auto_now=True)

class Game(models.Model):
    '''Games created by engine for real stream and for stream phase'''
    active_game = models.BooleanField(verbose_name='This game is active (current)', default=True)
    real_stream = models.ForeignKey(
        'RealStream', verbose_name='Real stream', on_delete=models.CASCADE)
    stream_phase = models.ForeignKey(
        StreamPhase, verbose_name='Game phase of stream', on_delete=models.CASCADE)
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE, verbose_name='Game type', default=None, null=True)
    game_datetime = models.DateTimeField(
        verbose_name='Game starts datetime', auto_now_add=True)

    def get_game_modules(self):
        return self.game_type.module_items.filter().order_by('gamemoduleprops__order')

    def get_game_last_state(self):
        return GameState.objects.filter(game=self).order_by('id').last()

    def deactivate_game(self):
        self.active_game = False
        self.save()


class RealStream(models.Model):
    '''Real streams'''
    activate = models.BooleanField(default=False, verbose_name="Stream ready to online")
    online = models.BooleanField(default=False, verbose_name="Stream is online")
    real_stream_name = models.CharField(max_length=255, verbose_name='Real stream name', default='')
    stream_key = models.CharField(max_length=255, verbose_name='Stream key', default='')
    stream = models.ForeignKey(Stream, verbose_name='Stream prototype', on_delete=models.CASCADE)
    current_stream_phase = models.ForeignKey(StreamPhase, verbose_name='Current real stream phase', on_delete=models.SET_NULL, null=True, blank=True)
    current_obs_scene = models.ForeignKey(OBSScene, verbose_name='Current scene', on_delete=models.SET_NULL, null=True, blank=True)
    stream_start_datetime = models.DateTimeField(verbose_name='Planning start date time', blank=True, null=True)
    stream_realstart_datetime = models.DateTimeField(verbose_name='Real stream starts', blank=True, null=True, default=None)
    stream_realend_datetime = models.DateTimeField(verbose_name='Real stream ends', blank=True, null=True, default=None)
    start_phase_datetime = models.DateTimeField(verbose_name='Current phase start date time', blank=True, null=True)
    current_phase_games_count = models.IntegerField(verbose_name='Current game phase games count', default=0)
    current_chat_request_interval = models.IntegerField(verbose_name='API Chat request update interval in sec', default=30)
    video_id = models.CharField(max_length=255, null=True, blank=True, default=None, verbose_name='Video id of real stream')
    chat_id = models.CharField(max_length=255, null=True, blank=True, default=None, verbose_name='Chat id got from youtube')
    chat_last_page = models.CharField(max_length=255, null=True, blank=True, default=None, verbose_name='Chat last page')
    last_chat_request_datetime = models.DateTimeField(verbose_name='API chat last request datetime', blank=True, null=True, default=None)
    enable_light_chat = models.BooleanField(default=False)
    current_light_chat_request_interval = models.IntegerField(verbose_name='Light Chat request update interval in sec', default=3)
    current_audio_file = models.ForeignKey(AudioFile, verbose_name="Audio file", on_delete=models.SET_NULL, null=True, blank=True, default=None)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.stream_start_datetime) + ':' + self.real_stream_name + ' : from [' + self.stream.stream_name + ']'

    def create_new_game(self):
        current_game = Game(active_game=True, real_stream=self, stream_phase=self.current_stream_phase, game_type=self.current_stream_phase.game_type)
        current_game.save()
        start_game_state = GameState(game = current_game, state_time=0, state='{}', state_tag="START")
        start_game_state.save()

    @staticmethod
    def get_last_real_stream_by_stream_key(stream_key):
        return RealStream.objects.filter(stream_key=stream_key).last() or False

    def get_stream_begins_in(self):
        return self.stream_start_datetime.replace(tzinfo=utc).timestamp() - datetime.utcnow().replace(tzinfo=utc).timestamp()

    def get_stream_phase_duration(self):
        return datetime.utcnow().replace(tzinfo=utc).timestamp() - self.start_phase_datetime.replace(tzinfo=utc).timestamp()

    def get_last_stream_phase(self):
        """
        Return last StreamPhase for current RealStream.
        """
        return StreamPhase.objects.filter(phase_stream=self.stream).order_by('order').last()

    def save_disable_realstream(self):
        """
        Save and disables current real stream
        """
        self.stream_realend_datetime = datetime.utcnow().replace(tzinfo=utc)
        self.activate = False
        self.online = False
        self.save()

    def get_realstream_timestamp(self):
        return self.stream_start_datetime.replace(tzinfo=utc).timestamp()

    def is_finished(self):
        """
        Check if real stream is finished
        Real stream is finished if:
        for game stream:
            current_phase_games_count >= last_phase.max_games_count
        """
        # find last phase of stream from ordered phases of stream
        # if real stream not ready for online (activate = False) , return None
        if not self.stream_realend_datetime is None:
            return True

        if not self.activate:
            return False

        # if stream don't has phases, return None
        last_phase = self.get_last_stream_phase()
        if last_phase is None:
            return False

        # if current phase is last
        if self.current_stream_phase == last_phase:
            # if phase is game phase, check current games count
            if self.current_stream_phase.is_game_phase:
                # if this is game phase
                if self.current_phase_games_count >= last_phase.max_games_count:
                    #if curent game count is more then max game count
                    self.save_disable_realstream()
                    return True
                else:
                    # stream is not finished yet
                    return False
            else:
                # if not game stream, check last phase time > phase_time and last phase don't has modules
                if not self.start_phase_datetime is None:
                    delta = datetime.utcnow().replace(tzinfo=utc).timestamp() - self.start_phase_datetime.replace(tzinfo=utc).timestamp()
                    if (delta > self.current_stream_phase.phase_time) and (last_phase.phase_modules.count() == 0):
                        self.save_disable_realstream()
                        return True
                    else:
                        # return not 
                        return not self.online
                else:
                    # start_phase_datetime is not set
                    return False
        else:
            #current phase is not last
            return False
    
    def not_finished(self):
        return not bool(self.is_finished())

    def get_livechat_id_by_video(self):
        try:
            config = configparser.ConfigParser()
            config.read('.env')
            API_KEY = config['DEFAULT']['api_key']
            start = self.stream.game_channel.test_video.find('?v=')
            video_id = self.stream.game_channel.test_video[start+3:]
            params = {'part': 'liveStreamingDetails,statistics,snippet',
                    'key': API_KEY,
                    'id': video_id,
                    'fields': 'items(id,liveStreamingDetails(activeLiveChatId,concurrentViewers,actualStartTime))'}

            url = 'https://www.googleapis.com/youtube/v3/videos'
            r = requests.get(url, headers=None, params=params).json()
            return r['items'][0]['liveStreamingDetails']['activeLiveChatId']
        except:
            return None

    def get_real_stream_audio(self, data):
        data = { **data,
                'updateInterval': 10,
                'found': True,
                'active': False,
                'file-name': 'none'
                }
        data['updateInterval'] = self.stream.default_obs_request_interval
        if self.online:
            data['active'] = True
            # point of scene calcs
            if not self.current_audio_file is None:
                if (not self.is_finished()) and self.current_stream_phase and self.stream_realstart_datetime:
                    data['updateInterval'] = self.current_stream_phase.obs_request_interval
                data['file-name'] = self.current_audio_file.audio_file_name
            else:
                data['file-name'] = 'none'
        else:
            data['active'] = False
        data['finished'] = self.is_finished()
        return data

    def initRealStream(self):
        #starting real stream. init all params
        self.stream_realstart_datetime = datetime.utcnow().replace(tzinfo=utc)
        self.stream_realend_datetime = None
        self.online = True
        # find start stream phase
        start_stream_phase = StreamPhase.objects.filter(phase_stream=self.stream).order_by('order').first()
        if not start_stream_phase is None:
            self.current_stream_phase = start_stream_phase
            self.save()
            phase_obs_scene = self.current_stream_phase.phase_obs_scene
            if not phase_obs_scene is None:
                self.current_obs_scene = phase_obs_scene
                self.start_phase_datetime = datetime.utcnow().replace(tzinfo=utc)
                self.current_phase_games_count = 0
                self.current_chat_request_interval = start_stream_phase.chat_request_interval
                self.save()
                Game.objects.filter(real_stream=self).delete()
            else:
                print('!!!======================Phase has no OBS scene===================!!!')
        else:
            print('!!!================Stream has no any phases========================!!!')

    def get_video__and_chat_id(self):
        #work with chat if real_stream is active
        if self.online:
            #when check if real_stream has video_id of strean
            if (self.video_id is None) or (self.video_id == ''):
                
                # get video id from gamechannel test_video 
                video_url = self.stream.game_channel.test_video
                start = video_url.find('?v=')
                end = video_url.find('" rel="')
                video_id = video_url[start+3:end]
                if len(video_id) > 5 and start > 10 and end > 10:
                    # got video_id
                    self.video_id = video_id
                    self.save()
                else:
                    print("Can't find video id")
                
                # second method get video id by youtube api
                # print('Try to get video id')
                # try:
                #     params = {'part': 'id',
                #         'key': config['API_KEY'],
                #         'channelId': real_stream.stream.game_channel.channel_id,
                #         'eventType': 'live',
                #         'type': 'video',
                #         'order': 'viewCount',
                #         'fields': 'items(id(videoId))'}
                #     yapi_url = 'https://www.googleapis.com/youtube/v3/search'
                #     r = requests.get(yapi_url, headers=None, params=params).json()
                #     print(r)
                #     video_id = r.get('items')[0].get('id').get('videoId')
                #     real_stream.video_id = video_id
                #     real_stream.save()
                # except Exception as err:
                #     print(err)

            else:
                if (self.chat_id is None) or self.chat_id == '':
                    print('Try to get chat id')
                    try:
                        #get it using test video in gamechannel
                        self.chat_id = self.get_livechat_id_by_video()
                        self.save()
                    except Exception:
                        print('Something went wrong getting chat id')
        return (not self.video_id is None) and (not self.chat_id is None)

    def get_video__and_chat_id_from_channel(self):
        # get video id from gamechannel test_video 
        video_url = self.stream.game_channel.test_video
        
        start = video_url.find('?v=')
        video_id = video_url[start+3:]
        print(video_id)
        if len(video_id) > 5 and start > 10:
            # got video_id
            self.video_id = video_id
            self.save()
        else:
            print("Can't find video id")
        self.chat_id = self.get_livechat_id_by_video()
        self.save()
            

        return (not self.video_id is None) and (not self.chat_id is None)

    def getAPIChatBuffer(self):
        if self.last_chat_request_datetime is None:
            self.last_chat_request_datetime = datetime.utcnow().replace(tzinfo=utc)
            self.save()
        
        if datetime.utcnow().replace(tzinfo=utc).timestamp() - self.last_chat_request_datetime.replace(tzinfo=utc).timestamp() >= self.current_chat_request_interval:
            #time to get chat mess from api
            print('===============================get API chat=======================================')
            config = configparser.ConfigParser()
            config.read('.env')
            API_KEY = config['DEFAULT']['api_key']
            params = {'part': 'snippet,authorDetails',
            'key': API_KEY,
            'liveChatId': self.chat_id,
            'maxResults': 2000,
            'fields': 'kind, etag, nextPageToken, pageInfo(totalResults, resultsPerPage), items(id, snippet(type, publishedAt, hasDisplayContent, displayMessage), authorDetails(displayName, channelId, channelUrl, profileImageUrl, isChatSponsor))'}
            if self.chat_last_page:
                    params['pageToken']= self.chat_last_page
            url = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
            session = requests.Session()
            chat_messages = session.get(url, headers=None, params=params).json()
            if self.chat_last_page != chat_messages['nextPageToken']:
                # print(chat_messages)
                self.chat_last_page = chat_messages['nextPageToken']
                self.save()
                new_buffer = ChatMessagesBuffer.objects.create(
                    real_stream = self,
                    messages = chat_messages
                )
                new_buffer.save()
                self.last_chat_request_datetime = datetime.utcnow().replace(tzinfo=utc)
                self.save()

    def parseAPIChatBuffer(self):
        all_chat_buffers = ChatMessagesBuffer.objects.filter(real_stream = self, proccessed = False)
        for buffer in all_chat_buffers:
            try:
                #json_buffer = ast.literal_eval(buffer.messages)
                json_buffer = buffer.messages
                json_message_items = json_buffer['items']
                for json_item in json_message_items:
                    if json_item['snippet']['type'] == 'textMessageEvent' and json_item['snippet']['hasDisplayContent']:
                        # lets find or create chatuser
                        author_details = json_item['authorDetails']
                        author = ChatUser.objects.filter(channelId = author_details['channelId']).first()
                        if author is None:
                            #new chat user
                            reg_date = parse_datetime(json_item['snippet']['publishedAt'].replace(' ', ''))
                            author = ChatUser(
                                displayName = author_details['displayName'],
                                channelId = author_details['channelId'],
                                channelUrl = author_details['channelUrl'],
                                profileImageUrl = author_details['profileImageUrl'],
                                photo_id = re.findall('[\w\-\_]{30,}', author_details['profileImageUrl'])[0],
                                register_date = reg_date
                            )
                            author.save()

                        new_chat_message = ChatMessage(
                            youtube_message_id = json_item['id'],
                            message_datetime = parse_datetime(json_item['snippet']['publishedAt'].replace(' ', '')),
                            message = json_item['snippet']['displayMessage'],
                            chat_user = author,
                            real_stream = self
                        )
                        new_chat_message.save()
                        # try to find this message in light chat and merge chat user and light chat user
                        start_date = parse_datetime(json_item['snippet']['publishedAt'].replace(' ', '')) - dt.timedelta(minutes=5)
                        end_date = parse_datetime(json_item['snippet']['publishedAt'].replace(' ', '')) + dt.timedelta(minutes=5)
                        light_chat_message = LightChatMessage.objects.filter(
                            chat_user_name = author_details['displayName'],
                            message_datetime__range=(start_date, end_date),
                            photo_id = re.findall('[\w\-\_]{30,}', author_details['profileImageUrl'])[0]
                        ).first()
                        if light_chat_message is not None:
                            #found such message
                            #write this light chat user a chat user if it' None yet
                            if light_chat_message.ligh_chat_user.chat_user is None:
                                # chat user did't set
                                light_chat_user = light_chat_message.ligh_chat_user
                                light_chat_user.chat_user = author
                                light_chat_user.save()


                buffer.proccessed = True
                buffer.save()
            except Exception as err:
                print('Error loading json chat buffer')
                print(err)

    def reset_real_stream(self):
        self.activate = False
        self.online = False
        self.current_obs_scene = None
        self.stream_start_datetime = datetime.utcnow().replace(tzinfo=utc)
        self.stream_realstart_datetime = None
        self.stream_realend_datetime = None
        self.start_phase_datetime = None
        self.current_phase_games_count = 0
        self.video_id = None
        self.chat_id = None
        self.chat_last_page = None
        self.last_chat_request_datetime = None
        self.enable_light_chat = self.stream.enable_light_chat
        self.current_light_chat_request_interval = 3
        self.current_audio_file = None
        self.current_stream_phase = None
        self.save()
        Game.objects.filter(real_stream=self).delete()

    def load_next_phase(self, next_phase):
        self.start_phase_datetime = get_current_datetime()
        self.current_stream_phase = next_phase
        self.current_obs_scene = next_phase.phase_obs_scene
        self.current_chat_request_interval = next_phase.chat_request_interval
        self.current_phase_games_count = 0
        self.save()
        
    def get_real_stream_phase_games(self):
        return Game.objects.filter(real_stream=self, stream_phase=self.current_stream_phase).order_by('id')

    def get_real_stream_phase_active_game(self):
        return Game.objects.filter(active_game=True, real_stream=self, stream_phase=self.current_stream_phase).last()

    def process_game_phase(self, data):
        '''Game phase processing'''
        if self.current_stream_phase.is_game_phase:
            phase_game_counter = self.get_real_stream_phase_games().count()
            current_active_game = self.get_real_stream_phase_active_game()

            if current_active_game is None:
                if phase_game_counter < self.current_stream_phase.max_games_count:
                    self.create_new_game()
                else:
                    next_phase = self.current_stream_phase.get_next_phase()
                    if not next_phase is None:
                        self.load_next_phase(next_phase)
                    else:
                        self.save_disable_realstream()
                        data['finished'] = self.is_finished()
            else:
                game_state = current_active_game.get_game_last_state()
                data = game_state.run_game_modules(data)
                if game_state.state_time > 0:
                    state_lasts = game_state.get_state_lasts()
                    data['state_lasts'] = state_lasts
                    if state_lasts > game_state.state_time:
                        game_state.create_new_game_state(state_tag="END")
                
                if game_state.state_tag == 'END':
                    current_active_game.deactivate_game()
                    self.current_phase_games_count = phase_game_counter
                    self.save()          
        return data

    def step_phase(self, data):
        phase_lasts = self.get_stream_phase_duration()
        phases = StreamPhase.objects.filter(phase_stream=self.stream).order_by('order')
        if phase_lasts > self.current_stream_phase.phase_time:
            next_phase = phases.filter(order__gt = self.current_stream_phase.order)
            if next_phase.count() > 0:
                next_phase = next_phase.first()
                current_phase = next_phase
                self.current_stream_phase = next_phase
                self.start_phase_datetime = datetime.utcnow().replace(tzinfo=utc)
                self.current_obs_scene = next_phase.phase_obs_scene
                self.current_chat_request_interval = next_phase.chat_request_interval
                self.current_phase_games_count = 0
                self.save()
            else:
                self.stream_realend_datetime = datetime.utcnow().replace(tzinfo=utc)
                self.activate = False
                self.online = False
                self.save()
                data['finished'] = self.is_finished()


        if self.start_phase_datetime is not None:
            data['phase_lasts'] = phase_lasts
        return data

    def process_phase_modules(self, data):
        if self.current_stream_phase.phase_modules.count() > 0:
            all_phase_modules = self.current_stream_phase.phase_modules.filter().order_by('phasemoduleprops__order')
            for p_module in all_phase_modules:
                module_full_name = MEDIA_FOLDER + PHASE_MODULES_PATH + p_module.module_name
                phase_mod = importlib.import_module(module_full_name)
                result, value = phase_mod.run(self)
                data['phase_module_' + str(p_module.module_name)] = value
                if not result:
                    #if module return false, when module will change phase by itself
                    # nextPhase = phases.filter(order__gt = currentPhase.order)
                    # if nextPhase.count() > 0:
                    #     nextPhase = nextPhase.first()
                    #     currentPhase = nextPhase
                    #     real_stream.current_stream_phase = nextPhase
                    #     real_stream.start_phase_datetime = datetime.utcnow().replace(tzinfo=utc)
                    #     real_stream.current_obs_scene = nextPhase.phase_obs_scene
                    #     real_stream.current_phase_games_count = 0
                    #     real_stream.save()
                    return data
        return data

    def process_stream_modules(self, data):
        if self.stream.stream_modules.count() > 0:
            all_stream_modules = self.stream.stream_modules.filter().order_by('streammoduleprops__order')
            for s_module in all_stream_modules:
                module_full_name = MEDIA_FOLDER + STREAM_MODULES_PATH + s_module.module_name
                stream_mod = importlib.import_module(module_full_name)
                result, value = stream_mod.run(self)
                data['stream_module_' + str(s_module.module_name)] = value
                if not result:
                    #if module return false, when select next phase or module will change phase by itself
                    # nextPhase = phases.filter(order__gt = currentPhase.order)
                    # if nextPhase.count() > 0:
                    #     nextPhase = nextPhase.first()
                    #     currentPhase = nextPhase
                    #     real_stream.current_stream_phase = nextPhase
                    #     real_stream.start_phase_datetime = datetime.utcnow().replace(tzinfo=utc)
                    #     real_stream.current_obs_scene = nextPhase.phase_obs_scene
                    #     real_stream.current_phase_games_count = 0
                    #     real_stream.save()
                    # else:
                    #     real_stream.activate = False
                    #     real_stream.save()
                    #     data['finished'] = True
                    if 'updateInterval' in result[1]:
                        data['updateInterval'] = result[1]['updateInterval']
                    
                    return data
        return data

    def has_current_obs_scene(self):
        return not self.current_obs_scene is None

    def has_current_stream_phase(self):
        return not self.current_stream_phase is None

    def process_real_stream(self, data):
        data['updateInterval'] = self.current_stream_phase.sync_request_interval
        data = self.process_stream_modules(data=data)
        data = self.process_game_phase(data=data)
        data = self.process_phase_modules(data=data)
        data = self.step_phase(data=data)
        return data

    def load_API_chat(self):
        self.getAPIChatBuffer()
        self.parseAPIChatBuffer()

    

class Sponsors(models.Model):
    '''Model for saving sponsors of channel from real stream'''
    chat_user = models.ForeignKey(
        ChatUser, verbose_name='Chat user', null=True, on_delete=models.CASCADE)
    is_sponsor = models.BooleanField(default=False)
    real_stream = models.ForeignKey(RealStream, on_delete=models.CASCADE, verbose_name='Real stream of player')
     


class ChatMessage(models.Model):
    '''Messages from YouTube API chat for in real stream'''
    proccessed = models.BooleanField(default=False)
    youtube_message_id = models.CharField(max_length=255, default='')
    message_datetime = models.DateTimeField()
    chat_user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    message = models.TextField(default='')
    real_stream = models.ForeignKey('RealStream', verbose_name='Real stream', on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return str(self.message_datetime) + ':' + self.chat_user.displayName + ' : ' + self.message

class LightChatMessage(models.Model):
    '''Messages parsed from stream chat by JS chrome extension'''
    proccessed = models.BooleanField(default=False)
    ligh_chat_user = models.ForeignKey(LightChatUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    web_message_id = models.CharField(max_length=255, default='', unique=True)
    message_datetime = models.DateTimeField()
    chat_user_name = models.CharField(max_length=255, default='')
    profileImageUrl = models.CharField(max_length=255, default='')
    photo_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    message = models.TextField(max_length=255, default='')
    real_stream = models.ForeignKey('RealStream', verbose_name='Real stream', on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return str(self.message_datetime) + ':' + self.chat_user_name + ' : ' + self.message

    class Meta:
        indexes = [models.Index(fields=['web_message_id', ]), ]


class Infoblock(models.Model):
    '''Info blocks what can be load from other source like OBS '''
    block_key = models.CharField(max_length=255, default='')
    block_value = models.TextField(null=True, blank=True, default='')
    infoblock_module = models.ForeignKey(InfoblockModule, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        return self.block_key + ': ' + self.block_value[:100]

    def get_absolute_url(self):
        return reverse('infoblock', kwargs={'infoblock_key': self.block_key})


class ChatBackMessage(models.Model):
    '''Messages to send back to chat from JS chrome extension'''
    proccessed = models.BooleanField(default=False)
    message = models.CharField(max_length=255, default='')
    real_stream = models.ForeignKey('RealStream', verbose_name='Real stream', on_delete=models.CASCADE)
    message_datetime = models.DateTimeField(verbose_name='Message sent', auto_now_add=True)

    def __str__(self):
        if self.proccessed:
            proc = 'dropped'
        else:
            proc = 'in process'
        return proc + ': ' + self.message



class GameLog(models.Model):
    '''Model for common game logs'''
    proccessed = models.BooleanField(default=False)
    game = models.ForeignKey(Game, verbose_name='Log game ref', on_delete=models.CASCADE)
    log_datetime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(verbose_name='Serialized JSON game log message', default='{}')

    def __str__(self):
        return self.message

class GameMoveLog(models.Model):
    '''Move log of game'''
    game = models.ForeignKey(Game, verbose_name='Log game ref', on_delete=models.CASCADE)
    log_datetime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(verbose_name='Front game moves log message', default='')

    def __str__(self):
        return self.message

class GameState(models.Model):
    '''State of game with json state tag'''
    game = models.ForeignKey(Game, verbose_name='Game of state', on_delete=models.CASCADE)
    start_state_datetime = models.DateTimeField(auto_now_add=True)
    state_time = models.IntegerField(default=0, verbose_name="State timeout in seconds")
    state = models.TextField(verbose_name='Serialized JSON state of game')
    prev = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name="Previous state", related_name='%(class)s_previous_state')
    next = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, default=None , verbose_name="Next state", related_name='%(class)s_next_state')
    state_tag = models.CharField(max_length=255, verbose_name="STATE TAG", default='BLANK')

    def create_new_game_state(self, state_tag='BLANK'):
        new_game_state = GameState(game = self.game, state_time=0, state=self.state, prev = self, state_tag=state_tag)
        new_game_state.save()
        self.next = new_game_state
        self.save()

    def get_state_lasts(self):
        return get_current_datetime().timestamp() - self.start_state_datetime.replace(tzinfo=utc).timestamp()

    def run_game_modules(self, data):
        for g_module in self.game.get_game_modules():
            module_full_name = MEDIA_FOLDER + GAME_MODULES_PATH + g_module.module_name
            game_mod = importlib.import_module(module_full_name)
            result, value = game_mod.run(self.game.real_stream)
            data['game_module_' + g_module.module_name] = value
            # if module return True, generate new blank state
            if result:
                self.create_new_game_state()
        return data

class GameTeam(models.Model):
    '''Game teams'''
    game = models.ForeignKey(Game, verbose_name='Team game ref', on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255, verbose_name="TEAM NAME", default='Team')
    team_tag = models.CharField(max_length=255, verbose_name="GAME NAME TAG", default='ONE')
    team_state = models.TextField(verbose_name='Serialized JSON state of team', default='{}')
    current_active_team = models.BooleanField(default=False)

class GamePlayer(models.Model):
    '''Game players'''
    game = models.ForeignKey(Game, verbose_name='Player game ref', on_delete=models.CASCADE)
    team = models.ForeignKey(GameTeam, verbose_name='PLayer team ref', on_delete=models.CASCADE)
    light_chat_register_message = models.ForeignKey(LightChatMessage, verbose_name='Register message from Light chat', on_delete=models.SET_NULL, null=True, blank=True )
    #y_chat_register_message = models.ForeignKey(ChatMessage, verbose_name='Register message from API chat', on_delete=models.SET_NULL, null=True, blank=True)
    player_state = models.TextField(verbose_name='Serialized JSON state of player', default='{}')
    ligh_chat_user = models.ForeignKey(LightChatUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    player_tag = models.CharField(max_length=255, verbose_name="Player TAG for fast selecting", default='PLAYER')

    def __str__(self):
        return self.ligh_chat_user.displayName + ' : ' + self.team.team_name

class GamePlayerMove(models.Model):
    '''Game player move or message.'''
    processed = models.BooleanField(default=False)
    player = models.ForeignKey(GamePlayer, verbose_name='Player ref', on_delete=models.CASCADE)
    game_state = models.ForeignKey(GameState, verbose_name='Game state ref', on_delete=models.CASCADE)
    light_chat_move_message = models.ForeignKey(LightChatMessage, verbose_name='Move message from Light chat', on_delete=models.SET_NULL, null=True, blank=True )
    move_message = models.TextField(verbose_name='Message of user with his moves', default='')

class UserRank(models.Model):
    '''Rank of users'''
    game_type = models.ForeignKey(GameType, verbose_name='Game type of rank', on_delete=models.CASCADE)
    light_chat_user = models.ForeignKey(LightChatUser, verbose_name='Light chat user', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    api_chat_user = models.ForeignKey(ChatUser, verbose_name='Game type of rank', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    rank = models.FloatField(default=0)