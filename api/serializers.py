

def user_to_dict(user):
    user_detail = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": user.first_name
    }
    return user_detail


def instance_to_dict(instance):

    instance_detail = {
        "id": instance.id,
        "subordinate_id": instance.subordinate_id,
        "image": {
            "image_name": instance.image.image_name,
            "actual_name": instance.image.actual_name,
            "description": instance.image.description
        },
        "user": user_to_dict(instance.user),
        "name": instance.name,
        "IP": instance.IP,
        "URL": instance.URL,
        "RAM": instance.RAM,
        "cpu": instance.CPU,
        "ports": instance.ports,
        "ssh_port": instance.ssh_port,
        "status": instance.status,
    }
    return instance_detail


def instances_to_dict(instances):
    instance_detail = []

    for instance in instances:
        instance_detail.append(instance_to_dict(instance))

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


def subordinate_to_dict(subordinates):
    subordinate_detail = []

    for subordinate in subordinates:
        subordinate_detail.append({
            "id": subordinate.id,
            "name": subordinate.name,
            "IP": subordinate.IP,
            "URL": subordinate.URL,
            "RAM": subordinate.RAM,
            "CPU": subordinate.CPU,
            "cpu_remaining": subordinate.cpu_remaining,
            "memory_used": subordinate.memory_used
        })

    return subordinate_detail
