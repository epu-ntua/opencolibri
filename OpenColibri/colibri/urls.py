from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.conf import settings

from haystack.query import SearchQuerySet
from lists import *
from haystack.views import search_view_factory
# from colibri.api import *
from colibri import api, api_public_v1
#from organizations.backends import invitation_backend
from tastypie.api import Api
from forms import *
import views
from fileHandlingView import *
from django.contrib import admin
from voting.views import vote_on_object
# from haystack.views import SearchView, search_view_factory
from colibri.models import DatasetRequests
from django.views.generic import RedirectView
from wiki.urls import get_pattern as get_wiki_pattern
from django_notify.urls import get_pattern as get_notify_pattern
from djangoratings.views import AddRatingFromModel

admin.autodiscover()

colibri_api = Api(api_name='colibri')
colibri_api.register(api.OrganizationResource())
colibri_api.register(api.OrganizationUserResource())
colibri_api.register(api.UserResource())
colibri_api.register(api.ListResource())
colibri_api.register(api.ExtensionGraphResource())
colibri_api.register(api.DatasetResource())
colibri_api.register(api.ResourceResource())
colibri_api.register(api.DatasetApiResource())

colibri_api_public_v1 = Api(api_name='v1')
colibri_api_public_v1.register(api_public_v1.UserResource())
colibri_api_public_v1.register(api_public_v1.ListResource())
colibri_api_public_v1.register(api_public_v1.DatasetResource())
colibri_api_public_v1.register(api_public_v1.DatasetApiResource())
colibri_api_public_v1.register(api_public_v1.VisualizationResource())
colibri_api_public_v1.register(api_public_v1.ResourcesResource())
colibri_api_public_v1.register(api_public_v1.ApplicationResource())

datasetrequests_dict = {
'model': DatasetRequests,
'template_object_name': 'datasetrequests',
'allow_xmlhttprequest': True,
'template_name': 'request.html',
}

