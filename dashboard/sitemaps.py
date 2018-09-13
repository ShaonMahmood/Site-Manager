from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.contrib.sites.models import Site

from .models import Page


class PageSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        site = Site.objects.get_current()
        return Page.objects.filter(published=True, site_info=site.siteinfo_set.get())

    def priority(self, item):
        if item.page_name == 'index':
            return 1.0
        return 0.8

    def lastmod(self, item):
        return item.date_edited
