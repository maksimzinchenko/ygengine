# Generated by Django 3.2.16 on 2022-12-15 07:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yengine', '0004_auto_20221215_0021'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayName', models.CharField(default='', max_length=255)),
                ('channelId', models.CharField(default='', max_length=255)),
                ('channelUrl', models.CharField(default='', max_length=255)),
                ('profileImageUrl', models.CharField(default='', max_length=255)),
                ('photo_id', models.CharField(default='', max_length=255)),
                ('register_date', models.DateTimeField(auto_now_add=True)),
                ('banned', models.BooleanField(default=False, verbose_name='User banned')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_game', models.BooleanField(default=True, verbose_name='This game is active (current)')),
                ('game_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Game starts datetime')),
            ],
        ),
        migrations.CreateModel(
            name='GameModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('module_file', models.FileField(blank=True, default=None, null=True, upload_to='game_modules')),
                ('module_description', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GameModuleProps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
                ('game_module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gamemodule')),
            ],
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_state', models.TextField(default='{}', verbose_name='Serialized JSON state of player')),
                ('player_tag', models.CharField(default='PLAYER', max_length=255, verbose_name='Player TAG for fast selecting')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.game', verbose_name='Player game ref')),
            ],
        ),
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gametype_name', models.CharField(default='', max_length=255)),
                ('reg_change', models.BooleanField(default=False, verbose_name='Enable change registration')),
                ('multi_move', models.BooleanField(default=False, verbose_name='Enable multi moves or disable')),
                ('first_move', models.BooleanField(default=False, verbose_name='Enable first count move or last')),
                ('move_change', models.BooleanField(default=False, verbose_name='Enable change move option')),
                ('move_choice_option', models.CharField(choices=[('SNF', 'Single move. No change. Count first'), ('SCL', 'Single move. Can change. Count last'), ('MNF', 'Multi move. No change. Count first'), ('MCL', 'Multi move. Can change. Count last'), ('MCLA', 'Multi move. Can add. Count last')], default='SNF', max_length=4)),
                ('module_items', models.ManyToManyField(through='yengine.GameModuleProps', to='yengine.GameModule')),
            ],
        ),
        migrations.CreateModel(
            name='InfoblockModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('module_file', models.FileField(blank=True, default=None, null=True, upload_to='infoblock_modules')),
                ('module_description', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LightChatUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayName', models.CharField(default='', max_length=255)),
                ('profileImageUrl', models.CharField(default='', max_length=255)),
                ('photo_id', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('register_date', models.DateTimeField(auto_now_add=True)),
                ('banned', models.BooleanField(default=False, verbose_name='User banned')),
                ('chat_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.chatuser')),
            ],
        ),
        migrations.CreateModel(
            name='PhaseModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('module_file', models.FileField(blank=True, default=None, null=True, upload_to='phase_modules')),
                ('module_description', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhaseModuleProps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RealStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activate', models.BooleanField(default=False, verbose_name='Stream ready to online')),
                ('online', models.BooleanField(default=False, verbose_name='Stream is online')),
                ('real_stream_name', models.CharField(default='', max_length=255, verbose_name='Real stream name')),
                ('stream_key', models.CharField(default='', max_length=255, verbose_name='Stream key')),
                ('stream_start_datetime', models.DateTimeField(blank=True, null=True, verbose_name='When stream starts')),
                ('stream_realstart_datetime', models.DateTimeField(blank=True, default=None, null=True, verbose_name='When stream starts real')),
                ('stream_realend_datetime', models.DateTimeField(blank=True, default=None, null=True, verbose_name='When stream ends real')),
                ('start_phase_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Current phase start date time')),
                ('current_phase_games_count', models.IntegerField(default=0, verbose_name='Current game phase games count')),
                ('current_chat_request_interval', models.IntegerField(default=30, verbose_name='Chat request update interval in sec')),
                ('video_id', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Video id of real stream')),
                ('chat_id', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Chat id got from youtube')),
                ('chat_last_page', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Chat last page')),
                ('last_chat_request_datetime', models.DateTimeField(blank=True, default=None, null=True, verbose_name='API last request datetime')),
                ('enable_light_chat', models.BooleanField(default=False)),
                ('current_light_chat_request_interval', models.IntegerField(default=3, verbose_name='Chrome Extension Light Chat request update interval in sec')),
                ('current_audio_file', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.audiofile', verbose_name='Audio file')),
                ('current_obs_scene', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.obsscene', verbose_name='Current scene')),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stream_name', models.CharField(default='Name', max_length=255, verbose_name='Stream name')),
                ('default_obs_request_interval', models.IntegerField(default=5, verbose_name='Default stream update interval in OBS in sec')),
                ('default_sync_request_interval', models.IntegerField(default=5, verbose_name='Default sync timer update interval in sec')),
                ('default_obs_scene', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.obsscene')),
                ('game_channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.gamechannel', verbose_name='Game stream channel')),
                ('playlist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.playlist', verbose_name='Real stream playlist')),
            ],
        ),
        migrations.CreateModel(
            name='StreamModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('module_file', models.FileField(blank=True, default=None, null=True, upload_to='stream_modules')),
                ('module_description', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserRank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.FloatField(default=0)),
                ('api_chat_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.chatuser', verbose_name='Game type of rank')),
                ('game_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gametype', verbose_name='Game type of rank')),
                ('light_chat_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.lightchatuser', verbose_name='Light chat user')),
            ],
        ),
        migrations.CreateModel(
            name='StreamPhase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_game_phase', models.BooleanField(default=False, verbose_name='Is game Phase')),
                ('max_games_count', models.IntegerField(default=0, verbose_name='Maximum number of stream phase games')),
                ('phase_time', models.IntegerField(default=0, verbose_name='Time in seconds')),
                ('order', models.IntegerField(default=0)),
                ('obs_request_interval', models.IntegerField(default=10, verbose_name='Scene update interval in OBS in sec')),
                ('sync_request_interval', models.IntegerField(default=5, verbose_name='Sync timer update interval in sec')),
                ('enable_API_chat', models.BooleanField(default=False, verbose_name='Scan chat messages over YouTube API')),
                ('chat_request_interval', models.IntegerField(default=30, verbose_name='Chat API update interval in sec')),
                ('game_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.gametype', verbose_name='Game type if it is game phase')),
                ('phase_modules', models.ManyToManyField(through='yengine.PhaseModuleProps', to='yengine.PhaseModule')),
                ('phase_obs_scene', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.obsscene', verbose_name='Phase scene')),
                ('phase_stream', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.stream', verbose_name='Stream')),
                ('playlist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.playlist', verbose_name='Real stream playlist')),
            ],
        ),
        migrations.CreateModel(
            name='StreamModuleProps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.stream')),
                ('stream_module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.streammodule')),
            ],
        ),
        migrations.AddField(
            model_name='stream',
            name='stream_modules',
            field=models.ManyToManyField(through='yengine.StreamModuleProps', to='yengine.StreamModule'),
        ),
        migrations.CreateModel(
            name='Sponsors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sponsor', models.BooleanField(default=False)),
                ('chat_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.chatuser', verbose_name='Chat user')),
                ('real_stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.realstream', verbose_name='Real stream of player')),
            ],
        ),
        migrations.AddField(
            model_name='realstream',
            name='current_stream_phase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.streamphase', verbose_name='Current phase'),
        ),
        migrations.AddField(
            model_name='realstream',
            name='stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.stream', verbose_name='Stream prototype'),
        ),
        migrations.AddField(
            model_name='phasemoduleprops',
            name='phase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.streamphase'),
        ),
        migrations.AddField(
            model_name='phasemoduleprops',
            name='phase_module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.phasemodule'),
        ),
        migrations.CreateModel(
            name='LightChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proccessed', models.BooleanField(default=False)),
                ('web_message_id', models.CharField(default='', max_length=255, unique=True)),
                ('message_datetime', models.DateTimeField()),
                ('chat_user_name', models.CharField(default='', max_length=255)),
                ('profileImageUrl', models.CharField(default='', max_length=255)),
                ('photo_id', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('message', models.TextField(default='', max_length=255)),
                ('ligh_chat_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.lightchatuser')),
                ('real_stream', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.realstream', verbose_name='Real stream')),
            ],
        ),
        migrations.CreateModel(
            name='Infoblock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_key', models.CharField(default='', max_length=255)),
                ('block_value', models.TextField(blank=True, default='', null=True)),
                ('infoblock_module', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.infoblockmodule')),
            ],
        ),
        migrations.CreateModel(
            name='GameTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(default='Team', max_length=255, verbose_name='TEAM NAME')),
                ('team_tag', models.CharField(default='ONE', max_length=255, verbose_name='GAME NAME TAG')),
                ('team_state', models.TextField(default='{}', verbose_name='Serialized JSON state of team')),
                ('current_active_team', models.BooleanField(default=False)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.game', verbose_name='Team game ref')),
            ],
        ),
        migrations.CreateModel(
            name='GameState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_state_datetime', models.DateTimeField(auto_now_add=True)),
                ('state_time', models.IntegerField(default=0, verbose_name='State timeout in seconds')),
                ('state', models.TextField(verbose_name='Serialized JSON state of game')),
                ('state_tag', models.CharField(default='BLANK', max_length=255, verbose_name='STATE TAG')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.game', verbose_name='Game of state')),
                ('next', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gamestate_next_state', to='yengine.gamestate', verbose_name='Next state')),
                ('prev', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gamestate_previous_state', to='yengine.gamestate', verbose_name='Previous state')),
            ],
        ),
        migrations.CreateModel(
            name='GamePlayerMove',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processed', models.BooleanField(default=False)),
                ('move_message', models.TextField(default='', verbose_name='Message of user with his moves')),
                ('game_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gamestate', verbose_name='Game state ref')),
                ('light_chat_move_message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.lightchatmessage', verbose_name='Move message from Light chat')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gameplayer', verbose_name='Player ref')),
            ],
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='ligh_chat_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.lightchatuser'),
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='light_chat_register_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.lightchatmessage', verbose_name='Register message from Light chat'),
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gameteam', verbose_name='PLayer team ref'),
        ),
        migrations.CreateModel(
            name='GameMoveLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_datetime', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(default='', verbose_name='Front game moves log message')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.game', verbose_name='Log game ref')),
            ],
        ),
        migrations.AddField(
            model_name='gamemoduleprops',
            name='phase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gametype'),
        ),
        migrations.CreateModel(
            name='GameLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proccessed', models.BooleanField(default=False)),
                ('log_datetime', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(default='{}', verbose_name='Serialized JSON game log message')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.game', verbose_name='Log game ref')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='game_type',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.gametype', verbose_name='Game type'),
        ),
        migrations.AddField(
            model_name='game',
            name='real_stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.realstream', verbose_name='Real stream'),
        ),
        migrations.AddField(
            model_name='game',
            name='stream_phase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.streamphase', verbose_name='Game phase of stream'),
        ),
        migrations.CreateModel(
            name='ChatMessagesBuffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proccessed', models.BooleanField(default=False)),
                ('messages', models.TextField(verbose_name='JSON response from Youtube API')),
                ('record_datetime', models.DateTimeField(auto_now=True)),
                ('real_stream', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.realstream', verbose_name='Real stream')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proccessed', models.BooleanField(default=False)),
                ('youtube_message_id', models.CharField(default='', max_length=255)),
                ('message_datetime', models.DateTimeField()),
                ('message', models.TextField(default='')),
                ('chat_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.chatuser')),
                ('real_stream', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='yengine.realstream', verbose_name='Real stream')),
            ],
        ),
        migrations.CreateModel(
            name='ChatBackMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proccessed', models.BooleanField(default=False)),
                ('message', models.CharField(default='', max_length=255)),
                ('message_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Message sent')),
                ('real_stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.realstream', verbose_name='Real stream')),
            ],
        ),
        migrations.AddIndex(
            model_name='lightchatuser',
            index=models.Index(fields=['displayName', 'profileImageUrl'], name='yengine_lig_display_f6428c_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='lightchatuser',
            unique_together={('displayName', 'profileImageUrl')},
        ),
        migrations.AddIndex(
            model_name='lightchatmessage',
            index=models.Index(fields=['web_message_id'], name='yengine_lig_web_mes_bd801a_idx'),
        ),
    ]
