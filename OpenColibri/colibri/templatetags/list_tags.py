import ast

from django import template
from django.template.defaultfilters import stringfilter

from colibri.lists import *


register = template.Library()


@register.filter
def country(country_code):
    return dict(COUNTRIES)[country_code]


@register.filter
def removeFromUrl(url, parameterToRemove):
    try:
        index = url.index(parameterToRemove)
        substring = url[index:]
    except:
        return url
    if 'order_by' in parameterToRemove or 'page' in parameterToRemove:
        suffix = '&'
    else:
        suffix = '&selected_facets='
    try:
        toRemove = suffix + substring[:substring.index('&')]
    except:
        toRemove = suffix + substring[:]
    final = url.replace(toRemove, '')
    return final


@register.filter
def length(listArg):
    return len(listArg)


@register.filter
def categories(unicode_category_codes):
    category_codes = [item.encode('ascii') for item in ast.literal_eval(unicode_category_codes)]
    categories = ''
    for category_code in category_codes:
        if category_code is not '':
            categories += dict(CATEGORIES)[category_code] + ', '
    return categories[:-2]


@register.filter
def humanize_country(countrystring):
    x = countrystring
    if (x == "Please choose a country.."): x = x.replace("Please choose a country..", "No country specified")
    return x


@register.filter
def image_publishers(x):
    if x == 'data.gov.uk':
        p_img = 'data.gov.uk.png'
    elif x == 'colibri':
        p_img = 'colibri.portal.png'
    elif x == 'Eurostat':
        p_img = 'eurostat.png'
    elif x == 'data.gouv.fr':
        p_img = 'datagouvfr.png'
    elif x == 'govdata.de':
        p_img = 'govdata.de.png'
    elif x == 'data.gob.es':
        p_img = 'data.gov.es.png'
    elif x == 'Data Archiving and Networked Services':
        p_img = 'dans.png'
    else:
        p_img = ''
    return p_img


@register.filter
def link_publishers(x):
    if x == 'data.gov.uk':
        p_link = 'http://data.gov.uk/'
    elif x == 'colibri':
        p_link = 'http://www.colibridata.eu'
    elif x == 'Eurostat':
        p_link = 'http://epp.eurostat.ec.europa.eu/'
    elif x == 'data.gouv.fr':
        p_link = 'http://www.data.gouv.fr/'
    elif x == 'govdata.de':
        p_link = 'https://www.govdata.de/'
    elif x == 'data.gob.es':
        p_link = 'http://datos.gob.es'
    elif x == 'Data Archiving and Networked Services':
        p_link = 'http://www.dans.knaw.nl/'
    else:
        p_link = ''
    return p_link