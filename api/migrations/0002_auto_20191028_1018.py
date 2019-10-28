# Generated by Django 2.1.3 on 2019-10-28 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instance',
            name='IPs',
        ),
        migrations.AddField(
            model_name='instance',
            name='IP',
            field=models.TextField(default='127.0.0.0'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instance',
            name='URL',
            field=models.TextField(default='localhost:8000'),
            preserve_default=False,
        ),
    ]