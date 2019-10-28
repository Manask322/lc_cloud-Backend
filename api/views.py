# from django.core.serializers import get_serializer
# from django.shortcuts import render
# from rest_framework import generics, permissions

import json
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from api.serializers import *
from api.models import Image, Instance
from rest_framework.decorators import api_view
from django.contrib.auth.models import User


# Create your views here.


def list_of_instances(request, username):
    """
        List all the Instances
    """
    try:
        user = User.objects.get(username=username)
        try:
            instance = Instance.objects.filter(user=user)
            instance = instances_to_dict(instance)
            return JsonResponse({"instances": instance}, status=200)
        except Instance.DoesNotExist:
            return JsonResponse({"message": "Instances for username = {} does not exists".format(username)}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "User Name {} does not exits".format(username)}, status=400)


def instance_detail(request, pk):
    try:
        instance = Instance.objects.get(pk=pk)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance detail not found for Id= {} .".format(pk)}, status=400)
    instance = instance_to_dict(instance)
    return JsonResponse({"instance": instance}, status=200)


def start_instance(request):
    """
    Starts a Instance
    :param request:
    :param pk:
    :return:
    """
    try:
        instance = request.POST["instance"]
        user = User.objects.get(username=instance["username"])
    except KeyError:
        return JsonResponse({"message": "Instance Details not correct."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "requested user does not exists."}, status=400)

    new_instance = Instance(
        user=user,
        name=request["name"],
        IP=request["IP"],
        URL=request["URL"],
        RAM=request["RAM"],
        CPU=request["CPU"],
        ports=request["ports"],
        status="RU"
    )
    new_instance.save()

    return JsonResponse({"message": "Instance stated successfully"}, status=200)


def stop_instance(request, pk):
    """
    Stops the Instance
    :param request:
    :param pk:
    :return:
    """
    try:
        instance = Instance.objects.get(pk=pk)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance for requested ID= {} does not exists.".format(pk)}, status=400)
    return JsonResponse({"message": "Instance Stopped successfully"}, status=200)


def list_of_images(request):
    """
    Returns list of all Images
    :param request:
    :return: list_of_images
    """
    images = Image.objects.all()
    images = image_to_dict(images)
    return JsonResponse({"message": "Displayed list of Images", "images": images}, status=200)


def resource_monitor(request, pk):
    """
    Gives the Instance resources
    :param request:
    :param pk:
    :return:
    """
    try:
        current_instance = Instance.objects.get(pk=pk)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance does not exists for given ID"}, status=400)
    return JsonResponse({"message": "Returns resource usage", "instance": current_instance}, status=200)


def login(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.get(username=username)
    except KeyError:
        return JsonResponse({"message": "Incomplete data"}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid username"}, status=400)
    if user.password != password:
        return JsonResponse({"message": "Invalid password"}, status=400)
    return JsonResponse({"message": "Successfully logged in"}, status=200)


def signup(request):
    try:
        user_details = json.loads(request.POST['user_details'])
        if User.objects.filter(username=user_details['username']).exists():
            return JsonResponse({"message": "User with username={} already exists".
                                format(user_details['username'])}, status=400)
        User(username=user_details['username'], password=user_details['password'],
             name=user_details['name'], email=user_details['email'],
             dob=parse_date(user_details["dob"]), sex=user_details["sex"]).save()
        return JsonResponse({"message": "Successfully signed up"}, status=200)
    except KeyError:
        return JsonResponse({"message": "Incomplete data"}, status=400)






# class RegistrationAPI(generics.GenericAPIView):
#     serializer_class = CreateUserSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "token": AuthToken.objects.create(user)
#         })
#
#
# class LoginAPI(generics.GenericAPIView):
#     serializer_class = LoginUserSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "token": AuthToken.objects.create(user)[1]
#         })
#
#
# class UserAPI(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated, ]
#     serializer_class = UserSerializer
#
#     def get_object(self):
#         return self.request.user
