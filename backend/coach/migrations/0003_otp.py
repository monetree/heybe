# Generated by Django 2.2.6 on 2019-11-03 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0002_coachregister_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, max_length=256, null=True)),
                ('otp', models.IntegerField()),
            ],
        ),
    ]
