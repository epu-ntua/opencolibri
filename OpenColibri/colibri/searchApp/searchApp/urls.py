__author__ = 'mpetyx'

from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

                       url(r'^admin/', include(admin.site.urls)),

                       (r'^appsearch/$', 'searchApp.views.searchApp'),
                       (r'^search_dataset/$', 'searchApp.views.search_dataset'),
                       (r'^search/', include('haystack.urls')),

)