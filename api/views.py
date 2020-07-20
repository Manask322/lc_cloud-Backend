import requests as req
import json
from django.http import JsonResponse
from api.serializers import *
from api.models import Image, Instance, Subordinate
from django.contrib.auth.models import User


# subordinate_response = req.get('http://localhost:8001/lc_subordinate/start_instance/1')

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


def decide(subordinates, cpu, memory):
    """
    :param subordinates:
    :param cpu:
    :param memory:
    :return: returns a subordinate node to run a instance
    """
    max_free_memory = -1
    candidate_subordinate = None
    for subordinate in subordinates:
        if subordinate.cpu_remaining < cpu:
            continue
        url = "http://{}/lc_subordinate/get_system_resource/".format(subordinate.URL)
        subordinate_system_resource = req.get(url)
        # if subordinate_system_resource.status_code == 500:
        #     if subordinate_system_resource.json()['message'] == "Internal Server Error":
        #         return -1
        #     elif subordinate_system_resource.json()['message'] == "RAM not numeric":
        #         return -2
        if subordinate_system_resource.status_code == 500:
            continue
        subordinate_system_resource = subordinate_system_resource.json()
        print(subordinate_system_resource)
        host_ram = subordinate_system_resource['host_ram']
        docker_ram = subordinate_system_resource['docker_ram']
        total_ram = subordinate_system_resource['total_ram']
        free_memory = total_ram - (host_ram - docker_ram + subordinate.memory_used)
        print("Subordinate: {}\tFree Memory: {}\tSubordinate memory_used: {}".format(subordinate.name, free_memory, subordinate.memory_used))
        if free_memory >= memory and free_memory > max_free_memory:
            candidate_subordinate = subordinate
            max_free_memory = free_memory
    return candidate_subordinate


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
        subordinates = Subordinate.objects.all()
        image = Image.objects.get(id=request["image"])
        # Write a decide function to choose subordinate.
        print(request)
        subordinate = decide(subordinates, request['cpu'], request['memory'])
        print(subordinate)
        if subordinate is None:
            return JsonResponse({"message": "No resources left to run instance"}, status=500)
        # elif subordinate == -1:
        #     return JsonResponse({"message": "Internal Server Error"}, status=500)
        # elif subordinate == -2:
        #     return JsonResponse({"message": "RAM not numeric"}, status=500)

        new_instance = Instance(subordinate_id=subordinate.id, user=user)
        new_instance.status = 'CR'
        new_instance.name = request['name']
        new_instance.RAM = int(request['memory'])
        new_instance.CPU = int(request['cpu'])
        new_instance.image = image
        new_instance.save()

        subordinate_response = req.post('http://{}/lc_subordinate/start_instance/'.format(subordinate.URL),
                                  data=json.dumps({
                                      'instance_id': new_instance.id,
                                      'image': image.actual_name,
                                      'cpu': request['cpu'],
                                      'memory': request['memory']
                                  }),
                                  headers={
                                      'content-type': 'application/json'
                                  })

        # subordinate_response = req.get('http://localhost:8001/lc_subordinate/start_instance/{}'.format(1))
        print(subordinate_response)
        if subordinate_response.status_code != 200:
            new_instance.delete()
            return JsonResponse({"message": "Subordinate response not correct"}, status=500)
        subordinate_response = subordinate_response.json()
        # print(subordinate_response)
        try:
            subordinate_ssh = int(subordinate_response['ssh_port'])
        except KeyError:
            new_instance.delete()
            return JsonResponse({"message": "Subordinate Response not correct"}, status=500)
        new_instance.IP = subordinate.IP
        new_instance.subordinate_id = subordinate.id
        new_instance.ssh_port = subordinate_ssh
        new_instance.status = 'RU'
        new_instance.save()

        subordinate.cpu_remaining -= request['cpu']
        subordinate.memory_used += request['memory']
        subordinate.save()

    except KeyError:
        return JsonResponse({"message": "Instance Details not correct."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"message": "requested user does not exists."}, status=400)
    return JsonResponse({"message": "Instance stated successfully", "instance_id": new_instance.id}, status=200)


def stop_instance(request, pk):
    """
    Stops the Instance
    :param request:
    :param pk:
    :return:
    """
    try:
        instance = Instance.objects.get(pk=pk)
        subordinate = Subordinate.objects.get(pk=instance.subordinate_id)
        subordinate_response = req.post('http://{}/lc_subordinate/stop_instance/'.format(subordinate.URL),
                                  data=json.dumps({
                                      'instance_id': instance.id,
                                  }),
                                  headers={
                                      'content-type': 'application/json'
                                  })

        if subordinate_response.status_code != 200:
            return JsonResponse({"message": "Instance not found"}, status=500)
        subordinate_response = subordinate_response.json()
        subordinate.cpu_remaining += instance.CPU
        subordinate.memory_used -= instance.RAM
        subordinate.save()
        instance.delete()
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance for requested ID= {} does not exists.".format(pk)}, status=400)
    return JsonResponse({"message": subordinate_response['message']}, status=200)


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
        subordinate = Subordinate.objects.get(id=current_instance.subordinate_id)
        url = subordinate.URL
        subordinate_response = req.get('http://{}/lc_subordinate/get_instance_resource/{}'.format(url, current_instance.id))
        if subordinate_response.status_code == 500:
            return JsonResponse({"message": "Subordinate running the instance gave Error"}, status=500)
    except Instance.DoesNotExist:
        return JsonResponse({"message": "Instance does not exists for given ID"}, status=200)
    return JsonResponse(
        {
            "message": "Returns resource usage",
            "memory": subordinate_response.json()['memory'],
            "cpu": subordinate_response.json()['cpu']
        }, status=200)


def profile(request, username):
    """
    :param username:
    :param request:
    :return: user details
    """
    try:
        user = User.objects.get(username=username)
        user = user_to_dict(user)
    except User.DoesNotExist:
        return JsonResponse({"message": "User details with username = {} not found.".format(username)}, status=400)
    return JsonResponse({"message": "User details found", "user": user}, status=200)


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
