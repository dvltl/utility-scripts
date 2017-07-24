#!/usr/bin/python

# https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# https://developers.google.com/sheets/api/quickstart/python

import sys
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

def open_spreadsheet(name):
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open(name).sheet1

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    return list_of_hashes

def pretty_print(list):
    step = '\n\t\t'
    for item in list:
        s = item[_module] + '\n'
        s += '\t' + _date + step + item[_date].strftime('%d.%m.%Y') + '\n'
        if item[_dtag][_true]:
            s += '\t' + _true + step + ', '.join(item[_dtag][_true]) + '\n'
        if item[_dtag][_false] and show_false:
            s += '\t' + _false + step + ', '.join(item[_dtag][_false]) + '\n'
        s += '\t' + _sent + step + str(item[_sent]) + '\n'
        print(s)

def print_stats(list):
    print('Number of modules found: ' + str(len(list)) + '\n')
    all_tags = set()
    for item in list:
        all_tags |= item[_dtag][_true]
        all_tags |= item[_dtag][_false]

    for tag in all_tags:
        num = 0
        for item in list:
            if tag in item[_dtag][_true]:
                num += 1
                prefix = _true
            elif tag in item[_dtag][_false] and show_false:
                num += 1
                prefix = _false
        if num > 0:
            print('Number of modules with tag <' + prefix + ':' + tag + '>: ' + str(num))

def setify_tags(item):
    tag = item[_dtag].split('; ')
    item[_dtag] = {_true: set(), _false: set()}
    if item[_tag] == _true or item[_tag] == _false:
        item[_dtag][item[_tag]] |= set(tag)
    return item

def transform_numeric(item):
    item[_date] = datetime.strptime(item[_date], '%d.%m.%Y').date()
    item[_sent] = int(item[_sent])
    return item

def cut(item):
    for key in [_desc,_comment,_day,_vo,_errid]:
        del item[key]
    return item

def gather_tags(lines):
    i = 0
    j = 1
    while i < len(lines) - 1 and j < len(lines):
        if not lines[i][_module] == '':
            if len(lines[j]) > 0 and lines[j][_module] == '':
                lines[i][_dtag][_true] |= lines[j][_dtag][_true]
                if show_false:
                    lines[i][_dtag][_false] |= lines[j][_dtag][_false]
            else:
                i = j
            j += 1
    return lines



def preprocess(lines):

    lines = map(cut, lines)

    # gather true_unsafe tags for each file
    lines = list(map(setify_tags, lines))

    # remove false_unsafes and errors
#    lines = filter(lambda x: 'true_unsafe' in x[_tag], lines)

    lines = gather_tags(lines)

    # remove lines without info on true_unsafe modules
    # (they don't have a date of last modification)
    lines = filter(lambda x: not x[_date] == '', lines)

    # transform string date into python date
    lines = list(map(transform_numeric, lines))

    # filter all of the modules which maintainers had been notified about the problem
    lines = list(filter(lambda x: x[_sent] == 0, lines))

    # sort data by last modified date
    lines.sort(key=lambda x: x[_date], reverse=True)
    return lines

def filter_by_tag(input_lines, tag):
    lines = list(filter(lambda x: tag in x[_dtag][_true] | x[_dtag][_false], input_lines))
    return lines

####################################################################

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

lines = open_spreadsheet("sync:race tagged")

_tag = 'Tag'
_dtag = 'DetailedTag'
_sent = 'Message sent'
_date = 'Last change to source code'
_comment = 'Launch information'
_vo = 'Verification object'
_errid = 'Error trace identifier'
_desc = 'Description'
_module = 'Module'
_day = 'Day'
_true = 'true_unsafe'
_false = 'false_unsafe'

show_false = not '--no-false' in sys.argv

lines = preprocess(lines)

if '--tag' in sys.argv:
    lines = filter_by_tag(lines, sys.argv[sys.argv.index('--tag') + 1])

pretty_print(lines)

if '--print-stats' in sys.argv:
    print_stats(lines)
