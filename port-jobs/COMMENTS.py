#!/usr/bin/env python3
import re
from sys import argv

# read arguments
arguments = argv[1:]

# define regular expression depending on arguments
if arguments[0] == 'ALL':
    regex = re.compile(r'^\s*#.*$\n?', re.MULTILINE)
else:
    regex = re.compile(r'^\s*# PORT.*$\n?', re.MULTILINE)

# read input file
text = open("working/sshyp.py", "r").read()

# run the defined regular expression
new_text = re.sub(regex, '', text)

# write the updated text
open("working/sshyp.py", "w").write(new_text)
