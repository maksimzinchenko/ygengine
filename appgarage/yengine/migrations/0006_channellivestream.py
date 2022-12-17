# Generated by Django 3.2.16 on 2022-12-15 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yengine', '0005_auto_20221215_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelLiveStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_id', models.CharField(max_length=255)),
                ('video_title', models.CharField(max_length=255)),
                ('published_at', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('thumbnail', models.CharField(max_length=255)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yengine.gamechannel')),
            ],
        ),
    ]