
import os
import shlex
import shutil
import subprocess
from string import Template

from django.conf import settings
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.db.models.signals import pre_save, post_save

from dashboard.models import SiteInfo


@receiver(pre_save, sender=Site)
def site_pre_save(sender, **kwargs):
    print('site_pre_save: ', sender)
    instance = kwargs.get('instance')

    if instance.id:
        template_path = settings.MULTI_SITE_TEMPLATE_DIR
        static_path = settings.STATIC_ROOT
        obj = sender.objects.get(id=instance.id)
        domain = obj.domain
        if (os.path.isdir(os.path.join(template_path, domain)) and instance.domain != domain
                and (not os.path.isdir(os.path.join(template_path, instance.domain)))):
            print("have to mode site template dir")
            shutil.copytree(os.path.join(template_path, domain), os.path.join(template_path, instance.domain))

        if (os.path.isdir(os.path.join(static_path, domain)) and instance.domain != domain
                and (not os.path.isdir(os.path.join(static_path, instance.domain)))):
            print("have to mode site template dir")
            shutil.copytree(os.path.join(static_path, domain), os.path.join(static_path, instance.domain))

    else:   #When there is no existing instance or site
        template_path = settings.MULTI_SITE_TEMPLATE_DIR
        new_template_path = settings.NEW_SITE_DEFAULT_TEMPLATE_PATH
        if (os.path.isdir(new_template_path)
                and (not os.path.isdir(os.path.join(template_path, instance.domain)))):
            print("have to mode site template dir")
            shutil.copytree(new_template_path, os.path.join(template_path, instance.domain))
        if instance.domain:
            try:
                nginx_file_edit(instance.domain)
            except Exception as err:
                print("Exception: {0}".format(err))


@receiver(post_save, sender=Site)
def site_post_save(sender, **kwargs):
    print('site_post_save: ', sender)
    instance = kwargs.get('instance')
    print('instance: ', instance.domain, instance.name)

    site_info_obj, created = instance.siteinfo_set.get_or_create()
    if created or site_info_obj.site_title is None:
        site_info_obj.site_title = instance.name
        site_info_obj.save()

    for page_name in settings.DEFAULT_PAGES:
        page, created = site_info_obj.page_set.get_or_create(page_name=page_name)
        if created or page.title is None:
            page.title = site_info_obj.site_title
            page.save()


def nginx_file_edit(new_domain):
    editable_file_name = 'nginx_settings.conf'
    editable_file_dir = '/etc/nginx/sites-enabled/'
    
    temp_string = ""
    file_path = os.path.join(settings.BASE_DIR, 'server_conf', editable_file_name)
    
    try:
        all_sites_from_db = Site.objects.exclude(
            domain='localsite.com'
        ).exclude(domain=new_domain)
        all_sites_string = new_domain + ' www.{0} '.format(new_domain)
        for obj in all_sites_from_db:
            all_sites_string += (obj.domain + " www.{0}".format(obj.domain) + " ")
        # print('****************----------------------------------', all_sites_string)
        try:
            with open(file_path, 'r') as ll:
                lines = ll.read()
                temp_string += lines    #save as string for use later
        except FileNotFoundError:
            print(editable_file_name, " file not found, buddy....")
        
        new_str = Template(temp_string).substitute(all_sites=all_sites_string)
        
        if not os.path.isfile(os.path.join(editable_file_dir, editable_file_name)):
            f = open(editable_file_name, "w+")  # new file create
        else:
            f = open(editable_file_name, "w")
        f.write(new_str)

        # this code below is for nginx restart
        try:
            out_list = list()
            arg = shlex.split("systemctl restart nginx.service")
            proc = subprocess.Popen(arg,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
            out, err = proc.communicate()
            if out:
                out_list = out.strip(" \n").split("\n")
            return out_list, err
        except TypeError as err1:
            print(err1)
    
    except TypeError as err1:
        print(err1)
