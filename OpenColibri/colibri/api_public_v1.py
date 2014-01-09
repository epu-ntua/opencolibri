__author__ = 'mpetyx'

import urllib

from tastypie.resources import ModelResource, Resource, ALL
from tastypie import fields
from django.contrib.auth.models import User
from tastypie.utils import trailing_slash
from django.conf.urls.defaults import url
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from django.http import HttpResponse
from django.db.models import Q
import simplejson

from library import *
from organizations.models import *
from models import Dataset, Application
import models
import lists
import colibri
from lists import *


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        resource_name = 'users';


class OrganizationResource(ModelResource):
    class Meta:
        queryset = Organization.objects.all()


class ApplicationResource(ModelResource):
    class Meta:
        queryset = Application.objects.all()
        resource_name = "applications"


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


class DatasetResource(ModelResource):
    uploader = fields.ForeignKey(UserResource, 'uploader', full=True)
    maintainingGroup = fields.ForeignKey(OrganizationResource, "maintainingGroup", full=True, null=True)
    # uploader = fields.ForeignKey(bundle.user, 'uploader', full=True)
    # uploader = fields.ToOneField(bundle.user, 'uploader', full=True)
    # resources = fields.ToManyField('colibri.api.ResourceResource', 'resources', full=True)

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'datasets'
        limit = 20
        ordering = ALL
        filtering = {
            "title": ALL,
            "description": ALL,
            "maintainingGroup": ALL,
            "author": ALL,
            "country": ALL,
            "uploader": ALL,
        }

        # authentication = ApiKeyAuthentication()
        authorization = Authorization()

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

    def dehydrate_categories(self, bundle):
        return bundle.obj.get_categories_display()

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

        list_allowed_methods = ['get', 'post']


class VisualizationResource(ModelResource):
    class Meta:

        queryset = Dataset.objects.all()
        resource_name = 'visualization'


    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/(?P<dataset_id>\d+)/json%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('json'), name="json"),
            url(r"^(?P<resource_name>%s)/(?P<dataset_id>\d+)/visual%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('visual'), name="visual"),
        ]

    def json(self, request, **kwargs):

        dataset_id = kwargs.get('dataset_id')

        """
        display the whole row
        """


    def visual(self, request, **kwargs):
        # dataset = Dataset.objects.get(pk=pk)
        #Load the JSON object

        """
        handling the json dataset
        """

        # jsondata = JsonCreator.Final(dataset)

        dataset_id = kwargs.get('dataset_id')

        from jsonHandler import generatingJsonFormat
        # json_data = generatingJsonFormat.ExcelHandling().result()
        from models import Resource, Dataset

        dataset = Dataset.objects.get(id=dataset_id)
        if dataset.resources:
            resource_id = dataset.resources[0].id
        else:
            return "no dataset found"
        resource = Resource.objects.get(id=resource_id)

        if str(resource.file) == '':
            url = resource.uri
        else:
            url = "https://" + settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/" + str(resource.file)

        if "xls" in url:

            # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
            file = urllib.urlretrieve(url, ".././tmp/skatoula.xls")
            #heroku save
            json_data = generatingJsonFormat.ExcelHandling(file=".././tmp/skatoula.xls").result()

        elif "csv" in url:

            # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
            file = urllib.urlretrieve(url, ".././tmp/skatoula.csv")
            #heroku save
            json_data = generatingJsonFormat.CsvHandling(file=".././tmp/skatoula.csv").result()

        else:
            return "this is not either xls nor csv"

        json_data = simplejson.dumps(json_data)

        if request.method == 'GET':
            response = HttpResponse(json_data, mimetype='application/json')
            response['Content-Disposition'] = "filename=%s" % 'france-elections.json'
            return response

            #Save the JSON object
        if request.method == 'POST':
            if 'filename' in request.POST.keys():
                #Export datagrid to CSV
                csv_data = request.POST['data']
                response = HttpResponse(csv_data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="' + request.POST['filename'] + '"'
                return response
            else:
                # Save Visualization State
                json_data = request.raw_post_data
                #SAVE json_data to Amazon S3
                #.........
                json_file = open('colibri/static/visualizations/france-elections2.json', 'w')
                json_file.write(json_data)
                json_file.close()
                response = HttpResponse(json_data, mimetype='application/json')
                return response


class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(MultipartResource, self).deserialize(request, data, format)


class ResourcesResource(MultipartResource, ModelResource):
    # file = fields.FileField(attribute="file", null=True, blank=True)
    dataset = fields.ForeignKey(DatasetResource, 'dataset', full=True)

    class Meta:
        always_return_data = True
        queryset = models.Resource.objects.all()
        resource_name = 'resource'
        allowed_methods = ['get', 'post']
        ordering = ALL
        limit = 20
        filtering = {
            "description": ALL,
            # "file": ALL,
            "format": ALL,
            # "language": ALL,
            "dataset": ALL,
        }
        excludes = ['id']
        include_resource_uri = False
        # authentication = ApiKeyAuthentication()
        # authorization = DjangoAuthorization()
        authorization = Authorization()


class MyResource(ModelResource):
    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'uploading'
        list_allowed_methods = ['get', 'post']
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()