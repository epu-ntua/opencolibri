import datetime
from random import random
import os
import urllib
import urllib2

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import signals
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from imagekit.models import ImageSpecField
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.db.models import Avg, Max, Min, Count
from tastypie.models import create_api_key
from django.db.models.signals import post_init
from django.contrib.comments.signals import comment_was_posted
from django.http import HttpResponse

from tagging.forms import TagField
import tagging
from organizations.models import Organization
from library import *
from athumb.fields import ImageWithThumbsField
from athumb.backends.s3boto import S3BotoStorage_AllPublic
from djangoratings.fields import RatingField
from lists import *
from fluent_comments.models import CommentsRelation
from fields import *
from jsonfield import JSONField



# It is generally good to keep these stored in their own module, to allow
# for other DEPRECATEDmodels.py modules to import the values. This assumes that more
# than one model stores stuff in the same bucket.
PUBLIC_MEDIA_BUCKET = S3BotoStorage_AllPublic(bucket=settings.AWS_STORAGE_BUCKET_NAME)

# The base url for accessing public photos
PUBLIC_PHOTO_BASEURL = 'http://s3-eu-west-1.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/photos/'

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

User.groups = property(lambda u: Organization.objects.get_for_user(user=u))


class EngModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(EngModel):
    """
    In order to identify the user or group as owner, a new CKAN user is created for each user and each group. This information is internal to CKAN and not exposed through the API when requesting information on a dataset. To overcome this, we store the authentication key of each user in our relational database.

    Each user has a set of credentials (username and password) stored either in our LDAP server or in an external authentication system that supports the OpenID protocol.
    """
    user = models.OneToOneField(User)
    nameAppearance = models.CharField(max_length=256, blank=True,
                                      null=True) #Information on the way the name is displayed in public (for instance, Dimitris Batis or Dimitris G. Batis or Batis Dimitris)
    country = models.CharField(max_length=3, default='--',
                               choices=COUNTRIES) #combobox PREDEFINED LIST. LIST "COUNTRIES"
    facebookUrl = models.URLField(max_length=256, blank=True, null=True) #User's Facebook profile
    twitterUrl = models.URLField(max_length=256, blank=True, null=True) #User's Twitter profile
    googleUrl = models.URLField(max_length=256, blank=True, null=True) #User's Google+ profile
    linkedInUrl = models.URLField(max_length=256, blank=True, null=True) #User's LinkedIn profile
    websiteUrl = models.URLField(max_length=256, blank=True, null=True) #User's personal website
    karma = models.IntegerField(blank=True, null=True) #User's "karma" rating.
    scientific_background = models.CharField(max_length=10, default='--',
                                             choices=SCIENTIFIC_DOMAINS) # PREDEFINED LIST. LIST "SCIENTIFIC DOMAINS"
    rpg_class = models.CharField(max_length=2, default='--', choices=RPG_CLASS) # Users Pick a class like in rpgs


UserProfile.avatar = property(lambda d: Photo.objects.get_or_create(user_profile=d)[0])


def user_post_delete(sender, instance, **kwargs):
    try:
        UserProfile.objects.get(user=instance).delete()
    except:
        pass


def user_post_save(sender, instance, **kwargs):
    try:
        UserProfile.objects.get_or_create(user=instance)
    except:
        pass


models.signals.post_delete.connect(user_post_delete, sender=User)
models.signals.post_save.connect(user_post_save, sender=User)


def photo_upload_path(instance, filename):
    return os.path.join(
        "photos", "user_%d" % instance.user_profile.user.id, filename)


class Photo(EngModel):
    user_profile = models.ForeignKey(UserProfile)
    photo_original = ImageWithThumbsField(
        upload_to=photo_upload_path,
        thumbs=(
            ('48x48', {'size': (48, 48), 'crop': True}),
            ('68x68', {'size': (68, 68), 'crop': True}),
            ('100x100', {'size': (100, 100), 'crop': True}),
            ('150x150', {'size': (150, 150), 'crop': True}),
        ),
        blank=True, null=True)

    def __unicode__(self):
        return "%d" % self.id


