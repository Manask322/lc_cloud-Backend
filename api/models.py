from django.db import models
from django.contrib.auth.models import User
from django.core.validators import int_list_validator

# Create your models here.


class Image(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    image_name = models.CharField(max_length=255, null=False)
    actual_name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)

    def __str__(self):
        return self.image_name


class Instance(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    IP = models.TextField()
    URL = models.TextField()
    RAM = models.IntegerField(null=False)
    CPU = models.IntegerField(null=False)
    ports = models.IntegerField(null=False)
    status = models.CharField(
        max_length=2,
        choices=[
            ('ID', 'Idle'),
            ('ST', 'Started'),
            ('RU', "Running"),
            ('SP', 'Stopped'),
        ],
        default='ID',
    )

    def __str__(self):
        return self.name


class Slave(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    IP = models.TextField()
    URL = models.TextField()
    RAM = models.IntegerField(null=False)
    CPU = models.IntegerField(null=False)

    def __str__(self):
        return self.name
