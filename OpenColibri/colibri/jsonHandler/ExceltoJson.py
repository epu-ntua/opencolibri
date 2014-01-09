__author__ = 'mpetyx'

from collections import OrderedDict

import simplejson as json

import xlrd


wb = xlrd.open_workbook('views.xls')
sh = wb.sheet_by_index(0)

cars_list = []

for rownum in range(1, sh.nrows):
    cars = OrderedDict()
    row_values = sh.row_values(rownum)
    cars['car-id'] = row_values[0]
    cars['make'] = row_values[1]
    cars['model'] = row_values[2]
    cars['miles'] = row_values[3]

    cars_list.append(cars)

cars2 = OrderedDict()
cars2['meta'] = cars_list
carsduo = []
carsduo.append(cars2)

j = json.dumps(carsduo, sort_keys=True, indent=4 * ' ')

with open('data2.json', 'w') as f:
    f.write(j)

f.close()

print "finished"


class ExcelToJson():
    def __init__(self):
        """

        to
        """