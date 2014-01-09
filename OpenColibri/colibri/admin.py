'''
Created on Feb 4, 2013

@author: mpetyx
'''

from django.contrib import admin
from models import *


class PhotoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Photo, PhotoAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserProfile, UserProfileAdmin)


class ResourceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Resource, ResourceAdmin)


class RevisionDatasetAdmin(admin.ModelAdmin):
    pass


admin.site.register(RevisionDataset, RevisionDatasetAdmin)


class ApplicationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Application, ApplicationAdmin)


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Comment, CommentAdmin)


class DatasetGeoTempContextAdmin(admin.ModelAdmin):
    pass


admin.site.register(DatasetGeoTempContext, DatasetGeoTempContextAdmin)


class DatasetScientificContextAdmin(admin.ModelAdmin):
    pass


admin.site.register(DatasetScientificContext, DatasetScientificContextAdmin)


class DataPortalAdmin(admin.ModelAdmin):
    pass


admin.site.register(DataPortal, DataPortalAdmin)


class DatasetAdmin(admin.ModelAdmin):
    pass


admin.site.register(Dataset, DatasetAdmin)


class DatasetIndividualRatingAdmin(admin.ModelAdmin):
    pass


admin.site.register(DatasetIndividualRating, DatasetAdmin)


class DatasetRequestsAdmin(admin.ModelAdmin):
    pass


admin.site.register(DatasetRequests, DatasetRequestsAdmin)


class VisualizationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Visualization, VisualizationAdmin)