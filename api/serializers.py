from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


def user_to_dict(user):
    user_detail = {
        "id": user.id,
        "username": user.username,
    }
    return user_detail


def instance_to_dict(instance):

    instance_detail = {
        "id": instance.id,
        "user": user_to_dict(instance.user),
        "name": instance.name,
        "IP": instance.IP,
        "URL": instance.URL,
        "RAM": instance.RAM,
        "CPU_usage": instance.CPU,
        "ports": instance.ports,
        "status": instance.status,
    }
    return instance_detail


def instances_to_dict(instances):
    instance_detail = []

    for instance in instances:
        instance_detail.append({
            "id": instance.id,
            "user": user_to_dict(instance.user),
            "name": instance.name,
            "IP": instance.IP,
            "URL": instance.URL,
            "RAM": instance.RAM,
            "CPU_usage": instance.CPU,
            "ports": instance.ports,
            "status": instance.status,
        })

    return instance_detail


def image_to_dict(images):
    image_detail = []

    for image in images:
        image_detail.append({
            "id": image.id,
            "image_name": image.image_name,
            "actual_name": image.actual_name,
            "description": image.description
        })

    return image_detail

# class CreateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'password')
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         user = User.objects.create_user(validated_data['username'],
#                                         None,
#                                         validated_data['password'])
#         return user
#
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username')
#
#
# class LoginUserSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()
#
#     def validate(self, data):
#         user = authenticate(**data)
#         if user and user.is_active:
#             return user
#         raise serializers.ValidationError("Unable to log in with provided credentials.")
