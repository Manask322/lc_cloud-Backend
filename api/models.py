from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Image(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    image_name = models.CharField(max_length=255, null=False)
    actual_name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)

    def __str__(self):
        return self.image_name


class Instance(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    subordinate_id = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    IP = models.TextField()
    URL = models.TextField()
    RAM = models.IntegerField(null=True)
    CPU = models.IntegerField(null=True)
    ports = models.TextField()
    ssh_port = models.IntegerField(null=True)
    status = models.CharField(
        max_length=2,
        choices=[
            ('CR', 'Created'),
            ('RU', "Running"),
            ('SP', 'Stopped'),
        ],
        default='CR',
    )

    def __str__(self):
        return self.name


class Subordinate(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    IP = models.TextField()
    URL = models.TextField()
    RAM = models.IntegerField(null=False)
    CPU = models.IntegerField(null=False)
    cpu_remaining = models.IntegerField(default=CPU)
    memory_used = models.IntegerField(default=0)

    def __str__(self):
        return self.name
