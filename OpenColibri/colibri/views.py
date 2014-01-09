import datetime
import urllib

from django.contrib.auth.models import User
from django.shortcuts import render_to_response, render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.core.mail import send_mail
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, StdDev
from django.forms.models import inlineformset_factory, formset_factory
from django.template import loader, Context
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from tastypie.models import ApiKey

from haystack.views import FacetedSearchView
from library import *
from organizations.models import *
from forms import *
from models import Resource, Visualization
from colibri.models import DatasetRequests, Dataset, DatasetIndividualRating
from voting.models import Vote
from jsonHandler import JsonCreator


class DatasetFacetedSearchView(FacetedSearchView):
    pass


class UserListView(ListView):
    model = User
    template_name = 'user/_index.html'
    context_object_name = 'users'
    paginate_by = 25


class DatasetRequestDetailView(DetailView):
    model = DatasetRequests
    template_name = 'request-details.html'
    context_object_name = 'datasetrequest'


class DatasetRequestListView(ListView):
    model = DatasetRequests
    template_name = 'request.html'
    context_object_name = 'datasetrequestlist'
    paginate_by = 10

    def get_queryset(self):
        sort_type = self.request.GET.get('sort', '-date_updated')
        if sort_type == '-date_updated':
            return DatasetRequests.objects.order_by(sort_type)
        else:
            strSQL = 'SELECT colibri_datasetrequests.* FROM colibri_datasetrequests LEFT OUTER JOIN (SELECT object_id,COUNT(\'vote\') AS sumvotes FROM VOTES GROUP BY object_id) AS aggregatedtable ON colibri_datasetrequests.id = object_id ORDER BY sumvotes DESC, date_updated DESC'
            k = DatasetRequests.objects.raw(strSQL)
            #Vote.objects.values('object_id').annotate(dSum=Sum('vote')).order_by('vote')
            #DatasetRequests.objects.raw('SELECT colibri_datasetrequests.*,sumvotes FROM colibri_datasetrequests LEFT OUTER JOIN (SELECT object_id, COUNT('vote') AS sumvotes FROM VOTES GROUP BY object_id) ON colibri_datasetrequests.id = object_id ORDER BY sumvotes DESC;')
            #(Pdb) DatasetRequests.objects.raw('SELECT colibri_datasetrequests.id FROM colibri_datasetrequests LEFT OUTER JOIN (SELECT object.id, SUM('vote') FROM Votes GROUPBY #object.id) ON colibri_datasetrequests.id = object_id')
            #sqlite> SELECT object_id, COUNT('vote') FROM VOTES GROUP BY object_id ORDER BY COUNT('vote') DESC;
            return list(k)

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(DatasetRequestListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['current'] = 'datasetrequests_index'
        context['sort_by'] = self.request.GET.get('sort', 'date')
        return context


class DatasetDetailView(DetailView):
    model = Dataset
    template_name = 'dataset/_details.html'
    context_object_name = 'dataset'
    resources = Resource.objects.prefetch_related('dataset')

    def get_context_data(self, **kwargs):
        context = super(DatasetDetailView, self).get_context_data(**kwargs)
        context['current'] = 'dataset'
        context['AMAZON_BUCKET'] = settings.AWS_STORAGE_BUCKET_NAME
        if self.request.user.is_authenticated():
            context['dataset_is_editable_by_user'] = self.object.is_editable_by_user(self.request.user)
            context['applicationForm'] = ApplicationForm()
        return context

    def post(self, *args, **kwargs):
        dataset = Dataset.objects.get(pk=kwargs.get('pk'))
        data = self.request.POST
        applicationForm = ApplicationForm(data)
        if applicationForm.is_valid():
            application = applicationForm.save()
            dataset.increase()
            return redirect(dataset.get_absolute_url())
        return render(self.request, 'dataset/_details.html', {
            'current': 'dataset',
            'object': dataset,
            'dataset': dataset,
            'applicationForm': applicationForm
        })


class DatasetUpdateView(UpdateView):
    form_class = DatasetForm
    model = Dataset
    template_name = 'dataset/_edit.html'
    context_object_name = 'dataset'
    resources = Resource.objects.prefetch_related('dataset')

    def dispatch(self, *args, **kwargs):
        if not (Dataset.objects.get(pk=kwargs.get('pk')).is_editable_by_user(User.objects.get(username=args[0].user))):
            res = HttpResponse("Unauthorized")
            res.status_code = 401
            return res
        return super(DatasetUpdateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DatasetUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        DatasetResourceFormset = inlineformset_factory(Dataset, Resource, form=ResourceForm, extra=0, can_delete=True)
        context = super(DatasetUpdateView, self).get_context_data(**kwargs)
        context['current'] = 'dataset'

        dataset = self.object
        context['geoTempForm'] = DatasetGeoTempContextForm(instance=dataset.geoTempContext)
        context['scientificForm'] = DatasetScientificContextForm(instance=dataset.scientificContext)
        context['resourceFormset'] = DatasetResourceFormset(prefix='resource', instance=dataset)
        return context

    def post(self, *args, **kwargs):
        DatasetResourceFormset = inlineformset_factory(Dataset, Resource, extra=0, can_delete=True, form=ResourceForm)
        data = self.request.POST
        oldDataset = Dataset.objects.get(pk=kwargs.get('pk'))
        data['state'] = oldDataset.state
        data['uploader'] = oldDataset.uploader.id
        datasetForm = DatasetForm(data, request=self.request, instance=oldDataset)
        if datasetForm.is_valid():
            dataset = datasetForm.save(commit=False)
            gf = DatasetGeoTempContextForm(self.request.POST, instance=dataset.geoTempContext)
            sf = DatasetScientificContextForm(self.request.POST, instance=dataset.scientificContext)
            resourceForm = DatasetResourceFormset(data, self.request.FILES, prefix='resource', instance=dataset)
            # if resourceForm.is_valid():
            if sf.is_valid() and gf.is_valid() and resourceForm.is_valid():
                dataset.save()
                gf = gf.save(commit=False)
                gf.dataset = dataset
                gf.save()
                sf = sf.save(commit=False)
                sf.dataset = dataset
                sf.save()
                resources = resourceForm.save()
                return redirect(dataset.get_absolute_url())
        dataset = Dataset.objects.get(id=kwargs.get('pk'))
        gf = DatasetGeoTempContextForm(instance=dataset.geoTempContext)
        sf = DatasetScientificContextForm(instance=dataset.scientificContext)
        resourceForm = DatasetResourceFormset(prefix='resource', instance=dataset)
        return render(self.request, 'dataset/_edit.html', {
            'current': 'dataset',
            'form': datasetForm,
            'geoTempForm': gf,
            'scientificForm': sf,
            'dataset': dataset,
            'resourceFormset': resourceForm
        })


class DatasetDeleteView(DeleteView):
    model = Dataset
    template_name = 'dataset/_confirm_delete.html'
    context_object_name = 'dataset'
    success_url = '/dataset-search/?q='

    def dispatch(self, *args, **kwargs):
        if not (Dataset.objects.get(pk=kwargs.get('pk')).is_editable_by_user(User.objects.get(username=args[0].user))):
            res = HttpResponse("Unauthorized")
            res.status_code = 401
            return res
        return super(DatasetDeleteView, self).dispatch(*args, **kwargs)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class DatasetListView(ListView):
    model = Dataset
    template_name = 'dataset/_search.html'
    paginate_by = 30
    context_object_name = 'datasets'
    datasetSearchForm = None

    def get_context_data(self, **kwargs):
        context = super(DatasetListView, self).get_context_data(**kwargs)
        value = self.request.GET.get('value', '')
        urlParams = "&value=" + value if not value == '' else ''
        datasetSearchForm = DatasetSearchForm(self.request.GET) if value else DatasetSearchForm()
        context['datasetSearchForm'] = datasetSearchForm
        context['urlParams'] = urlParams
        context['current'] = 'dataset'
        context['query'] = value
        # context['datasets'] = Dataset.objects.filter((query, value)) if query and datasetSearchForm.is_valid else Dataset.objects.all()
        return context

    def get_queryset(self):
        value = self.request.GET.get('value', '')
        datasetSearchForm = DatasetSearchForm(self.request.GET) if value else DatasetSearchForm()
        value = self.request.GET.get('value', None)
        return Dataset.objects.filter(Q(title__icontains=value) | Q(
            author__icontains=value)) if value and datasetSearchForm.is_valid else Dataset.objects.all()


def index(request):
    try:
        latestRequestsModel = DatasetRequests.objects.order_by('-date_updated').all()[:3]
        latestDatasetsModel = Dataset.objects.order_by('-modified_date').all()[:3]
    except DatasetRequests.DoesNotExist:
        latestRequestsModel = None
        latestDatasetsModel = None
    try:
        numDatasets = Dataset.objects.count()
    except Dataset.DoesNotExist:
        numDatasets = None
    try:
        numResources = Resource.objects.count()
    except Resource.DoesNotExist:
        numResources = None
    try:
        numApplications = Application.objects.count()
    except Application.DoesNotExist:
        numApplications = None
    try:
        numUsers = User.objects.count()
    except User.DoesNotExist:
        numUsers = None
    params = {'current': 'home', 'numUsers': numUsers, 'numApplications': numApplications, 'numResources': numResources,
              'numDatasets': numDatasets, 'latestRequests': latestRequestsModel, 'latestDatasets': latestDatasetsModel}
    return render(request, 'index.html', params)


@login_required(login_url='/accounts/login/')
def request_acceptanswer(request, request_id, comment_id):
    params = {'current': 'datasetrequests_index'}
    drequests = DatasetRequests.objects.get(pk=request_id)
    drequests.accepted_comment = comment_id
    drequests.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/accounts/login/')
def request_vote(request, request_id, direction):
    params = {'current': 'datasetrequests_index'}
    drequests = DatasetRequests.objects.get(pk=request_id)
    if direction == 'up':
        Vote.objects.record_vote(drequests, request.user, +1)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/accounts/login/')
def request_new(request):
    if request.method == 'GET':
        params = {'current': 'datasetrequests_index'}
        return render(request, 'requests-add.html', {'form': DatasetRequestsForm()})
    if request.method == 'POST':
        form = DatasetRequestsForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.author = request.user
            a.date_created = datetime.datetime.now()
            a.date_updated = a.date_created
            a.save()
            params = {'current': 'datasetrequests_index'}
            return HttpResponseRedirect(reverse('datasetrequests_details', args=(a.id,)))


def csvviewer(request, pk):
    import unicodecsv

    resource = get_object_or_404(Resource, pk=pk)
    if str(resource.file) == '':
        url = resource.uri
    else:
        url = "https://" + settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/" + str(resource.file)

    file = urllib.urlopen(url)
    filesniff = urllib.urlopen(url)
    try:
        dialect = unicodecsv.Sniffer().sniff(filesniff.read(1024))
        csv_data = unicodecsv.reader(file, dialect, encoding='utf-8')
    except Exception:
        csv_data = unicodecsv.reader(file, delimiter=',', encoding='utf-8')

    data = []
    index = 1
    try:
        for row in csv_data:
            if (index == 1): headercolumns = row
            data.append(row)
            index = index + 1
    except Exception:
        params = {
            'dataset_pk': resource.dataset.id, 'current': 'dataset',
        }
        return render(request, 'visualization/csverror.html', params)
    try:
        params = {
            'Resource': Resource, 'data': data, 'headercolumns': headercolumns, 'current': 'dataset',
            'dataset_pk': resource.dataset.id, 'resource_language': resource.language,
        }
        return render(request, 'visualization/csvviewer.html', params)
    except Exception:
        params = {
            'dataset_pk': resource.dataset.id, 'current': 'dataset',
        }
    return render(request, 'visualization/csverror.html', params)


def analyze(request):
    if request.method == 'POST':
        #Retrieve the required post parameters
        retrievedData = request.POST.getlist("datasnap[]")
        cleanedData = []
        numberOfClusters = int(request.POST.get("numberOfClusters"))
        labelColumn = int(request.POST.get("labelColumn"))
        attributeAColumn = int(request.POST.get("attributeAColumn"))
        attributeBColumn = int(request.POST.get("attributeBColumn"))


        #Prepare the input dataset for the K-Means clustering algorithm
        Kmeansinput = []

        for index, item in enumerate(retrievedData):
            row = item.split(',')
            cleanedData.append(row)
            x = safe_convert_float(row[attributeAColumn - 1])
            y = safe_convert_float(row[attributeBColumn - 1])
            Kmeansinput.append((x, y))

        #Run the K-Means Clustering Algorithm

        from cluster import KMeansClustering

        cl = KMeansClustering(Kmeansinput)
        number_only_clusters = cl.getclusters(numberOfClusters)

        #Reconstruct the clusters with the proper data labels
        clusters = []
        for clustersindex, clusteritem in enumerate(number_only_clusters):
            curclusterset = []
            for item, data in enumerate(clusteritem):
                for dataindex, dataitem in enumerate(cleanedData):
                    if ((safe_convert_float(cleanedData[dataindex][attributeAColumn - 1]) == data[0]) and (
                        safe_convert_float(cleanedData[dataindex][attributeBColumn - 1]) == data[1])):
                        curclusterset.append((cleanedData[dataindex][labelColumn - 1], data[0], data[1]))
            clusters.append(curclusterset)

            #Return results
        params = {'current': 'dataset', 'clusters': clusters}
    return render(request, 'visualization/analyze.html', params)


def profile(request, pk):
    userModel = User.objects.get(pk=pk)
    if (userModel == request.user):
        curKey = ApiKey.objects.get_or_create(user=userModel)[0]
    else:
        curKey = None
    try:
        latestDatasetsModel = Dataset.objects.order_by('-modified_date').filter(uploader=pk)[:5]
    except Dataset.DoesNotExist:
        latestDatasetsModel = None
    try:
        latestRequestsModel = DatasetRequests.objects.order_by('-date_updated').filter(author=pk)[:5]
    except DatasetRequests.DoesNotExist:
        latestRequestsModel = None
    current = 'profile' if userModel == request.user else 'community'
    params = {'current': current, 'active_tab': 'groups', 'userModel': userModel, 'latestDatasets': latestDatasetsModel,
              'latestRequests': latestRequestsModel, 'key': curKey}
    return render(request, 'profile.html', params)


def ontowiki(request):
    params = {'current': 'dataset'}
    return render(request, 'linkedata/ontowiki.html', params)


def sparql(request):
    params = {'current': 'dataset'}
    return render(request, 'linkedata/sparql.html', params)


def terms(request):
    params = {'current': 'about'}
    return render(request, 'terms.html', params)


def about(request):
    params = {'current': 'about'}
    return render(request, 'about.html', params)


def contact(request):
    params = {'current': 'about'}
    return render(request, 'contact.html', params)


def visual(request):
    params = {'current': 'about'}
    return render(request, 'visualization/visual.html', params)


def visualjson(request):
    #Load the JSON object
    if request.method == 'GET':
        params = {'current': 'about'}
        json_data = open('colibri/static/visualizations/france-elections.json')
        response = HttpResponse(json_data, mimetype='application/json')
        response['Content-Disposition'] = "filename=%s" % 'france-elections.json'
        return response
        #Save the JSON object
    if request.method == 'POST':
        if 'filename' in request.POST.keys():
            #Export datagrid to CSV
            csv_data = request.POST['data']
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + request.POST['filename'] + '"'
            return response
        else:
            # Save Visualization State
            json_data = request.raw_post_data
            #SAVE json_data to Amazon S3
            #.........
            json_file = open('colibri/static/visualizations/france-elections2.json', 'w')
            json_file.write(json_data)
            json_file.close()
            response = HttpResponse(json_data, mimetype='application/json')
            return response


#def portal_add(request):
#    params = {'portal_form': DataPortalForm()}
#    if request.method == 'GET':
#        return render(request, 'dataset/_form.html', params)
#    form = DataPortalForm(request.POST)
#    a = form.is_valid()
#    if form.is_valid():
#        data = {
#            'error': 'false',
#            }
#    else:
#        data = {
#            'error': 'true',
#        }
#    data = simplejson.dumps(data)
#    return HttpResponse(data, mimetype='application/json')

def dataset_add(request):
    DatasetResourceFormset = inlineformset_factory(Dataset, Resource, extra=1, form=ResourceForm)
    if request.method == 'GET':
        return render(request, 'dataset/_add.html', {
            'current': 'dataset',
            'resourceFormset': DatasetResourceFormset(prefix='resource'),
            'datasetForm': DatasetForm(request=request),
            'geoTempForm': DatasetGeoTempContextForm(),
            'scientificForm': DatasetScientificContextForm()
        })
    if request.method == 'POST':
        data = request.POST
        data['state'] = 'AA'
        data['uploader'] = request.user.id
        datasetForm = DatasetForm(data, request=request)
        scf = DatasetScientificContextForm(data)
        gtf = DatasetGeoTempContextForm(data)
        if datasetForm.is_valid():
            dataset = datasetForm.save(commit=False)
            resourceForm = DatasetResourceFormset(prefix='resource', data=data, files=request.FILES, instance=dataset)
            if resourceForm.is_valid() and gtf.is_valid() and scf.is_valid():
                dataset.save()
                scf = scf.save(commit=False)
                scf.dataset = dataset
                scf.save()
                gtf = gtf.save(commit=False)
                gtf.dataset = dataset
                gtf.save()
                resources = resourceForm.save()
                return redirect('dataset_details', pk=dataset.id)
        resourceForm = DatasetResourceFormset(prefix='resource', data=data, files=request.FILES)
        return render(request, 'dataset/_add.html', {
            'current': 'dataset',
            'resourceFormset': resourceForm,
            'datasetForm': datasetForm,
            'geoTempForm': gtf,
            'scientificForm': scf,
        })


def dataset_extend(request, **kwargs):
    extension_attempt = kwargs.get('extension_attempt')
    index_of_extension_attempt = int(extension_attempt) - 1
    try:
        request.session['temp_extension_attempts'][index_of_extension_attempt]
    except IndexError:
        return redirect('dataset_details', pk=kwargs.get('pk'))
    datasetToBeExtended = Dataset.objects.get(pk=kwargs.get('pk'))
    oldTitle = datasetToBeExtended.title
    DatasetResourceFormset = inlineformset_factory(Dataset, Resource, extra=1, form=ResourceForm)
    if request.method == 'GET':
        datasetToBeExtended.title += '-' + request.session['temp_extension_attempts'][index_of_extension_attempt][
            'revision_type']
        datasetToBeExtended.publisher = 'colibri'
        datasetForm = DatasetForm(request=request, instance=datasetToBeExtended)
        return render(request, 'dataset/_extend.html', {
            'current': 'dataset',
            'resourceFormset': DatasetResourceFormset(prefix='resource'),
            'datasetForm': datasetForm,
            'geoTempForm': DatasetGeoTempContextForm(instance=datasetToBeExtended.geoTempContext),
            'scientificForm': DatasetScientificContextForm(instance=datasetToBeExtended.scientificContext),
            'datasetToBeExtended': datasetToBeExtended,
            'revision_type': request.session['temp_extension_attempts'][index_of_extension_attempt]['revision_type'],
            'short_description': request.session['temp_extension_attempts'][index_of_extension_attempt][
                'short_description'],
            'oldTitle': oldTitle
        })
    if request.method == 'POST':
        data = request.POST
        data = request.POST
        data['state'] = 'AA'
        data['uploader'] = request.user.id
        datasetForm = DatasetForm(data, request=request)
        scf = DatasetScientificContextForm(data)
        gtf = DatasetGeoTempContextForm(data)
        if datasetForm.is_valid():
            dataset = datasetForm.save(commit=False)
            resourceForm = DatasetResourceFormset(prefix='resource', data=data, files=request.FILES, instance=dataset)
            if resourceForm.is_valid() and gtf.is_valid() and scf.is_valid():
                dataset.save()
                scf = scf.save(commit=False)
                scf.dataset = dataset
                scf.save()
                gtf = gtf.save(commit=False)
                gtf.dataset = dataset
                gtf.save()
                resources = resourceForm.save()
                revision = RevisionDataset.objects.create(original=datasetToBeExtended, revision=dataset,
                                                          revision_type=data['revision_type'],
                                                          short_description=data['short_description'])
                revision.save()
                return redirect('dataset_details', pk=dataset.id)
        resourceForm = DatasetResourceFormset(prefix='resource', data=data, files=request.FILES)
        return render(request, 'dataset/_extend.html', {
            'current': 'dataset',
            'resourceFormset': resourceForm,
            'datasetForm': datasetForm,
            'geoTempForm': gtf,
            'scientificForm': scf,
            'datasetToBeExtended': datasetToBeExtended,
            'revision_type': data['revision_type'],
            'short_description': data['short_description'],
            'oldTitle': oldTitle
        })


def dataset_extend_modal(request, **kwargs):
    if request.method == 'GET':
        form_action = reverse('dataset_extend_modal', kwargs={'pk': kwargs.get('pk')})
        params = {'current': 'profile', 'form_action': form_action,
                  'dataset_extend_modal_form': DatasetExtendModalForm()}
        return render(request, 'dataset/_modal.html', params)
    if request.method == 'POST':
        modalForm = DatasetExtendModalForm(request.POST)
        if modalForm.is_valid():
            extension_attempt = {'revision_type': request.POST['revision_type'],
                                 'short_description': request.POST['short_description']}
            try:
                request.session['temp_extension_attempts']
            except KeyError:
                request.session['temp_extension_attempts'] = []
            request.session['temp_extension_attempts'].append(extension_attempt)
            request.session.modified = True
            dataset = Dataset.objects.get(pk=kwargs.get('pk'))
            #dataset.increase()
            return redirect('dataset_extend', extension_attempt=len(request.session['temp_extension_attempts']),
                            pk=kwargs.get('pk'))
        else:
            res = HttpResponse("Unauthorized")
            res.status_code = 401
            return res


def dataset_rate_modal(request, **kwargs):
    if request.method == 'GET':
        params = {'current': 'dataset', 'dataset_id': kwargs.get('pk'), 'rating_form': DatasetRatingForm()}
        return render(request, 'dataset/_modalRating.html', params)
    if request.method == 'POST':
        form = DatasetRatingForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.Rater = request.user
            a.dataset = Dataset.objects.get(pk=kwargs.get('pk'))
            a.save()
            params = {'current': 'dataset'}
            return HttpResponseRedirect(reverse('dataset_details', args=(a.dataset.id,)))


def dataset_increase_popularity(request, **kwargs):
    if request.method == 'POST':
        dataset = Dataset.objects.get(pk=kwargs.get('pk'))
        dataset.increase()
        res = HttpResponse("Success")
        res.status_code = 200
        return res
    else:
        res = HttpResponse("Unauthorized")
        res.status_code = 401
        return res


def dataset_rate_view_modal(request, **kwargs):
    from djangoratings.models import Vote;

    if request.method == 'GET':

        curDataset = Dataset.objects.get(pk=kwargs.get('pk'))
        #Get number of votes per Score value (1-5)
        scoreDistr = [0, 0, 0, 0, 0] #How many votes per Star
        relativeScoreDistr = [0, 0, 0, 0, 0] #Percentage of the votes to this star relative to all the votes
        votesCount = float(Vote.objects.all().filter(object_id=curDataset.id).count())
        if (votesCount > 0):
            for idx, val in enumerate(scoreDistr):
                curScoreidx = idx + 1
                scoreDistr[idx] = Vote.objects.all().filter(object_id=curDataset.id).filter(score=curScoreidx).count()
                relativeScoreDistr[idx] = int((scoreDistr[idx] / votesCount) * 100)

        #Get Accuracy, Completeness, Consistancy, Timeless Mean Score
        reviewDistr = [0, 0, 0, 0] #Mean of quality points (1-10 scale)
        relativereviewDistr = [0, 0, 0, 0] #Mean of quality points relative to 100
        resultsCount = DatasetIndividualRating.objects.all().filter(dataset=curDataset).count();
        if (resultsCount > 0):
            reviewDistr[0] = float(
                DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(Sum('Accurancy'))[
                    'Accurancy__sum']) / float(resultsCount)
            reviewDistr[1] = float(
                DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(Sum('Completeness'))[
                    'Completeness__sum']) / float(resultsCount)
            reviewDistr[2] = float(
                DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(Sum('Consistency'))[
                    'Consistency__sum']) / float(resultsCount)
            reviewDistr[3] = float(
                DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(Sum('Timelineness'))[
                    'Timelineness__sum']) / float(resultsCount)
            relativereviewDistr[0] = int(reviewDistr[0] * 10)
            relativereviewDistr[1] = int(reviewDistr[1] * 10)
            relativereviewDistr[2] = int(reviewDistr[2] * 10)
            relativereviewDistr[3] = int(reviewDistr[3] * 10)
            #Get Accuracy, Completeness, Consistancy, Timeless Standard Deviation - SQLLITE DOES NOT SUPPORT STD_DEV
        reviewDistrSTD = [0, 0, 0, 0]
        #if (resultsCount > 0):
        #reviewDistrSTD[0]=float(DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(StdDev('Accurancy'))['Accurancy__stddev'])
        #reviewDistrSTD[1]=float(DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(StdDev('Completeness'))['Completeness__stddev'])
        #reviewDistrSTD[2]=float(DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(StdDev('Consistency'))['Consistency__stddev'])
        #reviewDistrSTD[3]=float(DatasetIndividualRating.objects.all().filter(dataset=curDataset).aggregate(StdDev('Timelineness'))['Timelineness__stddev'])

        #Get individual reviews
        reviews = DatasetIndividualRating.objects.all().filter(dataset=curDataset)
        params = {'current': 'dataset', 'dataset_id': kwargs.get('pk'), 'resultsCount': resultsCount,
                  'relativeScoreDistr': relativeScoreDistr, 'scoreDistr': scoreDistr, 'reviewDistr': reviewDistr,
                  'relativereviewDistr': relativereviewDistr, 'reviewDistrSTD': reviewDistrSTD, 'reviews': reviews}
        return render(request, 'dataset/_modalViewRating.html', params)


def opendatasites(request):
    params = {'current': 'opendatasites'}
    return render(request, 'opendatasites/datasources_en.html', params)


def community(request):
    params = {'current': 'community'}
    return render(request, 'community.html', params)


def group_add(request):
    params = {'current': 'profile', 'group_form': GroupForm()}
    if (not request.is_ajax()):
        return HttpResponse('Unauthorized', status=401)
    if (request.method == 'POST'):
        form = GroupForm(request.POST)
        params['form'] = form
        if form.is_valid():
            owner_id = str(request.user.id)
            name = request.POST['name'].strip()
            organization = Organization.objects.create(name=name, slug=get_slug(name), is_active=True)
            add_user(request, organization, request.user, True, True)
            admin_ids = array_unique(array_diff(array_explode(',', request.POST['admins']), [owner_id]))
            member_ids = array_unique(
                array_diff(array_diff(array_explode(',', request.POST['members']), admin_ids), [owner_id]))
            if admin_ids != ['']:
                for admin in User.objects.filter(id__in=admin_ids):
                    if not organization.is_member(admin):
                        add_user(request, organization, admin, True)
            if member_ids != ['']:
                for member in User.objects.filter(id__in=member_ids):
                    if not organization.is_member(member):
                        add_user(request, organization, member)
            return HttpResponse('OK', status=200)
        return HttpResponse('BadRequest', status=400)
    return render(request, 'profile/_add_group.html', params)


def add_user(request, organization, user, is_admin=False, is_owner=False):
    org_user = OrganizationUser.objects.create(user=user,
                                               organization=organization, is_admin=is_admin)
    if is_owner:
        OrganizationOwner.objects.create(organization=organization,
                                         organization_user=org_user)
    send_mail('colibri Portal Notification',
              'You have been added to the colibri portal group ' + organization.name + ' by user ' + request.user.username +
              '. In case you wish to leave the group,' +
              ' you can do so visiting the "My Groups" tab in "My Profile" in the colibri portal at http://www.colibridata.eu.' +
              ' \n \n' +
              'About colibri' +
              '\n' + '---------------------' +
              '\n \n' +
              'The main goal of the colibri project is the development and use of a data infrastructure, incorporating distributed and diverse public sector information (PSI) resources, capable of supporting scientific collaboration and research, particularly for the Social Science and Humanities (SSH) scientific communities, while also empowering the deployment of open governmental data towards citizens.' +
              'The colibri e-infrastructure is envisaged to promote a highly synergetic approach to governance research, by providing the ground for experimentation to actors from both ICT and non-ICT related disciplines and scientific communities, as well as by ensuring that the scientific outcomes are made accessible to the citizens, so that they can monitor public service delivery and influence the decision making process.' +
              '\n \n' +
              'colibri is a combination of CP & CSA project funded under the European Commission FP7 Programme. To find out more about the project, visit http://www.colibri-project.eu',
              'no-reply@colibrintua.com', [user.email], fail_silently=False)
    return org_user


# au
import simplejson as json
# from haystack.query import SearchQuerySet

import logging

# def autocomplete(request):
#     logging.error("starting............")
#     print "koukli"
#     sqs = SearchQuerySet().autocomplete(title=request.GET.get('q', ''))[:5]
# #    sqs = SearchQuerySet().autocomplete(nameAppearance='kou')
#     logging.error("success!!!!!!!!!")
#     suggestions = [result.title for result in sqs]
#     logging.error(suggestions)
#     # Make sure you return a JSON object, not a bare list.
#     # Otherwise, you could be vulnerable to an XSS attack.
#     the_data = json.dumps({
#         'results': suggestions
#     })
#     return HttpResponse(the_data, content_type='application/json')

def autocomplete_template(request):
    return render(request, 'autocomplete.html')


class UserUpdateView(UpdateView):
    form_class = UserForm
    model = User
    template_name = 'profile/_edit.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        user = self.object
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['current'] = 'account-settings'
        context['userProfileForm'] = UserProfileForm(instance=user.profile)
        context['userModel'] = user
        return context

    def get(self, *args, **kwargs):
        if (str(self.request.user.id) != str(kwargs.get('pk'))):
            res = HttpResponse("Unauthorized")
            res.status_code = 401
            return res
        else:
            return super(UserUpdateView, self).get(self, *args, **kwargs)

    def get_success_url(self, **kwargs):

        return "/profile/" + kwargs.get('pk')

    def post(self, *args, **kwargs):
        if (str(self.request.user.id) != str(kwargs.get('pk'))  ):
            res = HttpResponse("Unauthorized")
            res.status_code = 401
            return res
        else:
            data = self.request.POST
            user = self.request.user
            data['password'] = user.password
            data['date_joined'] = user.date_joined
            data['last_login'] = user.last_login
            data['is_active'] = user.is_active
            data['is_staff'] = user.is_staff
            data['is_superuser'] = user.is_superuser
            userForm = UserForm(data, instance=user)
            if userForm.is_valid():
                user = userForm.save(commit=False)
                userProfileForm = UserProfileForm(self.request.POST, instance=user.profile)
                if userProfileForm.is_valid():
                    user.save()
                    userProfile = userProfileForm.save(commit=False)
                    userProfile.user = user
                    userProfile.save()
                    if 'picture' in self.request.FILES:
                        picture = self.request.FILES['picture']
                        avatar = userProfile.avatar
                        avatar.photo_original = picture
                        avatar.save()
                    return redirect(self.get_success_url(**kwargs))
            return render(self.request, 'profile/_edit.html', {
                'current': 'account-settings',
                'form': userForm,
                'userProfileForm': userProfileForm,
                'userModel': user
            })


# Visualizations STABILIZE
def externalvis(request, application_pk):
    app = Application.objects.get(id=application_pk)
    app_url = app.url
    dataset_id = app.dataset.id
    params = {'current': 'dataset', 'application_url': app_url, 'dataset_id': dataset_id}
    return render(request, 'visualization/external.html', params)


def evisuals(request, pk):
    resource = Resource.objects.get(id=pk)
    params = {'current': 'about', 'pk': pk, 'dataset_pk': resource.dataset.id}
    return render(request, 'visualization/visual2.html', params)


def evisualjsons(request, pk):
    if request.method == 'GET':
        from jsonHandler import generatingJsonFormat

        resource = Resource.objects.get(id=pk)

        if not resource:
            return "no dataset found"

        # resource = Resource.objects.get(id=pk)
        if str(resource.file) == '':
            url = resource.uri
        else:
            url = "https://" + settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/" + str(resource.file)

        if "xls" in url:

            # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
            # file = urllib.urlretrieve(url, "temporaryFile.xls")
            file = urllib.urlretrieve(url, "temporaryFile.xls")
            #heroku save
            # json_data = generatingJsonFormat.ExcelHandling(file="temporaryFile.xls").result()
            json_data = generatingJsonFormat.ExcelHandling(file="temporaryFile.xls").result()


        elif "csv" in url:

            # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
            file = urllib.urlretrieve(url, "temporaryFile.csv")
            #heroku save
            json_data = generatingJsonFormat.CsvHandling(file="temporaryFile.csv").result()

        if (request.user.is_authenticated()) and (request.user == resource.dataset.uploader):
            json_data["access"] = "write"
        elif request.user.is_authenticated():
            json_data["access"] = "create"
        else:
            json_data["access"] = "read"
        json_data = simplejson.dumps(json_data)

        if request.method == 'GET':
            response = HttpResponse(json_data, mimetype='application/json')
            response['Content-Disposition'] = "filename=%s" % 'france-elections.json'
            return response

            #     #Save the JSON object
            # if request.method == 'POST':
            #     if 'filename' in request.POST.keys() :
            #         #Export datagrid to CSV
            #         csv_data = request.POST['data']
            #         response = HttpResponse(csv_data,content_type='text/csv')
            #         response['Content-Disposition'] = 'attachment; filename="'+ request.POST['filename'] + '"'
            #         return response
            #     else:
            #         # Save Visualization State
            #         json_data = request.raw_post_data
            #         #SAVE json_data to Amazon S3
            #         #.........
            #         json_file= open('colibri/static/visualizations/france-elections2.json','w')
            #         json_file.write(json_data)
            #         json_file.close()
            #         response = HttpResponse(json_data,mimetype='application/json' )
            #         return response

    if request.method == 'POST':

        if 'filename' in request.POST.keys():
            #Export datagrid to CSV
            csv_data = request.POST['data']
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + request.POST['filename'] + '"'
            return response
        if not request.user.is_authenticated():
            return HttpResponse('No logged-in User', status=400)
        Cvisualization = Visualization()
        Cvisualization.user = request.user
        Cvisualization.body = request.body #request.body
        curTitle = json.loads(request.body).get("title")
        if curTitle:
            Cvisualization.title = curTitle
        Cvisualization.resource = Resource.objects.get(id=pk)
        try:
            Cvisualization.save()
            CApplication = Application.objects.create(dataset=Cvisualization.resource.dataset, uploader=request.user)
            CApplication.type = "VI"
            CApplication.title = Cvisualization.title
            CApplication.url = settings.LOGIN_REDIRECT_URL + "views/%d/saved/%d/" % (
            Cvisualization.resource.id, Cvisualization.id)
            CApplication.save()
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse('' + str(e) + '', status=400)


def evisualsSaved(request, pk, saved):
    resource = Resource.objects.get(id=pk)
    params = {'current': 'about', 'pk': pk, 'dataset_pk': resource.dataset.id, 'saved': saved}
    return render(request, 'visualization/visualSaved.html', params)


def evisualjsonsSaved(request, pk, saved):
    Cvisualization = Visualization.objects.get(id=saved)

    meta = Cvisualization.body

    if request.method == 'GET':
        from jsonHandler import generatingJsonFromSaved

        resource = Resource.objects.get(id=pk)

        if not resource:
            return "no dataset found"

        # resource = Resource.objects.get(id=pk)
        if str(resource.file) == '':
            url = resource.uri
        else:
            url = "https://" + settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/" + str(resource.file)

        if "xls" in url:

            # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
            file = urllib.urlretrieve(url, "temporaryFile.xls")
            #heroku save
            json_data = generatingJsonFromSaved.ExcelHandling(file="temporaryFile.xls", meta=meta).result()
            #.././tmp/temporaryFile

        elif "csv" in url:

            # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
            file = urllib.urlretrieve(url, "temporaryFile.csv")
            #heroku save
            json_data = generatingJsonFromSaved.CsvHandling(file="temporaryFile.csv", meta=meta).result()

        if (request.user.is_authenticated()) and (request.user == resource.dataset.uploader):
            json_data["access"] = "write"
        elif request.user.is_authenticated():
            json_data["access"] = "create"
        else:
            json_data["access"] = "read"
        json_data = simplejson.dumps(json_data)

        if request.method == 'GET':
            response = HttpResponse(json_data, mimetype='application/json')
            response['Content-Disposition'] = "filename=%s" % 'france-elections.json'
            return response

            #     #Save the JSON object
            # if request.method == 'POST':
            #     if 'filename' in request.POST.keys() :
            #         #Export datagrid to CSV
            #         csv_data = request.POST['data']
            #         response = HttpResponse(csv_data,content_type='text/csv')
            #         response['Content-Disposition'] = 'attachment; filename="'+ request.POST['filename'] + '"'
            #         return response
            #     else:
            #         # Save Visualization State
            #         json_data = request.raw_post_data
            #         #SAVE json_data to Amazon S3
            #         #.........
            #         json_file= open('colibri/static/visualizations/france-elections2.json','w')
            #         json_file.write(json_data)
            #         json_file.close()
            #         response = HttpResponse(json_data,mimetype='application/json' )
            #         return response

    if request.method == 'POST':
        if 'filename' in request.POST.keys():
            #Export datagrid to CSV
            csv_data = request.POST['data']
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + request.POST['filename'] + '"'
            return response
        if not request.user.is_authenticated():
            return HttpResponse('No logged-in User', status=400)
        Cvisualization = Visualization()
        Cvisualization.user = request.user
        Cvisualization.body = request.body #request.body
        curTitle = json.loads(request.body).get("title")
        if curTitle:
            Cvisualization.title = curTitle
        Cvisualization.resource = Resource.objects.get(id=pk)
        try:
            Cvisualization.save()
            CApplication = Application.objects.create(dataset=Cvisualization.resource.dataset, uploader=request.user)
            CApplication.type = "VI"
            CApplication.title = Cvisualization.title
            CApplication.url = settings.LOGIN_REDIRECT_URL + "views/%d/saved/%d/" % (
            Cvisualization.resource.id, Cvisualization.id)
            CApplication.save()
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse('' + str(e) + '', status=400)


def dataset_details_view(request, pk):
    """
    	{
		"datasetName" : "my_new_ds",
		"resources" : [{
				"fileName" : "athens demo.XLS",
				"type" : "XLS",
				"name" : "athens demo",
				"id" : "athens demo.XLS",
				"uri" : "http://myhost/resources/athens+demo.XLS"
			}
		],
		"id" : "10213.275233201115",
		"uri" : "http://localhost/datasets\10213.275233201115"
	}

    """

    if request.method == 'GET':

        final_json = {}

        dataset = Dataset.objects.get(id=pk)

        final_json["datasetName"] = dataset.title
        final_json["id"] = dataset.id
        final_json["uri"] = "http://www.colibridata.eu/dataset/%d/" % dataset.id

        res_list = []
        for resource in dataset.resources:
            res = {}

            if str(resource.file) == '':
                url = str(resource.uri)
            else:
                url = "https://" + settings.AWS_STORAGE_BUCKET_NAME + ".s3.amazonaws.com/" + str(resource.file)

            if "xlsx" in url.lower():
                type = "XLSX"
            elif "xls" in url.lower():
                type = "XLS"
            elif "csv" in url.lower():
                type = "CSV"
            else:
                type = ""

            filename = str(resource.file).replace("resources/dataset_%d/" % dataset.id, "")

            res["fileName"] = filename
            res["type"] = type
            res["name"] = filename
            res["id"] = resource.id
            res["uri"] = url

            res_list.append(res)

        final_json["resources"] = res_list

        json_data = simplejson.dumps(final_json)

        response = HttpResponse(json_data, mimetype='application/json')

        return response


class ApplicationDetailView(DetailView):
    model = Application
    template_name = 'application/application-details.html'
    context_object_name = 'application'


class ApplicationListView(ListView):
    model = Application
    template_name = 'application/application-list.html'
    context_object_name = 'applicationlist'
    paginate_by = 25
