import urllib

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from colibri.models import Resource
from colibri.models import Dataset, DatasetGeoTempContext, DatasetScientificContext
import unicodecsv


class Command(BaseCommand):
    args = '<url>'
    help = 'The url of the data_file to harvest'

    def handle(self, *args, **options):
        #import pdb;pdb.set_trace()
        for url in args:
            if ("http" in url):
                file = urllib.urlopen(url)
            else:
                file = open(url, 'r')
            if (file):
                csv_data = unicodecsv.reader(file, delimiter=',', quotechar='"', encoding='utf-8')
                curUser = User.objects.get(pk=145)

                for i, row in enumerate(csv_data):
                    try:
                        if (i != 0 ):
                            #Write row to database
                            if (i % 100 == 0): print 'Current line:' + str(i)
                            #Dataset
                            if (Dataset.objects.filter(title=row[3]).count() == 0):
                                curDataset = Dataset.objects.create(uploader=curUser)
                                curDataset.title = row[3]
                                curDataset.description = row[4]
                                curDataset.categories = row[5]
                                curDataset.url = row[6]
                                curDataset.license = row[7]
                                curDataset.country = row[8]
                                curDataset.author = row[11]
                                curDataset.publisher = row[12]
                                if (row[14] != ''): curDataset.date_published = row[14]
                                curDataset.save()
                                #Resource
                                for x in range(10):
                                    if (row[27 + x] != 'N/A' and row[27 + x] != ''):
                                        resource = Resource.objects.create(dataset=curDataset)
                                        resource.uri = row[27 + x]
                                        resource.description = row[37 + x]
                                        resource.language = row[26]
                                        resource.save()
                                    #Temporal
                                temporal = DatasetGeoTempContext.objects.create(dataset=curDataset)
                                if (row[15] != ''): temporal.temporal_granularity = row[15]
                                if (row[16] != ''): temporal.temporal_coverage_from = row[16]
                                if (row[17] != ''): temporal.temporal_coverage_to = row[17]
                                if (row[18] != ''): temporal.geographical_granularity = row[18]
                                if (row[19] != ''): temporal.geographical_coverage = row[19]
                                temporal.save()
                                #Scientific
                                scientific = DatasetScientificContext.objects.create(dataset=curDataset)
                                scientific.save()
                            else:
                                print("Record exists.Skipping line " + str(i))
                    except Exception as e:
                        print ('Error at line ' + str(i) + '.' + str(e))
                        try:
                            curDataset.delete()
                            scientific.delete()
                            temporal.delete()
                        except Exception as l:
                            print('Cannot delete:' + str(e))
                        
