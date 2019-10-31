import requests as req
import json
from django.http import JsonResponse
from api.serializers import *
from api.models import Image, Instance, Slave
from django.contrib.auth.models import User


# slave_response = req.get('http://localhost:8001/lc_slave/start_instance/1')

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
        return JsonResponse({"message": "Username {} does not exits".format(username)}, status=400)


def instance_detail(request, pk):
    """
    :param request:
    :param pk:
    :return: Returns Instance Detail
    """

    try:
        instance = Instance.objects.get(pk=pk)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance detail not found for Id= {} .".format(pk)}, status=400)
    instance = instance_to_dict(instance)
    return JsonResponse({"instance": instance}, status=200)


def decide(slaves, cpu, memory):
    """
    :param slaves:
    :param cpu:
    :param memory:
    :return: returns a slave node to run a instance
    """
    max_free_memory = -1
    candidate_slave = None
    for slave in slaves:
        if slave.cpu_remaining < cpu:
            continue
        url = "http://{}/lc_slave/get_system_resource/".format(slave.URL)
        slave_system_resource = req.get(url)
        # if slave_system_resource.status_code == 500:
        #     if slave_system_resource.json()['message'] == "Internal Server Error":
        #         return -1
        #     elif slave_system_resource.json()['message'] == "RAM not numeric":
        #         return -2
        slave_system_resource = slave_system_resource.json()
        host_ram = slave_system_resource['host_ram']
        docker_ram = slave_system_resource['docker_ram']
        total_ram = slave_system_resource['total_memory']
        free_memory = total_ram - (host_ram - docker_ram + slave.memory_used)
        if free_memory >= memory and free_memory > max_free_memory:
            candidate_slave = slave
    return candidate_slave


def start_instance(request):
    """
    Starts a Instance
    :param request:
    :param pk:
    :return:
    """
    request = json.loads(request.body.decode('UTF-8'))
    try:
        user = User.objects.get(username=request['username'])
        slaves = Slave.objects.all()
        image = Image.objects.get(id=request["image"])
        # Write a decide function to choose slave.
        slave = decide(slaves, request['cpu'], request['memory'])
        if slave is None:
            return JsonResponse({"message": "No resources left to run instance"}, status=500)
        # elif slave == -1:
        #     return JsonResponse({"message": "Internal Server Error"}, status=500)
        # elif slave == -2:
        #     return JsonResponse({"message": "RAM not numeric"}, status=500)

        new_instance = Instance(slave_id=slave.id, user=user)
        new_instance.status = 'CR'
        new_instance.name = request['name']
        new_instance.RAM = int(request['memory'])
        new_instance.CPU = int(request['cpu'])
        new_instance.save()

        slave_response = req.post('http://{}}/lc_slave/start_instance/'.format(slave.URL),
                                  data=json.dumps({
                                      'instance_id': new_instance.id,
                                      'image': image.actual_name,
                                      'cpu': request['cpu'],
                                      'memory': request['memory']
                                  }),
                                  headers={
                                      'content-type': 'application/json'
                                  })

        # slave_response = req.get('http://localhost:8001/lc_slave/start_instance/{}'.format(1))
        slave_response = slave_response.json()

        new_instance.IP = slave.IP
        new_instance.slave_id = slave.id
        new_instance.ssh_port = int(slave_response['ssh_port'])
        new_instance.status = 'RU'
        new_instance.save()

        slave.cpu_remaining -= request['cpu']
        slave.memory_used += request['memory']
        slave.save()

    except KeyError:
        return JsonResponse({"message": "Instance Details not correct."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "requested user does not exists."}, status=400)
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
        slave = Slave.objects.get(pk=instance.slave_id)
        slave_response = req.post('{}/lc_slave/start_instance/'.format(instance.IP),
                                  data=json.dumps({
                                      'instance_id': instance.id,
                                  }),
                                  headers={
                                      'content-type': 'application/json'
                                  })

        if slave_response.status_code == 400:
            return JsonResponse({"message": "Instance not found"}, status=400)
        slave_response = slave_response.json()
        slave.cpu_remaining += instance.CPU
        slave.memory_used -= instance.memory_used
        slave.save()

    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance for requested ID= {} does not exists.".format(pk)}, status=400)
    return JsonResponse({"message": slave_response['message']}, status=200)


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
        url = current_instance.URL
        slave_response = req.get('{}/get_instance_resource/{}'.format(url, current_instance.id))
        if slave_response.status_code == 500:
            return JsonResponse({"message": "Slave running the instance gave Error"}, status=500)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance does not exists for given ID"}, status=200)
    return JsonResponse(
        {
            "message": "Returns resource usage",
            "memory": slave_response.json()['memory'],
            "cpu": slave_response.json()['cpu']
        }, status=200)


def login(request):
    request = json.loads(request.body.decode('UTF-8'))
    try:
        username = request['username']
        password = request['password']
        user = User.objects.get(username=username)
    except KeyError:
        return JsonResponse({"message": "Incomplete data"}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid username"}, status=400)
    if user.password != password:
        return JsonResponse({"message": "Invalid password"}, status=400)
    return JsonResponse({"message": "Successfully logged in"}, status=200)


def signup(request):
    request = json.loads(request.body.decode('UTF-8'))
    try:
        user_details = request
        if User.objects.filter(username=user_details['username']).exists():
            return JsonResponse({"message": "User with username={} already exists".
                                format(user_details['username'])}, status=400)
        User(username=user_details['username'], password=user_details['password'],
             first_name=user_details['name'], email=user_details['email']).save()
        return JsonResponse({"message": "Successfully signed up"}, status=200)
    except KeyError:
        return JsonResponse({"message": "Incomplete data"}, status=200)
