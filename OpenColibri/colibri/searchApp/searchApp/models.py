__author__ = 'mpetyx'

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Kouklaki(models.Model):
    result = models.TextField()
    title = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


    class Admin:
        pass


from athumb.fields import ImageWithThumbsField
from athumb.backends.s3boto import S3BotoStorage_AllPublic
from djangoratings.fields import RatingField

# It is generally good to keep these stored in their own module, to allow
# for other DEPRECATEDmodels.py modules to import the values. This assumes that more
# than one model stores stuff in the same bucket.
PUBLIC_MEDIA_BUCKET = S3BotoStorage_AllPublic(bucket='colibrifp7/photos/')

# The base url for accessing public photos
PUBLIC_PHOTO_BASEURL = 'http://s3-eu-west-1.amazonaws.com/colibrifp7/photos/'


class Photo(models.Model):
    photo_original = ImageWithThumbsField(
        upload_to="photos",
        thumbs=(
            ('small', {'size': (170, 170), 'crop': True}),
            ('medium', {'size': (340, 340), 'crop': True}),
            ('large', {'size': (500, 500), 'crop': True}),
            ('original', {'size': (2048, 2048), 'crop': True}),
        ),
        blank=True, null=True,
        storage=PUBLIC_MEDIA_BUCKET)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%d" % self.id


class Person(models.Model):
    Citizen = 'CZ'
    Researcher = 'RS'
    Journalist = 'JS'
    Civil_Servant = 'CS'
    Politician = 'PL'
    Enterpreneur = 'ER'
    Hacker = 'HA'

    RPG_CLASS = (
        (Citizen, 'Citizen'),
        (Researcher, 'Researcher'),
        (Journalist, 'Journalist'),
        (Civil_Servant, 'Civil Servant'),
        (Politician, 'Politician'),
        (Enterpreneur, 'Enterpreneur'),
        (Hacker, 'Hacker'),
    )
    """
    In order to identify the user or group as owner, a new CKAN user is created for each user and each group. This information is internal to CKAN and not exposed through the API when requesting information on a dataset. To overcome this, we store the authentication key of each user in our relational database.

    Each user has a set of credentials (username and password) stored either in our LDAP server or in an external authentication system that supports the OpenID protocol.
    """

    name = models.CharField(max_length=256, blank=True, null=True)
    username = models.CharField(max_length=256, blank=True,
                                null=True) #Unique identifier of the user, part of their credentials.
    firstName = models.CharField(max_length=256, blank=True, null=True) #The user's first name
    middleName = models.CharField(max_length=256, blank=True, null=True) #The user's middle name
    lastName = models.CharField(max_length=256, blank=True, null=True) #The user's last name
    nameAppearance = models.CharField(max_length=256, blank=True,
                                      null=True) #Information on the way the name is displayed in public (for instance, Dimitris Batis or Dimitris G. Batis or Batis Dimitris)
    city = models.CharField(max_length=256, blank=True, null=True) #User's city of residence
    country = models.CharField(max_length=256, blank=True,
                               null=True)#User's country of residence. PREDEFINED LIST - COUNTRIES
    email = models.EmailField(max_length=256, blank=True, null=True) #User's e-mail address.
    facebookUrl = models.URLField(max_length=256, blank=True, null=True) #User's Facebook profile
    twitterUrl = models.URLField(max_length=256, blank=True, null=True) #User's Twitter profile
    googleUrl = models.URLField(max_length=256, blank=True, null=True) #User's Google+ profile
    linkedInUrl = models.URLField(max_length=256, blank=True, null=True) #User's LinkedIn profile
    websiteUrl = models.URLField(max_length=256, blank=True, null=True) #User's personal website
    avatar = models.ForeignKey(Photo, blank=True, null=True) #AVATAR HERE
    karma = models.IntegerField(blank=True, null=True) #User's "karma" rating.
    scientific_background = models.CharField(max_length=256, blank=True,
                                             null=True) # PREDEFINED LIST. LIST "SCIENTIFIC DOMAINS"
    rpg_class = models.CharField(max_length=256, blank=True, null=True,
                                 choices=RPG_CLASS) # Users Pick a class like in rpgs
    date_created = models.DateTimeField(auto_now_add=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Person.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


class Resources(models.Model):
    file = models.FileField(upload_to="/resources/")
    uri = models.CharField(max_length=256, blank=True,
                           null=True)  #Either a URL to an external resource or a URI in the format urn:file:<uuid> for locally stored files.
    downloadUrl = models.URLField(max_length=256, blank=True,
                                  null=True) #Auto-generated when saving resources in CKAN. Matches CKAN's url field.
    format = models.CharField(max_length=256, blank=True, null=True) #The file extension or MIME type of the resource.
    description = models.TextField(blank=True, null=True)  #Short description of the resource.
    language = models.CharField(max_length=256, blank=True,
                                null=True) #The language used in the file's contents (for instance, English).PREDEFINED LIST - LANGUAGES
    url_dic = models.URLField(max_length=256, blank=True,
                              null=True) #A URL to an external resource where one can find its documentation.
    filename = models.CharField(max_length=256, blank=True, null=True) #Original filename, if an uploaded file.
    visualizationId = models.IntegerField(blank=True,
                                          null=True)  #Either 0, if no visualization exists for the resource, or the ID of the visualization, as stored by the Visualizations Manager.
    #Add if it is a ScraperWiki type- TODO
    date_created = models.DateTimeField(auto_now_add=True)


class Publication(models.Model):
    """
    A dataset may contain information for any publication (scientific paper, news article, etc.) that uses the dataset as a cited source. The information for each publication is stored in the extras:publications field, as a list of objects
    """

    title = models.CharField(max_length=256, blank=True, null=True) #The title of the article.
    url = models.URLField(max_length=256, blank=True,
                          null=True) #The URL where the publication, or information about it, is available.
    type = models.CharField(max_length=256, blank=True,
                            null=True) #Publication type (newspaper article, research paper, book, etc.). PREDEFINED LIST - LIST "PublicationType"
    authors = models.ManyToManyRel(Person) #List of author names.
    uri = models.URLField(max_length=256, blank=True, null=True) #A URI (for instance, DOI or ISBN) for the publication.
    date_created = models.DateTimeField(auto_now_add=True)


class SoftwareApplication(models.Model):
    """
    A dataset may contain information for any software applications that use the dataset as a source. The information for each application is stored in the extras:applications field, as a list of objects.
    """
    title = models.CharField(max_length=256, blank=True, null=True) #The official title of the application or service.
    url = models.URLField(max_length=256, blank=True,
                          null=True) #The URL where the application is available, or information about it.
    type = models.CharField(max_length=256, blank=True, null=True) #PREDEFIND LIST. LIST "ApplicationType"
    maintainer = models.ForeignKey(
        Person) # POIOS EINAI O MAINTAINER TOU Application - LINK SE PINAKA USERS / USER GROUPS
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(blank=True, null=True)


class Comment(models.Model):
    name = models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)


