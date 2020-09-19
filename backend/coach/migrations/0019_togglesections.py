# Generated by Django 2.2.7 on 2020-01-07 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0018_associated'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToggleSections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.BooleanField(default=True)),
                ('workout', models.BooleanField(default=True)),
                ('playlist', models.BooleanField(default=True)),
                ('statistics', models.BooleanField(default=True)),
                ('coach', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='toggle_sections', to='coach.coachRegister')),
            ],
        ),
    ]