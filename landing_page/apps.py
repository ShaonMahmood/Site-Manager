from __future__ import unicode_literals

import warnings

from django.apps import AppConfig

from django.db import ProgrammingError, OperationalError, IntegrityError




class ListenersBindingWarning(Warning):
    pass


class LandingPageConfig(AppConfig):
    name = 'landing_page'

    def ready(self):

        try:
            from . import receivers
        except (ProgrammingError, OperationalError) as err:
            warnings.warn(str(err), ListenersBindingWarning)
