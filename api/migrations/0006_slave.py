# Generated by Django 2.1.3 on 2019-10-29 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20191028_1105'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slave',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('IP', models.TextField()),
                ('URL', models.TextField()),
                ('RAM', models.IntegerField()),
                ('CPU', models.IntegerField()),
            ],
        ),
    ]