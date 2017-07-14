import sys;
from datetime import datetime;

file = open(sys.argv[1]);

lines = file.read().split('\n');

# get the lines themselves
lines = list(map(lambda x: x.split(',')[-4:], lines));

# remove lines with empty info
lines = filter(lambda x: not [''] * 3 == x[:-1], lines);

# remove lines without true_unsafe modules
# (they have a date of last modification)
lines = filter(lambda x: not x[2] == '', lines);

# transform string date into python date
lines = list( map(lambda x:
                  [x[0], datetime.strptime(x[2], '%d.%m.%Y').date(),
                   int(x[3][0])],
                  lines[1:]));

print lines
