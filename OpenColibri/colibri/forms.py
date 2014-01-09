# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Select

import lists
from fields import OrganizationNameField
from models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from tagging.fields import TagField


class DatasetForm(forms.ModelForm):
    categories = forms.MultipleChoiceField(choices=lists.CATEGORIES)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['maintainingGroup'].queryset = Organization.objects.get_for_user(user=self.request.user)
        self.fields['categories'].choices = lists.CATEGORIES

    class Meta:
        model = Dataset
        exclude = ('nameCKAN',)
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(),
            'country': Select(attrs={'class': 'chzn-select'}),
            'categories': Select(attrs={'multiple': 'multiple'}),
        }


class DatasetSearchForm(forms.Form):
    value = forms.CharField(required=True, widget=forms.TextInput(attrs={'required': 'required'}))


class GroupForm(forms.Form):
    name = OrganizationNameField(required=True, max_length=100, widget=forms.TextInput(attrs={'required': 'required'}))
    members = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'users-input'}))
    admins = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'users-input'}))


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        widgets = {
            'type': Select(attrs={'class': 'chzn-select'}),
            'publicationType': Select(attrs={'class': 'chzn-select'}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        widgets = {
            'language': Select(attrs={'class': 'chzn-select'}),
        }

    def clean(self):
        if 'uri' in self.cleaned_data and 'file' in self.cleaned_data:
            if not self.cleaned_data['uri'] and not self.cleaned_data['file']:
                raise forms.ValidationError("A resource should either have a file or a uri")
        return self.cleaned_data


class DatasetRequestsForm(forms.ModelForm):
    class Meta:
        model = DatasetRequests
        exclude = ('author', 'date_created', 'accepted_comment', 'date_updated')


class DatasetRatingForm(forms.ModelForm):
    class Meta:
        model = DatasetIndividualRating
        exclude = ('Rater', 'dataset')


class DatasetScientificContextForm(forms.ModelForm):
    class Meta:
        model = DatasetScientificContext
        exclude = ('dataset')
        widgets = {
            'scientific_domain': Select(attrs={'class': 'chzn-select'}),
        }


class DatasetGeoTempContextForm(forms.ModelForm):
    class Meta:
        model = DatasetGeoTempContext
        exclude = ('dataset')
        widgets = {
            'temporal_coverage_from': forms.TextInput(attrs={'class': 'popupDatepicker'}),
            'temporal_coverage_to': forms.TextInput(attrs={'class': 'popupDatepicker'})
        }

    def clean(self):
        if 'temporal_coverage_from' in self.cleaned_data and 'temporal_coverage_to' in self.cleaned_data:
            try:
                if self.cleaned_data['temporal_coverage_from'] > self.cleaned_data['temporal_coverage_to']:
                    raise forms.ValidationError("temporal coverage to should be later than temporal coverage from")
            except:
                raise forms.ValidationError(
                    "please enter a valid date format for both temporal coverage dates (mm/dd/yyyy)")
        return self.cleaned_data

#    text_input = forms.CharField()
#
#    textarea = forms.CharField(
#        widget = forms.Textarea(),
#    )
#
#    radio_buttons = forms.ChoiceField(
#        choices = (
#            ('option_one', "Option one is this and that be sure to include why it's great"),
#            ('option_two', "Option two can is something else and selecting it will deselect option one")
#            ),
#        widget = forms.RadioSelect,
#        initial = 'option_two',
#    )
#
#    checkboxes = forms.MultipleChoiceField(
#        choices = (
#            ('option_one', "Option one is this and that be sure to include why it's great"),
#            ('option_two', 'Option two can also be checked and included in form results'),
#            ('option_three', 'Option three can yes, you guessed it also be checked and included in form results')
#            ),
#        initial = 'option_one',
#        widget = forms.CheckboxSelectMultiple,
#        help_text = "<strong>Note:</strong> Labels surround all the options for much larger click areas and a more usable form.",
#    )
#
#    appended_text = forms.CharField(
#        help_text = "Here's more help text"
#    )
#
#    prepended_text = forms.CharField()
#
#    prepended_text_two = forms.CharField()
#
#    file = forms.FileField(
#        label='Select a file',
#        help_text='max. 42 megabytes'
#    )
#
#    multicolon_select = forms.MultipleChoiceField(
#        choices = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')),
#    )
#
#    # Uni-form
#    helper = FormHelper()
#    helper.form_class = 'form-horizontal'
#    helper.layout = Layout(
#        Field('text_input', css_class='input-xlarge'),
#        Field('textarea', rows="3", css_class='input-xlarge'),
#        'radio_buttons',
#        Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
#        AppendedText('appended_text', '.00'),
#        PrependedText('prepended_text', '<input type="checkbox" checked="checked" value="" id="" name="">', active=True),
#        PrependedText('prepended_text_two', '@'),
#        'multicolon_select',
#        FormActions(
#            Submit('save_changes', 'Save changes', css_class="btn-primary"),
#            Submit('cancel', 'Cancel'),
#        )
#    )


from haystack.forms import FacetedSearchForm


class DatasetFacetedSearchForm(FacetedSearchForm):
    def __init__(self, *args, **kwargs):
        super(DatasetFacetedSearchForm, self).__init__(*args, **kwargs)
        if args[0]:
            self.orderBy = args[0].get('order_by', [])

    def search(self):
        sqs = super(DatasetFacetedSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            if self.orderBy == 'date':
                sqs = self.searchqueryset.order_by('modified_date')
            elif self.orderBy == '-date':
                sqs = self.searchqueryset.order_by('-modified_date')
            elif self.orderBy == '-title':
                sqs = self.searchqueryset.order_by('-sorted_title')
            elif self.orderBy == 'title':
                sqs = self.searchqueryset.order_by('sorted_title')
            elif self.orderBy == '-views':
                sqs = self.searchqueryset.order_by('-views')
            elif self.orderBy == 'views':
                sqs = self.searchqueryset.order_by('views')
            else:
                sqs = self.searchqueryset.order_by('-modified_date')
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

        return sqs


class DatasetExtendModalForm(forms.Form):
    revision_type = forms.ChoiceField(choices=lists.EXTENSION,
                                      widget=Select(attrs={'class': 'chzn-select', 'required': 'required'}))
    short_description = forms.CharField(required=True, widget=forms.TextInput(attrs={'required': 'required'}))


class UserProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        exclude = ('user')
        widgets = {
            'country': Select(attrs={'class': 'chzn-select'}),
            'scientific_background': Select(attrs={'class': 'chzn-select'}),
            'rpg_class': Select(attrs={'class': 'chzn-select'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
