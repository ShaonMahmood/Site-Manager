from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^unsubscribe/$', views.un_subscribe, name='un_subscribe'),
    url(r'^(?:(?P<slug>(privacy|terms|thanks))/)?$', views.index, name='index'),
]