class DataPortal(EngModel):
    """
    Represents open data portals, either national such as www.data.gov.uk or multi-national such as www.publicdata.eu. They serve as sources of the information contained in registered datasets. colibri administrators provide the list of data portals, not users.

    As CKAN's domain model has no entity for data portals, the same solution as above applies, i.e. the user inputs the name of the data portal in an auto-complete textbox. Ff the name matches one of the registered data portals, then we can provide additional information about the portal.

    The data portal is not directly linked to the dataset. Instead, an intermediate Source links between the dataset and the portal which hosts the original data.
    """
    name = models.CharField(max_length=256)


class Dataset(EngModel):
    """
    The dataset with all the resources attached
    A dataset is a collection of information that originates or derives from public sector information. The information is contained in one or more resources. The dataset may belong to either a single user or a group of users, but as far as CKAN is concerned it belongs just to a CKAN user (which, in reality, can be a group).
    """
    title = models.CharField(max_length=256, unique=True, null=True) #required
    description = models.TextField() #required, Summarizes the contents of the dataset.
    categories = MultiSelectField(max_length=256, blank=True,
                                  choices=CATEGORIES)  #checkbox-list, PREDEFINED LIST - LIST "CATEGORIES"
    url = models.URLField(max_length=256, blank=True,
                          null=True) #Location of the original dataset (for instance, in the publisher's website).
    license = models.CharField(max_length=256, blank=True,
                               null=True) #AUTOCOMPLETION WITH PREDEFINED LIST. LIST "LICENSES" autocomletion textbox
    country = models.CharField(max_length=3, default='--',
                               choices=COUNTRIES) #combobox PREDEFINED LIST. LIST "COUNTRIES"
    state = models.CharField(max_length=2, default='AA', choices=DATASET_STATE)
    published_via = models.ForeignKey(DataPortal, blank=True, null=True)
    rating = RatingField(range=5, blank=True, null=True)
    author = models.CharField(max_length=256, default='', blank=True,
                              null=True) #Who is the author of the dataset - AUTOCOMPLETION
    publisher = models.CharField(max_length=256, default='', blank=True,
                                 null=True) #Who is the publisher of the dataset - AUTOCOMPLETION
    maintainingGroup = models.ForeignKey(Organization, blank=True,
                                         null=True) #Cached information about the user or usergroup that manages the dataset.  #Cached name of the user or usergroup that maintains the dataset. LINK TO USERS / USERGROUPS TABLE
    uploader = models.ForeignKey(
        User) #Cached information about the user or usergroup that manages the dataset.  #Cached name of the user or usergroup that maintains the dataset. LINK TO USERS / USERGROUPS TABLE
    views = models.IntegerField(blank=True, null=True, default=0)
    comments_set = CommentsRelation()
    date_published = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    def increase(self):
        self.views += 1
        self.save()

    # TODO: write test and refactor
    def get_absolute_url(self):
        return u'/dataset/%d' % self.id

    def display_date_published(self):
        return '' if not self.date_published else self.date_published

    def display_country_comma_date_published(self):
        country = self.display_country()
        date_published = self.display_date_published()
        return country + ', ' + str(
            date_published) if date_published and country else country if country else date_published

    def display_country(self):
        return '' if self.country == '--' else self.get_country_display()

    def category_display(self):
        return self.get_categories_display()

    def is_revision(self):
        try:
            RevisionDataset.objects.get(revision=self)
            return True
        except RevisionDataset.DoesNotExist:
            return False

    def get_parent(self):
        revision = RevisionDataset.objects.get(revision=self)
        return revision.original

    def get_revision(self):
        revision = RevisionDataset.objects.get(revision=self)
        return revision

    def is_editable_by_user(self, user):
        return self.uploader == user or self.maintainingGroup in user.groups

    def get_original(self):
        dataset = self
        while dataset.is_revision():
            dataset = dataset.get_parent()
        return dataset

    def get_all_children(self, short_description=False, revision_type=False):
        datasetTree = {}
        if short_description:
            datasetTree['shortDescription'] = short_description
        if revision_type:
            datasetTree['revision_type'] = revision_type
        datasetTree['name'] = self.title
        datasetTree['uploader'] = self.uploader.username
        datasetTree['id'] = self.id
        datasetTree['url'] = self.get_absolute_url()
        datasetTree['dateExtended'] = self.created_date.strftime("%B %d, %Y")
        revisions = RevisionDataset.objects.filter(original=self)
        if len(revisions) > 0:
            datasetTree['children'] = []
            for c in revisions:
                datasetTree['children'].append(
                    c.revision.get_all_children(short_description=c.short_description, revision_type=c.revision_type))
        return datasetTree

    def totalRatingScore(self):
        return float(self.rating.score) / self.rating.votes


