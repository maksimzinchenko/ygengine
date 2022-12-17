from django.contrib import admin
from django.utils.safestring import mark_safe

import math, pytz
from datetime import datetime

from .models import Game, GameState, GameModule, GameModuleProps, GameType, GameTeam, GamePlayerMove
from .models import Stream, StreamPhase, StreamModule, StreamModuleProps
from .models import RealStream
from .models import PhaseModule, PhaseModuleProps
from .models import GameChannel, OBSScene, AudioGenre, PlayList, PlaylistItem, AudioFile, ChannelLiveStream
from .models import Infoblock, InfoblockModule
from .models import GameLog, GameMoveLog
from .models import ChatMessage, LightChatMessage, ChatBackMessage, ChatMessagesBuffer
from .models import ChatUser, LightChatUser, GamePlayer, UserRank

utc = pytz.UTC

# Register your models here.
admin.site.register(OBSScene)
admin.site.register(Infoblock)
admin.site.register(InfoblockModule)
admin.site.register(ChatBackMessage)
admin.site.register(GamePlayer)
admin.site.register(GameLog)
admin.site.register(UserRank)
admin.site.register(GameMoveLog)
admin.site.register(ChannelLiveStream)

@admin.register(GameChannel)
class GameChannelAdmin(admin.ModelAdmin):
    actions = ["fill_by_video", "fill_by_channel", "fill_name_by_video", "fill_name_by_channel"]

    list_display = ('channel_name', 'channel_id')
    search_fields = ['channel_name']
    list_display_links = ['channel_name']

    @admin.action(description='Search and fill channel data by video url')
    def fill_by_video(self, request, queryset):
        for channel in queryset:
            result, message = channel.fill_channelId_by_video()
            print(message)

    @admin.action(description='Search and fill channel data by channel url')
    def fill_by_channel(self, request, queryset):
        for channel in queryset:
            result, message = channel.fill_channelId_by_channel()
            print(message)

    @admin.action(description='Search and fill channel name by video url')
    def fill_name_by_video(self, request, queryset):
        for channel in queryset:
            result, message = channel.fill_channel_name_by_video()
            print(message)

    @admin.action(description='Search and fill channel name by channel url')
    def fill_name_by_channel(self, request, queryset):
        for channel in queryset:
            result, message = channel.fill_channel_name_by_channel()
            print(message)

admin.site.register(AudioGenre)

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('audio_file_name', 'timing','player')
    readonly_fields = [ 'audio_file_name', 'timing','player',]

    def player(self, obj):
        file = obj.audio_file.url
        template = f'<audio controls>' \
                   f'<source src={file}  type="audio/mpeg">' \
                   f'</audio>'
        return mark_safe(template)

#######################################################
class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 0
    ordering = ['order']

@admin.register(PlayList)
class PlayListAdmin(admin.ModelAdmin):
    list_display = ['playlist_name', 'playlist_count', 'playlist_long']
    readonly_fields = [ 'playlist_count', 'playlist_long']
    inlines = [PlaylistItemInline]

    def playlist_count(self, obj):
        all_songs = obj.playlist_items
        return all_songs.count()

    def playlist_long(self, obj):
        all_songs = obj.playlist_items.all()
        long = 0
        for i in all_songs:
            long += i.timing
        list_out = str(long) + ' sec | ' + str(math.floor(long/60)) + ':' + str(long%60)
        return list_out

#######################################################
@admin.register(LightChatUser)
class LightChatUserAdmin(admin.ModelAdmin):
    actions = ["ban_user"]

    list_display = ('banned', 'register_date', 'displayName', 'profileImageUrl', 'photo_id')
    search_fields = ['displayName']
    list_editable = ['banned',]
    list_display_links = ['displayName']

    @admin.action(description='Full reset real stream')
    def ban_user(self, request, queryset):
        for banned_user in queryset:
            GamePlayer.objects.filter(ligh_chat_user=banned_user).delete()
            LightChatMessage.objects.filter(ligh_chat_user=banned_user).delete()
            if banned_user.chat_user is not None:
                banned_user.chat_user.banned = True
    
            banned_user.save()
    
#######################################################
@admin.register(LightChatMessage)
class LightChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message_datetime', 'chat_user_name', 'message')
    search_fields = ['chat_user_name', 'message']
    ordering = ['-message_datetime']


#######################################################
@admin.register(StreamModule)
class StreamModuleAdmin(admin.ModelAdmin):
    readonly_fields = ["module_name"]

#######################################################
class StreamModulePropsInline(admin.TabularInline):
    model = StreamModuleProps
    extra = 0
    ordering = ['order']

