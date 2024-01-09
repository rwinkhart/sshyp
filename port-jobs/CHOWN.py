#!/usr/bin/env python3
import re
from sys import argv

# read arguments
arguments = argv[1:]

# define PORT target
string1 = '# PORT START TWEAK-EXT-CHOWN'
string2 = '# PORT END TWEAK-EXT-CHOWN'

# define replacement text depending on arguments
if len(arguments) > 0 and arguments[0] == 'BSD':
    replacement = "run((_escalator, 'chown', 'root:wheel', _exe_dir, _ini_dir))"
else:
    replacement = "run((_escalator, 'chown', 'root:root', _exe_dir, _ini_dir))"

# read input file
text = open('working/stweak.py', 'r').read()

# compile regex and modify text
regex = re.compile(f"{string1}.*?{string2}", re.DOTALL)

# find and replace the defined PORT target
new_text = re.sub(regex, replacement, text)

# write updated text
open('working/stweak.py', 'w').write(new_text)
