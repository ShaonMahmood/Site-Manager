from django import http
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.deprecation import MiddlewareMixin


class MultiSiteMiddleware(MiddlewareMixin):

    def process_request(self, request):
        host = request.get_host().replace('www.', '')
        print('MultiSiteMiddleware host: {0}'.format(host))
        try:
            site = Site.objects.get(domain=host)
            settings.SITE_ID = site.id
            Site.objects.clear_cache()
            return
        except Site.DoesNotExist:
            return http.HttpResponseRedirect('http://localsite.com/admin/')