class DatasetGeoTempContext(EngModel):
    dataset = models.OneToOneField(Dataset, primary_key=True)
    temporal_granularity = models.CharField(max_length=256, null=True,
                                            blank=True)   #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - LIST "TEMPORAL_GRANULARITY"
    temporal_coverage_from = models.DateField(blank=True,
                                              null=True) #The start date of temporal coverage of the dataset.
    temporal_coverage_to = models.DateField(null=True, blank=True) #The end date of temporal coverage of the dataset.
    geographical_granularity = models.CharField(max_length=256, default='',
                                                blank=True)  #Type of area covered (e.g. country, region, city, etc.).#AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - LIST "GEOGRAPHICAL_GRANULARITY"
    geographical_coverage = models.CharField(max_length=256, default='',
                                             blank=True) #The geographic area covered by the dataset.(IN THE FUTURE - maybe autocompletion from google)


class DatasetScientificContext(EngModel):
    dataset = models.OneToOneField(Dataset, primary_key=True)
    scientific_domain = models.CharField(max_length=30, default='--',
                                         choices=SCIENTIFIC_DOMAINS) #PREDEFINED LIST - List "Scientific Domains"
    data_collection_type = models.CharField(max_length=256, default='',
                                            blank=True)  #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "DataCollectionMethod"
    data_collection_description = models.TextField(blank=True) #Description of the data collection method.
    software_package = models.CharField(max_length=256, default='',
                                        blank=True)  #AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "software package"
    analysis_unit = models.CharField(max_length=256, default='',
                                     blank=True) #The unit of analysis that is the major entity analyzed in the study (for instance, individuals, groups, geographical units, etc.)#AUTOCOMPLETION WITH PREDEFINED LIST (users can put values not included in list) - List "Analysis Units"
    statistical_methodology = models.TextField(default='',
                                               blank=True) #Description of the methodology used, if statistical data.

    class Admin:
        pass


Dataset.geoTempContext = property(lambda d: DatasetGeoTempContext.objects.get_or_create(dataset=d)[0])
Dataset.scientificContext = property(lambda d: DatasetScientificContext.objects.get_or_create(dataset=d)[0])


def resources_upload_path(instance, filename):
    return os.path.join(
        "resources", "dataset_%d" % instance.dataset.id, filename)


class Resource(EngModel):
    description = models.TextField(blank=True, null=True) #required, Summarizes the contents of the dataset.
    file = models.FileField(upload_to=resources_upload_path, blank=True, null=True)
    uri = models.URLField(max_length=2000, blank=True,
                          null=True)  #Either a URL to an external resource or a URI in the format urn:file:<uuid> for locally stored files.
    format = models.CharField(max_length=256, default='', blank=True,
                              null=True) #The file extension or MIME type of the resource.
    language = models.CharField(max_length=100, default='--',
                                choices=LANGUAGES) #combobox PREDEFINED LIST. LIST "LANGUAGES"
    jsonfile = models.TextField(blank=True, null=True)
    dataset = models.ForeignKey(Dataset)
    downloads = models.IntegerField(blank=True, null=True, default=0)


    # TODO: remove
    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(Resource, self).save(*args, **kwargs)
        #If the file is RDF save it also to the Virtuoso Server
        if (self.file.name): #It is a file, not a url
            fileName, fileType = os.path.splitext(self.file.name)
            if (fileType.lower() == '.rdf'):
                rdffileurl = 'https://' + settings.AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/' + self.file.name
                #Storing into Virtuoso
                try:
                    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    top_level_url = settings.VIRTUOSO_SERVER
                    password_mgr.add_password(None, top_level_url, settings.VIRTUOSO_USER, settings.VIRTUOSO_KEY)
                    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                    opener = urllib2.build_opener(urllib2.HTTPHandler, handler)
                    request = urllib2.Request(settings.VIRTUOSO_DAV + os.path.basename(self.file.name),
                                              'LOAD <' + rdffileurl + '> INTO <' + settings.GRAPH_IRI + '>',
                                              {'Content-Type': 'application/sparql-query'})
                    f = urllib2.urlopen(request)
                    content = f.read()
                    f.close()
                except:
                    print 'Error storing into virtuoso'

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(Resource, self).delete(*args, **kwargs)

    def name(self, *args, **kwargs):
        return array_explode('/', str(self.file)).pop()

    def fileExtension(self):
        if (self.file.name):
            fileName, fileType = os.path.splitext(self.file.name)
            return fileType
        else:
            import urlparse

            path = urlparse.urlparse(self.uri).path
            fileType = os.path.splitext(path)[1]
            return fileType


