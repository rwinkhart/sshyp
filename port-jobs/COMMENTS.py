#!/usr/bin/env python3
from os import listdir
from re import match as rematch
from sys import argv

# read arguments
arguments = argv[1:]

# loop through all Python files in the working directory
for filename in listdir('working'):
    if filename.endswith('.py'):
        filepath = 'working/' + filename
        # read input file
        with open(filepath, 'r') as file:
            new_file = []
            for line in file:
                # determine whether to remove all or only PORT comments
                if len(arguments) > 0 and arguments[0] == 'ALL':
                    if not rematch(r'^\s*#', line):
                        new_file.append(line)
                elif not rematch(r'^\s*# PORT', line):
                    new_file.append(line)
        # write the updated file contents
        open(filepath, 'w').writelines(new_file)
