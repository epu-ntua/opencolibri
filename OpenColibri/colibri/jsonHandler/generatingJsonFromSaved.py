__author__ = 'mpetyx'

__author__ = 'mpetyx'

import csv
import json

import xlrd
import unicodecsv


def numeric(s):
    try:
        i = float(s)
        return True
    except ValueError, TypeError:
        return False


def meta(s):
    """

    :rtype : json
    """
    # s = s.replace("<QueryDict: {u'","")
    # s = s.replace("': [u'']}>","")
    # lol = json.loads(s)
    # lol = lol["meta"]
    lol = json.loads(s)
    lol = lol["meta"]
    return lol


def filters(s):
    # s = s.replace("<QueryDict: {u'","")
    # s = s.replace("': [u'']}>","")
    # lol = json.loads(s)
    lol = json.loads(s)
    try:
        lol = lol["filters"]
    except:
        lol = []
    return lol


def search_numeric_only(l):
    empty = []
    for element in l:
        if numeric(element):
            empty.append(float(element))

    return empty


class Generator():
    def __init__(self, meta):

        self.meta = meta
        self.aware = None

    def main(self, rows, columns):
        # import pdb;pdb.set_trace()
        final_json = {}
        final_json["meta"] = meta(self.meta)
        final_json["meta"]["filter"] = filters(self.meta)
        final_json["filters"] = filters(self.meta)
        final_json["items"] = self.fields_popularize(rows[1:])
        # final_json["access"] = "write"

        return final_json


    def set_the_fields_and_meta(self, columns):

        meta = {}
        attributes = []

        """
        in this method we are going to create the attributes, like this.
        {
                "name": "field_3",
                "label": "Geolocation - Latitude",
                "dataType": "number",
                "dataTypeQualifier": "sequential",
                "timezone": 0,
                "uniqueValues": null,
                "min": 41.85,
                "max": 49.8833333333,
                "format": {
                    "width": null,
                    "position": "3"
                }
            },
        """

        column = 0

        label = 0
        while column < len(columns):

            current_field = {}
            current_field["name"] = "field_%d" % (column + 1)
            current_field["label"] = "%s" % columns[column][label]
            current_field["dataType"] = self.search_datatype(columns[column][label:])
            if current_field["dataType"] == "number":
                current_field["min"] = min(search_numeric_only(columns[column][label:]))
                current_field["max"] = max(search_numeric_only(columns[column][label:]))
                current_field["dataTypeQualifier"] = "sequential"
                current_field["uniqueValues"] = None
            else:
                current_field["min"] = 0
                current_field["max"] = 0
                current_field["dataTypeQualifier"] = "qualitative"
                current_field["uniqueValues"] = self.find_distinct_values(column=columns[column][label:])

            current_field["timezone"] = 0

            current_field["format"] = {"width": None, "position": column}

            attributes.append(current_field)

            column = column + 1

        meta["attributes"] = attributes

        meta["columnCount"] = len(columns) - 1
        meta["locationFields"] = []
        meta["filter"] = {}
        meta["vis"] = {}
        meta["id"] = 1 #dataset.id
        meta["name"] = "file.xls" #dataset.resources.filename
        meta["description"] = "Buggy parser yet to be fixed" #dataset.description
        meta["datasetId"] = "33ad5b83-cb8a-4d6f-916f-a4eb6cbd878a"
        meta["createdOn"] = 1341098532634
        meta["updatedOn"] = 1341098532634
        meta["createdBy"] = None #dataset.author
        meta["updatedBy"] = "12560"

        return meta


    def find_max_and_min_per_column(self, column):

        return {'max': max(column), 'min': min(column)}

    def find_distinct_values(self, column):

        return list(set(column))

    def search_datatype(self, column):

        try:
            if float(column[(len(column) - 1) / 2]):
                return "number"
        except:
            temp = 2

        return "string"
        # if type(column[(len(column)-1)/2])==str:
        #     return "string"
        # else:
        #     return "number"

    def read_row(self, row):
        self.aware

    def fields_popularize(self, rows):

        """
        creating all the items of the format
        {
            "field_4": 0.666666666667,
            "field_3": 48.1666666667,
            "field_2": "Pays de la Loire",
            "field_1": "Mayenne",
            "field_7": 100,
            "field_8": 86.6,
            "field_10": 3.92,
            "field_5": 55.45,
            "field_6": 44.55,
            "field_9": 82.68
        },

        """
        items = []

        for row in rows:

            column = 0
            currentitem = {}
            while column < len(row):
                currentitem["field_%d" % (column + 1)] = row[column]
                column = column + 1
            items.append(currentitem)

        return items


