# Generated by Django 2.2.7 on 2019-11-17 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0011_coachbio_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayListVideos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coach', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlist_videos', to='coach.coachRegister')),
                ('playlist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlists_videos', to='coach.Playlist')),
                ('video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlists_videos', to='coach.Video')),
            ],
        ),
    ]
