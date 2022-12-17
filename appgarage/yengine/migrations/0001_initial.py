# Generated by Django 3.2.16 on 2022-12-14 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GameChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(default='Default Channel', max_length=255, verbose_name='Channel name or owner')),
                ('channel_id', models.CharField(default='', max_length=255, verbose_name='Channel ID from URL')),
                ('channel_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Channel URL')),
                ('test_video', models.CharField(blank=True, default='', max_length=255, verbose_name='Any video for getting channel id')),
                ('rtmp_key', models.CharField(default='', max_length=255, verbose_name='RTMP key for stream translation')),
            ],
        ),
    ]
