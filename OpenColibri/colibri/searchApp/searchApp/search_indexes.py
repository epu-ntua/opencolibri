__author__ = 'mpetyx'

import datetime
from haystack import indexes
from models import *

#haystack.autodiscover()


class KouklakiIndex(indexes.SearchIndex):# , indexes., indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    result = indexes.CharField(model_attr='result')
    date_created = indexes.DateTimeField(model_attr='date_created')

    def get_model(self):
        return Kouklaki

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(date_created__lte=datetime.datetime.now())


class PersonIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    username = indexes.CharField(model_attr='username') #Unique identifier of the user, part of their credentials.
    firstName = indexes.CharField(model_attr='firstName') #The user's first name
    lastName = indexes.CharField(model_attr='lastName') #The user's last name
    nameAppearance = indexes.CharField(
        model_attr='nameAppearance') #Information on the way the name is displayed in public (for instance, Dimitris Batis or Dimitris G. Batis or Batis Dimitris)
    city = indexes.CharField(model_attr='city') #User's city of residence
    country = indexes.CharField(model_attr='country')#User's country of residence. PREDEFINED LIST - COUNTRIES
    email = indexes.CharField(model_attr='email') #User's e-mail address.
    scientific_background = indexes.CharField(
        model_attr='scientific_background') # PREDEFINED LIST. LIST "SCIENTIFIC DOMAINS"
    rpg_class = indexes.CharField(model_attr='rpg_class') # Users Pick a class like in rpgs
    date_created = indexes.DateTimeField(model_attr='date_created')

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(date_created__lte=datetime.datetime.now())


class SoftwareApplicationIndex(indexes.SearchIndex):
    """
    A dataset may contain information for any software applications that use the dataset as a source. The information for each application is stored in the extras:applications field, as a list of objects.
    """
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title') #The official title of the application or service.
    url = indexes.CharField(model_attr='url') #The URL where the application is available, or information about it.
    type = indexes.CharField(model_attr='type') #PREDEFIND LIST. LIST "ApplicationType"
    maintainer = indexes.CharField(
        model_attr='maintainer') # POIOS EINAI O MAINTAINER TOU Application - LINK SE PINAKA USERS / USER GROUPS
    date_created = indexes.DateTimeField(model_attr='date_created')


    def get_model(self):
        return SoftwareApplication

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(date_created__lte=datetime.datetime.now())


class DatasetIndex(indexes.SearchIndex):
    """
        The dataset with all the resources attached
        A dataset is a collection of information that originates or derives from public sector information. The information is contained in one or more resources. The dataset may belong to either a single user or a group of users, but as far as CKAN is concerned it belongs just to a CKAN user (which, in reality, can be a group).
    """


    #---------Basic Information------#
    text = indexes.CharField(document=True, use_template=True)
    resources = indexes.CharField(model_attr='resources')#EINAI DYO FORES!
    title = indexes.CharField(model_attr='title')
    nameCKAN = indexes.CharField(
        model_attr='nameCKAN') #A unique slug identifying the dataset. Unfortunately, this is required by CKAN. PRECALCULATED, KEPT ONLY FOR COMPATIBILITY with CKAN.
    description = indexes.CharField(model_attr='description') #Summarizes the contents of the dataset.
    categories = indexes.CharField(model_attr='categories')  #PREDEFINED LIST - LIST "CATEGORIES"
    tags = indexes.CharField(model_attr='tags') #list of keywords - AUTOCOMPLETION
    url = indexes.CharField(
        model_attr='url') #Location of the original dataset (for instance, in the publisher's website).
    published_via = indexes.CharField(
        model_attr='published_via') #Name of the data portal where the dataset was published. When applicable, the dataset is linked to the registered data portals in the colibri website, as described below in this document.
    state = indexes.CharField(model_attr='state')
    language = indexes.CharField(model_attr='language') #PREDEFINED LIST. LIST "LANGUAGES"
    country = indexes.CharField(model_attr='country')#PREDEFINED LIST. LIST "COUNTRIES"
    date_created = indexes.CharField(model_attr='date_created')
    date_created_by_user = indexes.CharField(model_attr='date_created_by_user')

    #---------Geographics & Temporal Context------#
    temporal_granularity = indexes.CharField(
        model_attr='temporal_granularity')   #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - LIST "TEMPORAL_GRANULARITY"
    temporal_coverage_from = indexes.CharField(
        model_attr='temporal_coverage_from') #The start date of temporal coverage of the dataset.
    temporal_coverage_to = indexes.CharField(
        model_attr='temporal_coverage_to') #The end date of temporal coverage of the dataset.
    geographical_granularity = indexes.CharField(
        model_attr='geographical_granularity')  #Type of area covered (e.g. country, region, city, etc.).#AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - LIST "GEOGRAPHICAL_GRANULARITY"
    geographical_coverage = indexes.CharField(
        model_attr='geographical_coverage') #The geographic area covered by the dataset.(IN THE FUTURE - maybe autocompletion from google)

    #---------People / Organizations------#
    maintainer = indexes.CharField(
        model_attr='maintainer') #Cached information about the user or usergroup that manages the dataset.  #Cached name of the user or usergroup that maintains the dataset. LINK TO USERS / USERGROUPS TABLE

    #---------Scientific Context----------#
    scientific_domain = indexes.CharField(model_attr='scientific_domain') #PREDEFINED LIST - List "Scientific Domains"
    data_collection_type = indexes.CharField(
        model_attr='data_collection_type') #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "DataCollectionMethod"
    data_collection_description = indexes.CharField(
        model_attr='data_collection_description') #Description of the data collection method.
    software_package = indexes.CharField(
        model_attr='software_package')  #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "software package"

    #---------Relations----------#
    applications = indexes.CharField(
        model_attr='title')  #List of software applications that use this dataset as a source of information. See below for description of software apps.


    def get_model(self):
        return Dataset

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(date_created__lte=datetime.datetime.now())