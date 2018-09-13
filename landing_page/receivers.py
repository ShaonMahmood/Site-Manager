from django.dispatch import receiver
from .signals import *

@receiver(unique_name)
def unique_name_appended_to_domain(sender, instance, domain, **kwargs):
    print("instance.instance_name: ",instance.instance_name)
    instance.instance_name = domain + "-" + instance.instance_name

    instance.save(update_fields=["instance_name"])