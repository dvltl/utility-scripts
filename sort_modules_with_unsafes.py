#!/usr/bin/python

# https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# https://developers.google.com/sheets/api/quickstart/python

import sys;
from datetime import datetime;

def list_print(list):
    for item in list:
        print item

def preprocess(input_lines):
    # get the lines themselves
    lines = list(map(lambda x: x.split(',')[-4:], input_lines))

    # add tags
    for i in range(len(input_lines)):
        line = input_lines[i].split(',')
        lines[i].append(line[3])
        lines[i].append(line[4])

    # remove false_unsafes and errors
    lines = filter(lambda x: 'true_unsafe' in x[4], lines)

    # gather true_unsafe tags for each file
    print 'Only true_unsafe'
    list_print(lines)

    # remove lines with empty info
    lines = filter(lambda x: not [''] * 3 == x[:-1], lines)

    # remove lines without true_unsafe modules
    # (they have a date of last modification)
    lines = filter(lambda x: not x[2] == '', lines)

    # transform string date into python date
    lines = list( map(lambda x:
                      [x[0], datetime.strptime(x[2], '%d.%m.%Y').date(),
                       int(x[3][0]), x[4]],
                      lines[1:]))

    # sort data by last modified date
    lines.sort(key=lambda x: x[1], reverse=True)
    return lines

def filter_by_tag(input_lines, tag):
    lines = filter(lambda x: tag in x[3], input_lines)
    return lines

file = open(sys.argv[1])
lines = file.read().split('\n')

lines = preprocess(lines)

if len(sys.argv) > 2:
    lines = filter_by_tag(lines, sys.argv[2])

print
list_print(lines)
