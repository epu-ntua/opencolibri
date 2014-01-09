__author__ = 'mpetyx'

import csv
import json

import xlrd


def csv_from_excel():
    wb = xlrd.open_workbook('SampleData.xls')
    names = wb.sheet_names()
    sh = wb.sheet_by_name(names[0])
    your_csv_file = open('your_csv_file.csv', 'wb')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in xrange(sh.nrows):
        # print sh.row_values(rownum)
        try:
            wr.writerow(sh.row_values(rownum))
        except:
            continue

    your_csv_file.close()


def json_from_csv():
    f = open('your_csv_file.csv', 'rU')
    # Change each fieldname to the appropriate field name. I know, so difficult.
    reader = csv.DictReader(
        f)#, fieldnames = ( "fieldname0","fieldname1","fieldname2","fieldname3","fieldname4","fieldname5" ))
    # Parse the CSV into JSON
    print reader
    for row in reader:
        print row
        # break
    out = json.dumps([row for row in reader])
    print "JSON parsed!"
    # Save the JSON
    f = open('your_csv_file.json', 'w')
    f.write(out)
    print "JSON saved!"


csv_from_excel()
json_from_csv()

