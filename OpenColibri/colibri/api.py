import json

from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from django.contrib.auth.models import User
from tastypie.utils import trailing_slash
from django.conf.urls.defaults import url
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Q
import simplejson
from django.utils.translation import ugettext as _

from library import *
from organizations.models import *
from models import Dataset, DatasetGeoTempContext, DatasetScientificContext
import lists
import colibri
from lists import *


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        resource_name = 'users';


class OrganizationUserResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)

    class Meta:
        queryset = OrganizationUser.objects.all()

    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/leave-group%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('leave_group'), name="leave_group"),
        ]

    def leave_group(self, request, **kwargs):
        if not request.user.is_authenticated():
            return self.create_response(request, {
                'error': 'NotAllowed'
            })
        else:
            a = request.POST['organizationID']
            organization = Organization.objects.get(id=request.POST['organizationID'])
            role = get_role_for_user(self, request.user, organization)
            if (role == 'Member' or role == 'Admin'):
                organizationUser = OrganizationUser.objects.filter(organization_id=organization.id,
                                                                   user_id=request.user.id)
                organizationUser.delete()
                return self.create_response(request, {
                    'success': 'True'
                })
            else:
                return self.create_response(request, {
                    'error': 'NotAllowed'
                })
        try:
            organizations = Organization.objects.filter(is_active=1)
        except Organization.DoesNotExist:
            organizations = {}
        return self.create_response(request, {
            'groups': json_organizations(self, request, organizations)
        })


class OrganizationResource(ModelResource):

