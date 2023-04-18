#!/usr/bin/env python3
from os import listdir

# loop through all Python files in the working directory
for filename in listdir('working'):
    if filename.endswith('.py'):
        filepath = 'working/' + filename
        # read input file
        with open(filepath, 'r') as file:
            new_file = []
            for line in file:
                # remove blank lines
                if line != '\n':
                    new_file.append(line)
        # write the updated file contents
        open(filepath, 'w').writelines(new_file)
