# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import os
from django.apps import apps
from django.utils import lru_cache
from django.utils._os import upath
from django.contrib.sites.models import Site
from django.template.utils import get_app_template_dirs
from django.template.loaders.filesystem import Loader as BaseFilesystemLoader


class FilesystemLoader(BaseFilesystemLoader):

    def get_template_sources(self, template_name, template_dirs=None):
        print("get_template_sources: ", template_name, template_dirs)
        domain = Site.objects.get_current().domain
        print('get_template_sources:', domain)
        # print('template_name: {0}'.format(template_name))
        for tname in (os.path.join(domain, template_name), template_name):
            print('->>: ', template_name)
            for item in super(FilesystemLoader, self).get_template_sources(tname, template_dirs):
                yield item


@lru_cache.lru_cache()
def get_app_template_dirs(dirname):
    """
    Return an iterable of paths of directories to load app templates from.

    dirname is the name of the subdirectory containing templates inside
    installed applications.
    """
    template_dirs = []
    for app_config in apps.get_app_configs():
        if not app_config.path:
            continue
        template_dir = os.path.join(app_config.path, dirname)
        if os.path.isdir(template_dir):
            template_dirs.append(upath(template_dir))
    # Immutable return value because it will be cached and shared by callers.
    return tuple(template_dirs)


class AppDirectoriesLoader(BaseFilesystemLoader):

    def get_dirs(self):
        # domain = Site.objects.get_current().domain
        return get_app_template_dirs('templates')