class StreamPhaseInline(admin.TabularInline):
    model = StreamPhase
    extra = 0
    ordering = ['order']

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):

    list_display = ('stream_name', 'game_channel')
    inlines = [StreamModulePropsInline, StreamPhaseInline]

#######################################################
@admin.register(PhaseModule)
class PhaseModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_description')
    search_fields = ['module_name', 'module_description']
    readonly_fields = ['module_name']

#######################################################
class PhaseModulePropsInline(admin.TabularInline):
    model = PhaseModuleProps
    extra = 0
    ordering = ['order']
@admin.register(StreamPhase)
class StreamPhaseAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None,               {'fields': ['question_text']}),
    #     ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    # ]
    # list_display = ('stream_name', 'game_channel')
    inlines = [PhaseModulePropsInline]

#######################################################

@admin.register(GameModule)
class GameModuleAdmin(admin.ModelAdmin):
    readonly_fields = ["module_name"]
class  GameModulePropsInline(admin.TabularInline):
    model = GameModuleProps
    extra = 0
    ordering = ['order']
@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):
    inlines = [GameModulePropsInline]



#######################################################


class GameStateInline(admin.TabularInline):
    model = GameState
    extra = 0
    ordering = ['id']
    readonly_fields = ['start_state_datetime']
    fields = ['state_tag', 'start_state_datetime', 'state_time', 'state']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [GameStateInline]

#######################################################
class GameInline(admin.TabularInline):
    model = Game
    extra = 0
    ordering = ['game_datetime']


@admin.register(RealStream)
class RealStreamAdmin(admin.ModelAdmin):
    actions = ["init_real_stream", "get_live_chat_id_by_video", "get_live_chat_id_from_channel"]

    list_display = ('activate', 'online', 'real_stream_name', 'stream_key', 'stream_start_datetime', 'stream_realstart_datetime', 'video_id')
    list_display_links = ['real_stream_name']
    list_editable = ('activate','online', 'stream_key','video_id')
    fields = [('activate', 'online'),
    ('real_stream_name', 'stream_key'),
        'stream',
        'current_stream_phase',
        'current_obs_scene',
        ('stream_start_datetime', 'stream_realstart_datetime' ,'stream_realend_datetime'),
        'start_phase_datetime',
        'current_phase_games_count',
        'video_id',
        ('current_chat_request_interval', 'chat_id', 'chat_last_page', 'last_chat_request_datetime'),
        ('current_light_chat_request_interval'),
        'current_audio_file',
        'enable_light_chat'
        ]
    inlines = [GameInline]

    @admin.action(description='Full reset real stream')
    def init_real_stream(self, request, queryset):
        for real_stream in queryset:
            real_stream.reset_real_stream()

    @admin.action(description='Get live chat id by video url from channel and YouTube API')
    def get_live_chat_id_by_video(self, request, queryset):
        for real_stream in queryset:
            chat_id = real_stream.get_livechat_id_by_video()
            if not chat_id is None:
                real_stream.chat_id = chat_id
                real_stream.save()

    @admin.action(description='Fill video id and live chat id from GameChannel')
    def get_live_chat_id_from_channel(self, request, queryset):
        for real_stream in queryset:
            real_stream.get_video__and_chat_id_from_channel()
    


#######################################################

@admin.register(GameTeam)
class GameTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'team_tag', 'current_active_team', 'game', 'team_state')
    list_display_links = ['team_name']

####################################################

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('proccessed', 'message_datetime', 'chat_user', 'message', 'youtube_message_id')
    list_display_links = ['message']
####################################################

@admin.register(ChatMessagesBuffer)
class ChatMessagesBufferAdmin(admin.ModelAdmin):
    list_display = ('proccessed', 'record_datetime', 'messages', 'real_stream')
    list_display_links = ['messages']

####################################################

@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = ('banned', 'displayName', 'register_date')
    list_display_links = ['displayName']
####################################################

@admin.register(GamePlayerMove)
class GamePlayerMoveAdmin(admin.ModelAdmin):
    list_display = ('processed', 'player', 'game_state', 'move_message')


##################################################

class GamePlayerMoveInline(admin.TabularInline):
    model = GamePlayerMove
    extra = 0

@admin.register(GameState)
class GameStateAdmin(admin.ModelAdmin):
    readonly_fields = ['start_state_datetime']
    list_display = ('state_tag' ,'game', 'start_state_datetime', 'state_time', 'state')

    inlines = [GamePlayerMoveInline]

#######################################################