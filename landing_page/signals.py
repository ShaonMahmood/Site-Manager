import django.dispatch

unique_name = django.dispatch.Signal(providing_args=["instance","domain"])