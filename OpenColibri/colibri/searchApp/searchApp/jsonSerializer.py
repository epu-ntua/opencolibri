__author__ = 'mpetyx'

from django.core import serializers

serializers.serialize("json", [q.object for q in queryset])