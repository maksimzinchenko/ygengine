# Generated by Django 3.2.16 on 2022-12-16 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yengine', '0007_auto_20221216_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realstream',
            name='current_stream_phase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yengine.streamphase', verbose_name='Current real stream phase'),
        ),
    ]
