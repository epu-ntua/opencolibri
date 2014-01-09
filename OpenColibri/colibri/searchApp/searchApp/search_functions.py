__author__ = 'mpetyx'

#reference https://bitbucket.org/hellmoon666/django-searchApp

import operator

from django.db.models import Q
from django.utils.text import smart_split, unescape_string_literal


def raw_search(query, fields, raw_search):
    """ Performs a searchApp based on the raw searchApp string. Returns a new
            query filtered with the searchApp. """
    return search(query, fields, extract_terms(raw_search))


def search(query, fields, terms):
    """ Performs a searchApp based on a list of searchApp terms. Returns a new
            query filtered with the searchApp. """

    if len(terms) > 0:

        search_list = []

        for term in terms:
            field_list = []
            for field in fields:
                field_list.append(Q(**{field + '__icontains': term}))
            search_list.append(reduce(operator.or_, field_list))

        return query.filter(reduce(operator.and_, search_list))

    else:
        return query


def extract_terms(raw):
    """ Extraction based on spaces, understands double and single quotes. Returns a list of strings """

    terms = list(smart_split(raw))

    print terms
    for i, term in enumerate(terms):
        try:
            terms[i] = unescape_string_literal(terms)
        except ValueError:
            pass
    return terms