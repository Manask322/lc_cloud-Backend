from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('auth/login/', views.login, name="login"),
    path('auth/signup/', views.signup, name="signup"),
    path('list_instances/<str:username>', views.list_of_instances, name="list_of_instances"),
    path('list_images/', views.list_of_images, name="list_of_images"),
    path('start_instance/', views.start_instance, name='start_instance'),
    path('stop_instance/<str:pk>', views.stop_instance, name="stop_instance"),
    path('instance/<str:pk>', views.instance_detail, name="view_instance")
]
