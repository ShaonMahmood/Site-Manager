# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-23 00:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20171019_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteinfo',
            name='site_analytics_js',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='siteinfo',
            name='site_meta_webmaster',
            field=models.TextField(blank=True, null=True),
        ),
    ]
