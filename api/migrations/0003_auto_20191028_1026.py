# Generated by Django 2.1.3 on 2019-10-28 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20191028_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, unique=True),
        ),
    ]