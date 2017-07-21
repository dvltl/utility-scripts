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
        s += '\t' + _dtag + step + ', '.join(item[_dtag]) + '\n'
        s += '\t' + _sent + step + str(item[_sent]) + '\n'
        print(s)

def print_stats(list):
    print('Number of modules with true_unsafes: ' + str(len(list)) + '\n')
    all_tags = set()
    for item in list:
        all_tags |= item[_dtag]

    for tag in all_tags:
        num = 0
        for item in list:
            if tag in item[_dtag]:
                num += 1
        print('Number of modules with tag <' + tag + '>:' + str(num))

def setify_tags(item):
    tag = item[_dtag].split('; ')
    item[_dtag] = set()
    item[_dtag] |= set(tag)
    return item

def transform_numeric(item):
    item[_date] = datetime.strptime(item[_date], '%d.%m.%Y').date()
    item[_sent] = int(item[_sent])
    return item

def cut(item):
    for key in [_tag,_desc,_comment,_day,_vo,_errid]:
        del item[key]
    return item

def preprocess(lines):
    # remove false_unsafes and errors
    lines = filter(lambda x: 'true_unsafe' in x[_tag], lines)

    lines = map(cut, lines)

    # gather true_unsafe tags for each file
    lines = list(map(setify_tags, lines))

    i = 0
    j = 1
    while i < len(lines) - 1 and j < len(lines):
        if not lines[i][_module] == '':
            if len(lines[j]) > 0 and lines[j][_module] == '':
                if not '' in lines[j][_dtag]:
                    lines[i][_dtag] |= lines[j][_dtag]
            else:
                i = j
            j += 1

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
    lines = list(filter(lambda x: tag in x[_dtag], input_lines))
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

lines = preprocess(lines)

if len(sys.argv) > 1:
    lines = filter_by_tag(lines, sys.argv[1])

pretty_print(lines)
print_stats(lines)