class DataPortal(models.Model):
    """
    Represents open data portals, either national such as www.data.gov.uk or multi-national such as www.publicdata.eu. They serve as sources of the information contained in registered datasets. colibri administrators provide the list of data portals, not users.

    As CKAN's domain model has no entity for data portals, the same solution as above applies, i.e. the user inputs the name of the data portal in an auto-complete textbox. Ff the name matches one of the registered data portals, then we can provide additional information about the portal.

    The data portal is not directly linked to the dataset. Instead, an intermediate Source links between the dataset and the portal which hosts the original data.
    """
    name = models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)


class Source(models.Model):
    """
    Sources link to the open government data that were used to produce the dataset. A source can be:
    A link to another dataset already stored in colibri. In this case, the source contains the UUID of that dataset.
    A URL to the original data, published by a public sector organization. In this case, the source contains the URL and the relevant Organization object described above.
    A URL to a dataset published in another open data portal. In this case, the source contains the URL and the relevant DataPortal object described above.
    """

    name = models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)


class Dataset(models.Model):
    Awaiting_Approval = 'AA'
    Approved = 'AP'
    Rejected = 'RE'

    DATASET_STATE = (
        (Awaiting_Approval, 'Awaiting Approval'),
        (Approved, 'Approved'),
        (Rejected, 'Rejected'),
    )
    """
        The dataset with all the resources attached
        A dataset is a collection of information that originates or derives from public sector information. The information is contained in one or more resources. The dataset may belong to either a single user or a group of users, but as far as CKAN is concerned it belongs just to a CKAN user (which, in reality, can be a group).
    """

    resources = models.ManyToManyRel(Resources) #EINAI DYO FORES!

    #---------Basic Information------#
    title = models.CharField(max_length=256, blank=True, null=True)
    nameCKAN = models.CharField(max_length=256, blank=True,
                                null=True) #A unique slug identifying the dataset. Unfortunately, this is required by CKAN. PRECALCULATED, KEPT ONLY FOR COMPATIBILITY with CKAN.
    description = models.CharField(max_length=800, blank=True, null=True) #Summarizes the contents of the dataset.
    categories = models.CharField(max_length=256, blank=True, null=True)  #PREDEFINED LIST - LIST "CATEGORIES"
    tags = models.CharField(max_length=256, blank=True, null=True) #list of keywords - AUTOCOMPLETION
    url = models.URLField(max_length=256, blank=True,
                          null=True) #Location of the original dataset (for instance, in the publisher's website).
    published_via = models.ForeignKey(
        DataPortal) #Name of the data portal where the dataset was published. When applicable, the dataset is linked to the registered data portals in the colibri website, as described below in this document.
    license = models.CharField(max_length=256, blank=True,
                               null=True) #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list).LIST "LICENSES"
    state = models.CharField(max_length=2, blank=True, null=True, choices=DATASET_STATE)
    language = models.CharField(max_length=256, blank=True, null=True) #PREDEFINED LIST. LIST "LANGUAGES"
    country = models.CharField(max_length=256, blank=True, null=True) #PREDEFINED LIST. LIST "COUNTRIES"
    date_created = models.DateTimeField(auto_now_add=True)
    date_created_by_user = models.DateTimeField(blank=True, null=True)
    rating = RatingField(range=10)

    #---------Extension Related------#
    is_extended = models.BooleanField() #Whether the dataset is Extended in the colibri portal or Original. Default NO
    extension_type = models.CharField(max_length=256, blank=True, null=True) #PREDEFINED LIST - LIST "EXTENSIONS"
    extension_short_description = models.CharField(max_length=256, blank=True,
                                                   null=True) # a short description of what the extension was all about

    #---------Geographics & Temporal Context------#
    temporal_granularity = models.CharField(max_length=256, blank=True,
                                            null=True)   #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - LIST "TEMPORAL_GRANULARITY"
    temporal_coverage_from = models.DateField(blank=True,
                                              null=True) #The start date of temporal coverage of the dataset.
    temporal_coverage_to = models.DateField(blank=True, null=True) #The end date of temporal coverage of the dataset.
    geographical_granularity = models.CharField(max_length=256, blank=True,
                                                null=True)  #Type of area covered (e.g. country, region, city, etc.).#AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - LIST "GEOGRAPHICAL_GRANULARITY"
    geographical_coverage = models.CharField(max_length=256, blank=True,
                                             null=True) #The geographic area covered by the dataset.(IN THE FUTURE - maybe autocompletion from google)

    #---------People / Organizations------#
    author = models.CharField(max_length=256, blank=True, null=True) #Who is the author of the dataset - AUTOCOMPLETION
    publisher = models.CharField(max_length=256, blank=True,
                                 null=True) #Who is the publisher of the dataset - AUTOCOMPLETION
    maintainer = models.ForeignKey(
        Person) #Cached information about the user or usergroup that manages the dataset.  #Cached name of the user or usergroup that maintains the dataset. LINK TO USERS / USERGROUPS TABLE

    #---------Scientific Context----------#
    scientific_domain = models.CharField(max_length=256, blank=True,
                                         null=True) #PREDEFINED LIST - List "Scientific Domains"
    data_collection_type = models.CharField(max_length=256, blank=True,
                                            null=True)  #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "DataCollectionMethod"
    data_collection_description = models.CharField(max_length=500, blank=True,
                                                   null=True) #Description of the data collection method.
    software_package = models.CharField(max_length=256, blank=True,
                                        null=True)  #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "software package"
    analysis_unit = models.CharField(max_length=256, blank=True,
                                     null=True) #The unit of analysis that is the major entity analyzed in the study (for instance, individuals, groups, geographical units, etc.)#AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "Analysis Units"
    statistical_methodology = models.CharField(max_length=256, blank=True,
                                               null=True) #Description of the methodology used, if statistical data.

    #---------Relations----------#
    applications = models.ManyToManyRel(
        SoftwareApplication)   #List of software applications that use this dataset as a source of information. See below for description of software apps.
    publications = models.ManyToManyRel(
        Publication) #List of publications that cite the dataset as a source of information.
    sources = models.ManyToManyRel(Source) #Links to the original material used to produce the dataset.


    class Admin:
        pass


class RevisionDataset(models.Model):
    original = models.ForeignKey(Dataset, related_name="original_dataset", blank=True, null=True, )
    revision = models.ForeignKey(Dataset, related_name="child_dataset", blank=True, null=True, )
    author = models.ForeignKey(Person, blank=True, null=True, )
    date_created = models.DateTimeField(auto_now_add=True)

    class Admin:
        pass