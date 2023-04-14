#!/usr/bin/env python3
from os import listdir
import re
from sys import argv

# read arguments
arguments = argv[1:]

# define regular expression depending on arguments
if len(arguments) > 0 and arguments[0] == 'ALL':
    regex = re.compile(r'^\s*#.*$\n?', re.MULTILINE)
else:
    regex = re.compile(r'^\s*# PORT.*$\n?', re.MULTILINE)

for filename in listdir('working'):
    if filename.endswith('.py'):
        filepath = 'working/' + filename
        # read input file
        text = open(filepath, 'r').read()
        # run the defined regular expression
        new_text = re.sub(regex, '', text)
        # write updated text
        open(filepath, 'w').write(new_text)
