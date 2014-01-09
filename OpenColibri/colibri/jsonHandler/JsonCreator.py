__author__ = 'mpetyx'

"""
{
    "meta": {
        "rowCount": 55,
        "locationFields": [],
        "filter": {},
        "vis": {},
        "attributes": [
        {
        {
        {
        }

        ],
              "id":33,
      "name":"crime-rates.xlsx",
      "description":"Test case, automatically added.",
      "datasetId":"1234-5678-90",
      "createdOn":1357936321929,
      "updatedOn":1357936321929,
      "createdBy":"author",
      "updatedBy":"owner"
      },

        "items":

"""

import jsonpickle

jsonpickle.set_preferred_backend('simplejson')


class Pickle():
    def __init__(self, attributes=None, rowCount=None, locationFields=None, filter=None, vis=None, name=None,
                 description=None, datasetId=None, createdOn=None, updatedOn=None, createdBy=None, updatedBy=None):
        self.rowCount = rowCount
        self.locationFields = locationFields
        self.filter = filter
        self.vis = vis

        self.name = name
        self.description = description
        self.datasetId = datasetId
        self.createdOn = createdOn
        self.updatedOn = updatedOn
        self.createdBy = createdBy
        self.updatedBy = updatedBy

        before = []

        for attribute in attributes:
            before.append({"%d" % attribute: attribute})
        self.attributes = before


class Final():
    def __init__(self, items=None, attributes=None, rowCount=None, locationFields=None, filter=None, vis=None,
                 name=None, description=None, datasetId=None, createdOn=None, updatedOn=None, createdBy=None,
                 updatedBy=None):
        pivkle = Pickle(attributes=attributes, locationFields=locationFields, rowCount=rowCount, filter=filter, vis=vis,
                        name=name, description=description, datasetId=datasetId, createdOn=createdOn,
                        updatedOn=updatedOn, createdBy=createdBy, updatedBy=updatedBy)
        self.meta = jsonpickle.encode(pivkle, unpicklable=False)

        before = []

        for item in items:
            before.append({"%d" % item: item})

        self.items = before

    #pickled = jsonpickle.encode(Pickle(), unpicklable=False)
#print pickled

obj = Final(items=[1, 2, 3, 4], attributes=[1, 2], locationFields="athens", rowCount=35, filter=None, vis={},
            name="Michael", description="einai enas kouklos", datasetId="32387213594382423", createdOn="pote vasika",
            updatedOn=None, createdBy=None, updatedBy=None)
pickle = jsonpickle.encode(obj, unpicklable=False)

print pickle

import simplejson

simplejson.dumps(pickle)
print simplejson.dumps(pickle)
# print pickle.replace(r"\'", "")
# string.replace("'", r"\'")