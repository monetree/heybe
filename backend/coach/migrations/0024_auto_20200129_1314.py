# Generated by Django 2.2.7 on 2020-01-29 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0023_statistics'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statistics',
            old_name='no_of_playlists_the_vieos_is_in',
            new_name='no_of_playlists_the_video_is_in',
        ),
    ]
