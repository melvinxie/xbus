from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

js_info_dict = {
    'packages': ('ja',),
}

urlpatterns = patterns('',
    # Example:
    # (r'^kyoto-bus/', include('kyoto-bus.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^$', 'timetables.views.index'),
    (r'^direction/$', 'directions.views.direction'),
    (r'^nearby/$', 'stations.views.nearby'),
    (r'^list/(?P<key>\w+)/$', 'stations.views.list'),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)
