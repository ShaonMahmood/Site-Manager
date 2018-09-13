
import warnings

from django.conf import settings
from django.apps import AppConfig
from django.core.exceptions import ObjectDoesNotExist
from django.db import ProgrammingError, OperationalError, IntegrityError


class GroupCreationWarning(Warning):
    pass


class SiteCreationWarning(Warning):
    pass


class ListenersBindingWarning(Warning):
    pass


class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        print('create group')
        try:
            import dashboard.listeners
        except (ProgrammingError, OperationalError) as err:
            warnings.warn(str(err), ListenersBindingWarning)

        try:
            from django.contrib.auth.models import Group
            for group_name in settings.PROFILE_GROUPS:
                Group.objects.get_or_create(name=group_name)
        except (ProgrammingError, OperationalError) as err:
            warnings.warn(str(err), GroupCreationWarning)

        try:
            from django.contrib.sites.models import Site
            site = Site.objects.get(id=1)
            for field, value in settings.DEFAULT_SITE.items():
                setattr(site, field, value)
            site.save()
            for serving_site in settings.ALL_SITES:
                try:
                    Site.objects.get_or_create(**serving_site)
                except IntegrityError as err:
                    warnings.warn(str(err), SiteCreationWarning)
        except (ProgrammingError, OperationalError, ObjectDoesNotExist) as err:
            warnings.warn(str(err), SiteCreationWarning)