class ExcelHandling():
    def __init__(self, file=None, meta=None):

        self.meta = meta
        if file is None:
            wb = xlrd.open_workbook('SampleData.xls')
        else:
            wb = xlrd.open_workbook(file)

        sh1 = wb.sheet_by_index(0)
        rows = []
        columns = []

        for rownum in range(sh1.nrows): # sh1.nrows -> number of rows (ncols -> num columns)
            rows.append(sh1.row_values(rownum))

        # print rows

        for column in range(sh1.ncols):
            columns.append(sh1.col_values(column))

        # print columns

        res = Generator(meta=self.meta).main(rows=rows, columns=columns)

        # print res
        #
        # import simplejson
        # res = simplejson.dumps(res)#, indent=4 * ' ')

        # with open('data2.json', 'w') as f:
        #     f.write(res)
        #
        # f.close()

        self.res = res

    def result(self):

        return self.res


class CsvHandling():
    def __init__(self, file=None, meta=None):

        filesniff = open(file)
        try:
            dialect = unicodecsv.Sniffer().sniff(filesniff.read(1024))
            wb = unicodecsv.reader(open(file), dialect, encoding='utf-8')
        except Exception:
            wb = unicodecsv.reader(open(file), delimiter=',', encoding='utf-8')

        self.meta = meta
        # if file is None:
        #     wb = csv.reader(open('visualizable-iso-greek.csv', 'rU'))
        # else:
        #     wb = csv.reader(open(file, 'rU'))

        self.wb = wb

        reader = wb
        rows = []
        columns = []
        #
        # for rownum in range(sh1.nrows): # sh1.nrows -> number of rows (ncols -> num columns)
        #     rows.append(sh1.row_values(rownum))

        for row in reader:
            rows.append(row)

        print rows

        columns = self.columnsExtract(rows)

        print columns

        res = Generator(meta=self.meta).main(rows=rows, columns=columns)

        self.res = res

    def result(self):

        return self.res

    def columnsExtract(self, rows):

        columns = []

        num_col = len(rows[0])
        for enumeration in range(num_col):
            column = []
            for row in rows:
                column.append(row[enumeration])
            columns.append(column)

        return columns

    def exportToApi(self):

        # reader = csv.DictReader( self.wb)#, fieldnames = ( "fieldname0","fieldname1","fieldname2","fieldname3","fieldname4","fieldname5" ))
        reader = self.wb
        # Parse the CSV into JSON
        print reader
        # for row in reader:
        #     print row
        #     break
        out = json.dumps([row for row in reader])

        return out

        # Generator().main([["pedio1", 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 1],["pedio3", 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 1],["pedio2", 1, 1, 3, 3, 3, 1, 2, 3, 2, 1, 1]])

        # ExcelHandling()
        # import urllib
        # url = "https://colibrifp7.s3.amazonaws.com/resources/dataset_8/Greek%20Boroughs%20Longitude%20and%20Latitude.xlsx?Signature=%2BEAdj1fZtwD6f3QAnBtkhJolgDU%3D&Expires=1364743699&AWSAccessKeyId=AKIAJ3OQUQKOETJFUEAQ"
        # file = urllib.urlretrieve(url, ".././tmp/skatoula.xls")
        # #heroku save
        # print ExcelHandling(file=".././tmp/skatoula.xls").result()
        # print CsvHandling().exportToApi()
        # print CsvHandling().result()
        # print CsvHandling().result()

        # print numeric("10.000")

        # print max(search_numeric_only(["oy","1","5.42",9.342483]))