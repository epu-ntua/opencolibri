__author__ = 'mpetyx'

from django.http import HttpResponse
from django.template import loader, Context
from django.contrib.flatpages.models import FlatPage

from models import Kouklaki


def search(request):
#    query = request.GET['q']
    query = "what do you like?"
    results = Kouklaki.objects.all()
    template = loader.get_template("search_result.html")
    context = Context({'query': query, 'results': results})
    response = template.render(context)
    return HttpResponse(response)


def search_dataset(request):

#    query = request.GET['text']
#    results = FlatPage.objects.filter(content__icontains=query)
    query = "what do you like?"
    results = Kouklaki.objects.all()
    template = loader.get_template('dataset-search.html')
    context = Context({'query': query, 'results': results})
    response = template.render(context)
    return HttpResponse(response)


def search3(request):
    query = request.GET['q']
    results = FlatPage.objects.filter(content__icontains=query)
    template = loader.get_template()
    context = Context({'query': query, 'results': results})
    response = template.render(context)
    return HttpResponse(response)