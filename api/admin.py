from django.contrib import admin
from api.models import Image, Instance, Slave

# Register your models here.
admin.site.register(Image)
admin.site.register(Instance)
admin.site.register(Slave)
