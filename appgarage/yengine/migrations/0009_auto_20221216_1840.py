# Generated by Django 3.2.16 on 2022-12-16 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yengine', '0008_alter_realstream_current_stream_phase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realstream',
            name='current_chat_request_interval',
            field=models.IntegerField(default=30, verbose_name='API Chat request update interval in sec'),
        ),
        migrations.AlterField(
            model_name='realstream',
            name='current_light_chat_request_interval',
            field=models.IntegerField(default=3, verbose_name='Light Chat request update interval in sec'),
        ),
        migrations.AlterField(
            model_name='realstream',
            name='last_chat_request_datetime',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='API chat last request datetime'),
        ),
        migrations.AlterField(
            model_name='realstream',
            name='stream_realend_datetime',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Real stream ends'),
        ),
        migrations.AlterField(
            model_name='realstream',
            name='stream_realstart_datetime',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Real stream starts'),
        ),
        migrations.AlterField(
            model_name='realstream',
            name='stream_start_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Planning start date time'),
        ),
    ]
