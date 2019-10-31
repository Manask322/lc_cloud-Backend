

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
        "slave_id": instance.slave_id,
        "user": user_to_dict(instance.user),
        "name": instance.name,
        "IP": instance.IP,
        "URL": instance.URL,
        "RAM": instance.RAM,
        "CPU_usage": instance.CPU,
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


def slave_to_dict(slaves):
    slave_detail = []

    for slave in slaves:
        slave_detail.append({
            "id": slave.id,
            "name": slave.name,
            "IP": slave.IP,
            "URL": slave.URL,
            "RAM": slave.RAM,
            "CPU": slave.CPU,
            "cpu_remaining": slave.cpu_remaining,
            "memory_used": slave.memory_used
        })

    return slave_detail
