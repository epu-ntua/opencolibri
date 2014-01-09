__author__ = 'mpetyx'

from tastypie.resources import ModelResource, ALL
from organizations.models import *
import models
import colibri


class ResourcesResource(ModelResource):
    class Meta:
        queryset = models.Resource.objects.all()
        resource_name = 'resource'
        list_allowed_methods = ['get', 'post']
        ordering = ALL
        limit = 20
        filtering = {
            "description": ALL,
            # "file": ALL,
            "format": ALL,
            # "language": ALL,
            "dataset": ALL,
        }