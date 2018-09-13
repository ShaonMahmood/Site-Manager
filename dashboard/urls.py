from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^formInfo/$', views.site_form_list, name='form_list'),

    # url(r'^formInfo/add/$', views.site_form_list_create, name='form_data_add'),

    #url(r'^formInfo2/add/$', views.site2_form_list_create, name='form2_data_add'),

    # url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/(?P<page_item_type>[a-z_]+)/(?P<page_item_id>\d+)/AddFaqsFeatures/$',
    #     views.site2_form_list_create, name='form2_data_add'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/$', views.site_settings, name='site_settings'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/edit/$', views.edit_site_info, name='edit_site_info'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/$',
        views.settings_page, name='settings_page'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/edit/$',
        views.edit_page, name='edit_page'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/(?P<page_item_type>[a-z_]+)/(?P<page_item_id>\d+)/edit/$',
        views.edit_page_item, name='edit_page_item'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/(?P<page_item_type>[a-z_]+)/(?P<page_item_id>\d+)/AddFaqsFeatures/$',
        views.site2_form_list_create, name='form2_data_add'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/template(?:/(?P<app_label>[a-z_]+))?(?:/(?P<page_name>[a-z\-]+))?/$',
        views.templates, name='template'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/staticfiles(?:/(?P<app_label>[a-z_]+))?(?:/(?P<file_name>[a-z.\-]+))?/$',
        views.static_files, name='static_files'),

    # url(r'^(?P<domain>[a-z0-9\-.]+)/(?P<app_label>[a-z_]+)/(?P<model_name>[a-z]+)(?:/(?P<action>add))?/$',
    #     views.site_settings_items, name='site_settings_items'),
    #
    # url(r'^(?P<domain>[a-z0-9\-.]+)/(?P<app_label>[a-z_]+)/(?P<model_name>[a-z]+)/(?P<pk>\d+)/(?P<action>change)/$',
    #     views.site_settings_items, name='site_settings_items'),
    #url(r'^show/$', views.show,name='show'),
    url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/available/$',
        views.available, name='available'),

    url(r'^(?P<domain>[a-z0-9\-.]+)/page/(?P<page_name>[a-z_]+)/available/show/$',
        views.show, name='show'),

    url(r'^tinymceupload/$', views.tinymce_upload, name='writing-fileupload'),

]
