import datetime
from haystack import indexes
from models import Dataset


class DatasetIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    sorted_title = indexes.CharField(model_attr='title', indexed=False, stored=True)
    description = indexes.CharField(model_attr='description')
    country = indexes.CharField(model_attr='country', faceted=True)
    categories = indexes.CharField(model_attr='categories', faceted=True)
    publisher = indexes.CharField(model_attr='publisher', faceted=True)
    license = indexes.CharField(model_attr='license', faceted=True)
    views = indexes.IntegerField(model_attr='views', indexed=False, stored=True, default=0)
    modified_date = indexes.DateTimeField(model_attr='modified_date', indexed=False, stored=True)

    def get_model(self):
        return Dataset

    def prepare(self, object):
        self.prepared_data = super(DatasetIndex, self).prepare(object)

        self.prepared_data['format'] = [resource.format for resource in object.resources.all()]

        return self.prepared_data

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


        #http://django-haystack.readthedocs.org/en/latest/searchindex_api.html#realtimesearchindex

        #class NoteIndex(indexes.ModelSearchIndex, indexes.Indexable):
        #    class Meta:
        #        model = Note
        #        fields = ['user', 'pub_date']
        #        excludes = ['user']

        # class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):

        #     text = indexes.CharField(document=True, use_template=True)
        # #    nameAppearance  = indexes.CharField(model_attr='nameAppearance')
        # #    username = indexes.CharField(model_attr='username') #Unique identifier of the user, part of their credentials.
        # #    firstName = indexes.CharField(model_attr='firstName') #The user's first name
        # #    lastName = indexes.CharField(model_attr='lastName') #The user's last name
        # #    nameAppearance = indexes.CharField(model_attr='nameAppearance') #Information on the way the name is displayed in public (for instance, Dimitris Batis or Dimitris G. Batis or Batis Dimitris)
        # #    city = indexes.CharField(model_attr='city') #User's city of residence
        # #    country = indexes.CharField(model_attr='country')#User's country of residence. PREDEFINED LIST - COUNTRIES
        # ##    email = indexes.CharField(model_attr='email') #User's e-mail address.
        # #    scientific_background = indexes.CharField(model_attr='scientific_background') # PREDEFINED LIST. LIST "SCIENTIFIC DOMAINS"
        # #    rpg_class = indexes.CharField(model_attr='rpg_class') # Users Pick a class like in rpgs

        #     # We add this for autocomplete.
        #     nameAppearance = indexes.EdgeNgramField(model_attr='nameAppearance')

        #     def get_model(self):
        #         return UserProfile

        #     def index_queryset(self, using=None):
        #         """Used when the entire index for model is updated."""
        #         return self.get_model().objects.all()


        # class SoftwareApplicationIndex(indexes.SearchIndex, indexes.Indexable):
        #     """
        #     A dataset may contain information for any software applications that use the dataset as a source. The information for each application is stored in the extras:applications field, as a list of objects.
        #     """
        #     text = indexes.CharField(document=True, use_template=True)
        #     title = indexes.CharField(model_attr='title') #The official title of the application or service.
        #     url = indexes.CharField(model_attr='url') #The URL where the application is available, or information about it.
        #     type = indexes.CharField(model_attr='type') #PREDEFIND LIST. LIST "ApplicationType"
        #     maintainer = indexes.CharField(model_attr='maintainer') # POIOS EINAI O MAINTAINER TOU Application - LINK SE PINAKA USERS / USER GROUPS


        #     def get_model(self):
        #         return SoftwareApplication

        #     def index_queryset(self, using=None):
        #         """Used when the entire index for model is updated."""
        #         return self.get_model().objects.all()