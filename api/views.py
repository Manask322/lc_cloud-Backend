import requests as req
import json
from django.http import JsonResponse
from api.serializers import *
from api.models import Image, Instance, Slave
from django.contrib.auth.models import User


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
            return JsonResponse({"message": "Instances for username = {} does not exists".format(username)}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"message": "User Name {} does not exits".format(username)}, status=200)


def instance_detail(request, pk):
    try:
        instance = Instance.objects.get(pk=pk)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance detail not found for Id= {} .".format(pk)}, status=200)
    instance = instance_to_dict(instance)
    return JsonResponse({"instance": instance}, status=200)


def start_instance(request):
    """
    Starts a Instance
    :param request:
    :param pk:
    :return:
    """
    request = json.loads(request.body.decode('UTF-8'))
    try:
        user = User.objects.get(username=request["username"])
        slaves = Slave.objects.all()

        # Write a decide function to choose slave.

        new_instance = Instance(slave_id=1212, user=user)
        new_instance.save()

        slave_response = req.post('http://localhost:8001/lc_slave/start_instance/',
                                  data=json.dumps({
                                      'instance_id': new_instance.id,
                                      'image': '1',
                                      'cpu': 123,
                                      'memory': 212
                                  }),
                                  headers={
                                      'content-type': 'application/json'
                                  })

        # slave_response = req.get('http://localhost:8001/lc_slave/start_instance/{}'.format(1))
        # slave_response = slave_response.json()

    except KeyError:
        return JsonResponse({"message": "Instance Details not correct."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "requested user does not exists."}, status=400)

    n_instance = Instance(
        user=user,
        name=request["name"],
        IP=request["IP"],
        URL=request["URL"],
        RAM=request["RAM"],
        CPU=request["CPU"],
        ports=request["ports"],
        status="RU"
    )
    n_instance.save()

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
        slave_response = req.post('http://localhost:8001/lc_slave/start_instance/',
                                  data=json.dumps({
                                      'instance_id': 'manas',
                                      'image': '1',
                                      'cpu': 123,
                                      'memory': 212
                                  }),
                                  headers={
                                      'content-type': 'application/json'
                                  })
        slave_response = req.get('http://localhost:8001/lc_slave/start_instance/1')
        slave_response = slave_response.json()

    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance for requested ID= {} does not exists.".format(pk)}, status=200)
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
        return JsonResponse({"message": "Instance does not exists for given ID"}, status=200)
    return JsonResponse({"message": "Returns resource usage", "instance": current_instance}, status=200)


def login(request):
    request = json.loads(request.body.decode('UTF-8'))
    try:
        username = request['username']
        password = request['password']
        user = User.objects.get(username=username)
    except KeyError:
        return JsonResponse({"message": "Incomplete data"}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid username"}, status=200)
    if user.password != password:
        return JsonResponse({"message": "Invalid password"}, status=400)
    return JsonResponse({"message": "Successfully logged in"}, status=200)


def signup(request):
    request = json.loads(request.body.decode('UTF-8'))
    try:
        user_details = request
        if User.objects.filter(username=user_details['username']).exists():
            return JsonResponse({"message": "User with username={} already exists".
                                format(user_details['username'])}, status=200)
        User(username=user_details['username'], password=user_details['password'],
             first_name=user_details['name'], email=user_details['email']).save()
        return JsonResponse({"message": "Successfully signed up"}, status=200)
    except KeyError:
        return JsonResponse({"message": "Incomplete data"}, status=200)