sqs = SearchQuerySet().facet('country')
sqs = sqs.facet('categories')
sqs = sqs.facet('publisher')
sqs = sqs.facet('license')
sqs = sqs.facet('views')
sqs = sqs.facet('format')

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^datasetrequests/$', views.DatasetRequestListView.as_view(), name='datasetrequests_index'),
                       url(r'^datasetrequests/new/$', views.request_new, name='datasetrequests_new'),
                       url(r'^datasetrequests/(?P<pk>\d+)/$', views.DatasetRequestDetailView.as_view(),
                           name='datasetrequests_details'),
                       url(r'^datasetrequests/', include('fluent_comments.urls')),
                       url(r'^datasetrequests/vote/(?P<request_id>\d+)/(?P<direction>up|down|clear)$',
                           views.request_vote, name='datasetrequests_vote'),
                       url(r'^datasetrequests/answer/(?P<request_id>\d+)/(?P<comment_id>\d+)$',
                           views.request_acceptanswer, name='datasetrequests_acceptanswer'),
                       url(r'^profile/(?P<pk>\d+)/$', login_required(views.profile), name='profile'),
                       url(r'^terms/$', views.terms, name='terms'),
                       url(r'^about/$', views.about, name='about'),
                       url(r'^contact/$', views.contact, name='contact'),
                       url(r'^community$', views.community, name='community'),
                       url(r'^users$', login_required(views.UserListView.as_view()), name='users'),
                       # url(r'^/message/send/(?P<pk>\d+)/$', login_required(views.UserListView.as_view()), name='users'),
                       # url(r'^dataset-search/$', views.DatasetListView.as_view(), name='dataset_search'),
                       url(r'^dataset-search/$',
                           views.DatasetFacetedSearchView(form_class=DatasetFacetedSearchForm, searchqueryset=sqs),
                           name='dataset_search'),
                       url(r'^dataset/(?P<pk>\d+)/$', views.DatasetDetailView.as_view(), name='dataset_details'),
                       url(r'^dataset/(?P<pk>\d+)/edit$', login_required(views.DatasetUpdateView.as_view()),
                           name='dataset_edit'),
                       url(r'^dataset/(?P<pk>\d+)/delete$', login_required(views.DatasetDeleteView.as_view()),
                           name='dataset_delete'),
                       url(r'^dataset/(?P<pk>\d+)/extend/(?P<extension_attempt>\d+)$',
                           login_required(views.dataset_extend), name='dataset_extend'),
                       url(r'^dataset/add', login_required(views.dataset_add), name='dataset_add'),
                       url(r'^dataset/(?P<pk>\d+)/extend/modal$', login_required(views.dataset_extend_modal),
                           name='dataset_extend_modal'),
                       url(r'^dataset/(?P<pk>\d+)/increase-popularity$', views.dataset_increase_popularity,
                           name='dataset_increase_popularity'),
                       # Visualizations
                       #     url(r'^visual/$', views.visual, name='visual'), #ONLY FOR TESTING PURPOSES
                       #     url(r'^resources/$', views.visualjson, name='visualjson'), #ONLY FOR TESTING PURPOSES

                       # Visualizations STABILIZE
                       url(r'^views/(?P<pk>\d+)/$', views.evisuals, name='views'), #ONLY FOR TESTING PURPOSES
                       url(r'^views/(?P<pk>\d+)/saved/(?P<saved>\d+)/$', views.evisualsSaved, name='viewsSaved'),
                       url(r'^eresources/(?P<pk>\d+)/$', views.evisualjsons, name='visualjsons'),
                       #ONLY FOR TESTING PURPOSES
                       url(r'^eresources/(?P<pk>\d+)/saved/(?P<saved>\d+)/$', views.evisualjsonsSaved,
                           name='visualjsonsAfterSaved'),
                       url(r'^refineview/(?P<pk>\d+)/$', views.dataset_details_view, name='testingdatasetview'),
                       url(r'^csvviewer/(?P<pk>\d+)/$', views.csvviewer, name='csvviewer'),
                       url(r'^analyze/$', views.analyze, name='analyze'),
                       url(r'^externalvis/(?P<application_pk>\d+)/$', views.externalvis, name='externalvis'),
                       # LINKED DATA
                       url(r'^sparql/', views.sparql, name='sparql'),
                       url(r'^ontowiki/$', views.ontowiki, name='ontowiki'),
                       #ratings
                       url(r'rate-dataset/(?P<object_id>\d+)/(?P<score>\d+)/', AddRatingFromModel(),
                           {'app_label': 'colibri', 'model': 'dataset', 'field_name': 'rating', }),
                       url(r'^dataset/(?P<pk>\d+)/ratedialog/modal$', login_required(views.dataset_rate_modal),
                           name='dataset_rate_modal'),
                       url(r'^dataset/(?P<pk>\d+)/rateviewdialog/modal$', login_required(views.dataset_rate_view_modal),
                           name='dataset_rate_view_modal'),
                       #    url(r'^portal/add', login_required(views.portal_add), name='portal_add'),
                       url(r'^accounts/', include('allauth.urls')),
                       url(r'^opendatasites$', views.opendatasites, name='opendatasites'),
                       url(r'^group/add', login_required(views.group_add), name='group_add'),
                       url(r'^group-name-validate/$', 'ajax_validation.views.validate', {'form_class': GroupForm},
                           'group_name_validate'),
                       url(r'^groups/', include('organizations.urls')),
                       (r'^i18n/', include('django.conf.urls.i18n')),
                       url(r'^profile/(?P<pk>\w+)/edit$', login_required(views.UserUpdateView.as_view()),
                           name='profile_edit'),
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^api/', include(colibri_api.urls)),
                       (r'^api/public/', include(colibri_api_public_v1.urls)),
                       (r'^messages/', include('messages.urls')),
                       (r'^s/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.STATIC_DOC_ROOT}),
                       url(r'^rosetta/', include('rosetta.urls')),
                       #Applications
                       url(r'^application/$', views.ApplicationListView.as_view(), name='application_index'),
                       url(r'^application/(?P<pk>\d+)/$', views.ApplicationDetailView.as_view(),
                           name='application_details'),
                       # url(r'^$', 'colibri.views.home', name='home'),
                       # url(r'^colibri/', include('colibri.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),

                       # (r'^search/autocomplete/',views.autocomplete),
                       # (r'autocomplete/',views.autocomplete_template),

                       # url(r'^searchApp$', views.search, name='searchApp'),
                       # (r'^appsearch/$', 'colibri.colibri.searchApp.searchApp.views.search'),
                       # (r'^search/', include('haystack.urls')),
                       # url(r'^search/person/', search_view_factory(
                       #     view_class=SearchView,
                       #     template='autocomplete.html',
                       #     form_class=AutocompleteModelSearchForm
                       # ), name='autocomplete'),
                       url(r'^wiki/', get_wiki_pattern()),
                       url(r'^notify/', get_notify_pattern()),
                       (r'^favicon\.ico$', RedirectView.as_view(url='/s/imgs/favicon.ico')),
                       url(r'^datastories', include('articles.urls')),

)