Dataset.resources = property(lambda d: Resource.objects.filter(dataset=d))
Dataset.applications = property(lambda d: Application.objects.filter(dataset=d))


class RevisionDataset(EngModel):
    original = models.ForeignKey(Dataset, related_name="original_dataset", blank=True, null=True, )
    revision = models.ForeignKey(Dataset, related_name="child_dataset", blank=True, null=True, )
    revision_type = models.CharField(max_length=256, default='--',
                                     choices=EXTENSION) #PREDEFINED LIST - LIST "EXTENSIONS"
    short_description = models.TextField(default='',
                                         blank=True) # a short description of what the extension was all about

    class Admin:
        pass


class DatasetRequests(models.Model):
    name = models.CharField(max_length=256)
    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(User, blank=True, null=True, ) #author that created the dataset request
    category = models.CharField(max_length=2, default='', choices=DATASET_REQUESTS_TYPES)
    description = models.TextField(blank=False, null=False) #Summarizes the contents of the dataset.

    # Optional reverse relation, allow ORM querying:
    comments_set = CommentsRelation()

    #Accepted comment
    accepted_comment = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        verbose_name = "DatasetRequest"
        verbose_name_plural = "DatasetRequests"

    def __unicode__(self):
        return self.name

    class Admin:
        pass


class Application(EngModel):
    """
    A dataset may contain information for any software applications that use the dataset as a source. The information for each application is stored in the extras:applications field, as a list of objects.
    """
    title = models.CharField(max_length=256, default='') #The official title of the application or service.
    url = models.URLField(max_length=256,
                          default='') #The URL where the application is available, or information about it.
    dataset = models.ForeignKey(Dataset)
    type = models.CharField(max_length=256, default='',
                            choices=APPLICATION_TYPES) #PREDEFIND LIST. LIST "ApplicationType"
    maintainingGroup = models.ForeignKey(Organization, blank=True,
                                         null=True) # POIOS EINAI O MAINTAINER TOU Application - LINK SE PINAKA USERS / USER GROUPS
    publicationType = models.CharField(max_length=256, default='',
                                       choices=PUBLICATION_TYPES) #PREDEFIND LIST. LIST "ApplicationType"
    publicationAuthors = models.CharField(max_length=256, default='', blank=True, null=True)
    uploader = models.ForeignKey(User, blank=True, null=True)


class DatasetIndividualRating(models.Model):
    dataset = models.ForeignKey(Dataset)
    Rater = models.ForeignKey(User, blank=True, null=True)
    RatingReason = models.TextField(default='', blank=True)
    Accurancy = models.FloatField(blank=True, null=True, default=5)
    Completeness = models.FloatField(blank=True, null=True, default=5)
    Consistency = models.FloatField(blank=True, null=True, default=5)
    Timelineness = models.FloatField(blank=True, null=True, default=5)


class Comment(EngModel):
    name = models.CharField(max_length=256)


def event_comment_posts_action_update_datasetrequest(sender, **kwargs):
    drequest = kwargs.get('comment').content_object
    if isinstance(drequest, DatasetRequests):
        drequest.date_updated = kwargs.get('comment').submit_date
        drequest.save()


comment_was_posted.connect(event_comment_posts_action_update_datasetrequest)


class Visualization(models.Model):
    user = models.ForeignKey(User)
    # body = models.TextField()
    body = JSONField()
    # mainbody  = JSONField()
    title = models.TextField(default='', blank=True, null=True)
    comment = models.TextField(default='', blank=True, null=True)
    resource = models.ForeignKey(Resource)
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'title', 'resource'), )


Resource.visualization = property(lambda d: Visualization.objects.filter(resource=d))


#def create_dataset_relational_models(sender, **kwargs):
#    if (kwargs.get('created')):
#        dataset=kwargs.get('instance')
#        dataset.geoTempContext
#        dataset.scientificContext
#
#post_save.connect(create_dataset_relational_models, sender=Dataset)
#tagging.register(Dataset)

models.signals.post_save.connect(create_api_key, sender=User)