#    users = fields.ToManyField(OrganizationUserResource,
#        attribute=lambda bundle: bundle.obj.users.through.objects.filter(
#            organization=bundle.obj) or bundle.obj.users, full=True)

    class Meta:
        filtering = {"is_active": ALL}
        queryset = Organization.objects.all()
        list_allowed_methods = ['get']


    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/all%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('all'), name="all"),
            url(r"^(?P<resource_name>%s)/i-admin%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('i_admin'), name="i_admin"),
            url(r"^(?P<resource_name>%s)/i-member%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('i_member'), name="i_member"),
        ]

    def all(self, request, **kwargs):
        try:
            organizations = Organization.objects.filter(is_active=1)
        except Organization.DoesNotExist:
            organizations = {}
        return self.create_response(request, {
            'groups': json_organizations(self, request, organizations)
        })

    def i_admin(self, request, **kwargs):
        organization_ids = []
        organizationUsers = OrganizationUser.objects.filter(user_id=request.user.id, is_admin=1)
        if (not organizationUsers):
            organizationUsers = {}
        for organizationUser in organizationUsers:
            organization_ids.append(organizationUser.organization_id)

        organizations = Organization.objects.filter(id__in=organization_ids)
        return self.create_response(request, {
            'groups': json_organizations(self, request, organizations)
        })

    def i_member(self, request, **kwargs):
        organization_ids = []
        organizationUsers = OrganizationUser.objects.filter(user_id=request.user.id)
        if (not organizationUsers):
            organizationUsers = {}
        for organizationUser in organizationUsers:
            organization_ids.append(organizationUser.organization_id)
        organizations = Organization.objects.filter(id__in=organization_ids)
        return self.create_response(request, {
            'groups': json_organizations(self, request, organizations)
        })


def get_role_for_user(caller, user, organization):
    try:
        organizationUser = OrganizationUser.objects.get(organization_id=organization.id, user_id=user.id)
    except (OrganizationUser.DoesNotExist):
        organizationUser = None
    if (not organizationUser):
        return 'Not A Member'
    if (OrganizationOwner.objects.filter(organization_id=organization.id, organization_user=organizationUser)):
        return 'Owner'
    return 'Admin' if organizationUser.is_admin else 'Member'


def json_organizations(caller, request, organizations):
    return json.dumps([{
                           'requesterID': request.user.id,
                           'name': organization.name,
                           'role': get_role_for_user(caller, request.user, organization),
                           'id': organization.id,
                           'url': organization.get_absolute_url(),
                           'users': json.dumps([{
                                                    'userID': user.id,
                                                    'username': user.username,
                                                    'firstName': user.first_name,
                                                    'lastName': user.last_name,
                                                    'email': user.email,
                                                    'role': get_role_for_user(caller, user, organization),
                                                }
                                                for user in organization.users.all()], indent=4,
                                               separators=(',', ': ')),
                       } for organization in organizations], indent=4, separators=(',', ': '));


LIST_MAPPINGS = {
    'licenses': {
        'columnName': 'license',
        'table': 'Dataset',
        'list': 'LICENSES'
    },
    'tempGranularities': {
        'columnName': 'temporal_granularity',
        'table': 'DatasetGeoTempContext',
        'list': 'TEMPORAL_GRANULARITY'
    },
    'geoGranularities': {
        'columnName': 'geographical_granularity',
        'table': 'DatasetGeoTempContext',
        'list': 'SPATIAL_GRANULARITY'
    },
    'dataCollectionTypes': {
        'columnName': 'data_collection_type',
        'table': 'DatasetScientificContext',
        'list': 'DATACOLLECTION_METHOD'
    },
    'softwarePackages': {
        'columnName': 'software_package',
        'table': 'DatasetScientificContext',
        'list': 'SOFTWARE_PACKAGE'
    },
    'analysisUnits': {
        'columnName': 'analysis_unit',
        'table': 'DatasetScientificContext',
        'list': 'ANALYSIS_UNITS'
    }
}


class ListResource(Resource):
    class Meta:
        list_allowed_methods = ['get']

    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/licenses%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('genericDistinctList'), name="licenses"),
            url(r"^(?P<resource_name>%s)/tempGranularities%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('genericDistinctList'), name="tempGranularities"),
            url(r"^(?P<resource_name>%s)/geoGranularities%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('genericDistinctList'), name="geoGranularities"),
            url(r"^(?P<resource_name>%s)/dataCollectionTypes%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('genericDistinctList'), name="dataCollectionTypes"),
            url(r"^(?P<resource_name>%s)/softwarePackages%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('genericDistinctList'), name="softwarePackages"),
            url(r"^(?P<resource_name>%s)/analysisUnits%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('genericDistinctList'), name="analysisUnits"),
            url(r"^(?P<resource_name>%s)/publishers%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('publishers'), name="publishers"),
            url(r"^(?P<resource_name>%s)/authors%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('author'), name="author"),
            url(r"^(?P<resource_name>%s)/extension%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('extension'), name="extension"),
            url(r"^(?P<resource_name>%s)/extensionrequests%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('extensionrequests'), name="extensionrequests"),
            url(r"^(?P<resource_name>%s)/titles%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('title'), name="title"),
            url(r"^(?P<resource_name>%s)/datasetCountries%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('datasetCountries'), name="datasetCountries"),
            url(r"^(?P<resource_name>%s)/datasetUploaders%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('datasetUploaders'), name="datasetUploaders"),
            url(r"^(?P<resource_name>%s)/datasetLanguages%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('datasetLanguages'), name="datasetLanguages"),
        ]

    def genericDistinctList(self, request, **kwargs):
        humanReadableName = array_explode('/', request.path).pop(4)
        columnName = LIST_MAPPINGS[humanReadableName]['columnName']
        modelList = []
        model = eval(LIST_MAPPINGS[humanReadableName]['table'])
        distinctValuesInDatabase = model.objects.values(columnName).distinct()
        defaultValuesInLists = getattr(lists, LIST_MAPPINGS[humanReadableName]['list'])
        for value in defaultValuesInLists:
            modelList.append(value[-1])
        for distinctValueInDatabase in distinctValuesInDatabase:
            if distinctValueInDatabase[columnName] not in defaultValuesInLists:
                modelList.append(distinctValueInDatabase[columnName])
        return self.create_response(request, {
            humanReadableName: modelList
        })

    def title(self, request, **kwargs):
        titles = []
        distinctTitles = Dataset.objects.values('title').distinct()
        for title in distinctTitles:
            titles.append(title['title'])
        return self.create_response(request, {
            'title': titles
        })

    def datasetCountries(self, request, **kwargs):
        countries = []
        distinctCountries = Dataset.objects.values('country').distinct()
        countriesList = dict(COUNTRIES)
        for dataset in distinctCountries:
            countries.append({'code': '' if dataset['country'] == '--' else dataset['country'],
                              'name': '' if dataset['country'] == '--' else countriesList[dataset['country']]})
        return self.create_response(request, {
            'country': countries
        })

    def datasetUploaders(self, request, **kwargs):
        uploaders = []
        distinctUploaders = Dataset.objects.values('uploader').distinct()
        users = User.objects.filter(id__in=distinctUploaders)
        uploaders.append({'id': '', 'username': ''})
        for user in users:
            uploaders.append({'id': user.id, 'username': user.username})
        return self.create_response(request, {
            'uploader': uploaders
        })

    def datasetLanguages(self, request, **kwargs):
        languages = []
        distinctLanguages = colibri.models.Resource.objects.values('language').distinct()
        languagesList = dict(LANGUAGES)
        for dataset in distinctLanguages:
            languages.append({'code': '' if dataset['language'] == '--' else dataset['language'],
                              'name': '' if dataset['language'] == '--' else languagesList[dataset['language']]})
        return self.create_response(request, {
            'language': languages
        })

    def author(self, request, **kwargs):
        authors = []
        distinctAuthors = Dataset.objects.values('author').distinct()
        for author in distinctAuthors:
            authors.append(author['author'])
        return self.create_response(request, {
            'author': authors
        })

    def publishers(self, request, **kwargs):
        publishers = []
        distinctPublishers = Dataset.objects.values('publisher').distinct()
        for publisher in distinctPublishers:
            publishers.append(publisher['publisher'])
        return self.create_response(request, {
            'publishers': publishers
        })

    def extension(self, request, **kwargs):
        extensions = lists.EXTENSION_DESCRIPTION
        return self.create_response(request, {
            'extension_description': extensions[request.GET['extension']]
        })

    def extensionrequests(self, request, **kwargs):
        extensionrequests = lists.REQUEST_DESCRIPTION
        return self.create_response(request, {
            'extension_description': extensionrequests[request.GET['extensionrequests']]
        })


class ExtensionGraphResource(Resource):
    class Meta:
        list_allowed_methods = ['get']

    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/(?P<dataset_id>\d+)/linear%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('linear'), name="linear"),
            url(r"^(?P<resource_name>%s)/(?P<dataset_id>\d+)/tree%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('tree'), name="tree"),
        ]

    def linear(self, request, **kwargs):
        dataset_id = kwargs.get('dataset_id')
        try:
            dataset = Dataset.objects.get(pk=dataset_id)
        except Dataset.DoesNotExist:
            return self.create_response(request, {
                'error': 'Dataset does not exist'
            })
        datasets = []
        datasets.append(dataset)
        while dataset.is_revision():
            dataset = dataset.get_parent()
            datasets.append(dataset)
        return self.create_response(request, {
            'extensionGraph':
                json.dumps([{
                                'id': dataset.id,
                                'title': dataset.title,
                                'url': dataset.get_absolute_url()
                            }
                            for dataset in datasets], indent=4, separators=(',', ': '))
        })

    def tree(self, request, **kwargs):
        dataset_id = kwargs.get('dataset_id')

        try:
            dataset = Dataset.objects.get(pk=dataset_id)
        except Dataset.DoesNotExist:
            return self.create_response(request, {
                'error': 'Dataset does not exist'
            })
        dataset = dataset.get_original()
        datasets = dataset.get_all_children()
        return self.create_response(request, {
            'extensionTreeGraph':
                simplejson.dumps(datasets)
        })


class ResourceResource(ModelResource):
    class Meta:
        queryset = colibri.models.Resource.objects.all()
        resource_name = 'resource'

    def dehydrate_language(self, bundle):
        return {'code': '', 'name': ''} if bundle.obj.language == '--' else {'code': bundle.obj.language,
                                                                             'name': bundle.obj.get_language_display()};


class DatasetResource(ModelResource):
    uploader = fields.ForeignKey(UserResource, 'uploader', full=True)
    resources = fields.ToManyField('colibri.api.ResourceResource', 'resources', full=True)

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'datasets'
        limit = 20
        ordering = ALL
        filtering = {
            "title": ALL,
            "description": ALL,
            "author": ALL,
            "country": ALL,
            "uploader": ALL,
        }

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(DatasetResource, self).build_filters(filters)

        if ('language' in filters):
            language = filters['language']
            if (language != ""):
                qset = (
                    Q(resource__language=language)
                )
                orm_filters.update({'language': qset})
        if ('value' in filters):
            value = filters['value']
            if (value != ""):
                qset = (
                    Q(title__icontains=value) | Q(description__icontains=value)
                )
                orm_filters.update({'value': qset})
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'language' in applicable_filters:
            custom = applicable_filters.pop('language')
        elif 'value' in applicable_filters:
            custom = applicable_filters.pop('value')
        else:
            custom = None

        semi_filtered = super(DatasetResource, self).apply_filters(request, applicable_filters)

        return semi_filtered.filter(custom) if custom else semi_filtered

    # def dehydrate_categories(self, bundle):
    #     return bundle.obj.get_categories_display()

    def dehydrate_country(self, bundle):
        return {'code': '', 'name': ''} if bundle.obj.country == '--' else {'code': bundle.obj.country,
                                                                            'name': bundle.obj.display_country()};


class DatasetApiResource(ModelResource):
    uploader = fields.ForeignKey(UserResource, 'uploader', full=True)
    resources = fields.ToManyField('colibri.api.ResourceResource', 'resources', full=True)

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'datasetsapi'
        limit = 10
        ordering = ALL
        filtering = {
            "title": ALL,
            "description": ALL,
            "author": ALL,
            "country": ALL,
            "uploader": ALL,
        }

        list_allowed_methods = ['get']