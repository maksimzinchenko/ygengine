# Generated by Django 3.2.16 on 2022-12-14 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yengine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamechannel',
            name='channel_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='Channel ID from URL'),
        ),
        migrations.AlterField(
            model_name='gamechannel',
            name='channel_url',
            field=models.CharField(blank=True, max_length=255, verbose_name='Channel URL'),
        ),
        migrations.AlterField(
            model_name='gamechannel',
            name='rtmp_key',
            field=models.CharField(blank=True, max_length=255, verbose_name='RTMP key for stream translation'),
        ),
        migrations.AlterField(
            model_name='gamechannel',
            name='test_video',
            field=models.CharField(blank=True, max_length=255, verbose_name='Any video for getting channel id'),
        ),
    ]
