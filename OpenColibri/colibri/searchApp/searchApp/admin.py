__author__ = 'mpetyx'

from django.contrib import admin

from models import Kouklaki


class KouklakiAdmin(admin.ModelAdmin):
    pass


admin.site.register(Kouklaki, KouklakiAdmin)