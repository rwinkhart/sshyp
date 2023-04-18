#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# define PORT target
string1 = '# PORT START SSHYNC-REMOTE'
string2 = '# PORT END SSHYNC-REMOTE'

# read input file
text = open('working/sshync.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"\n{string1}.*?{string2}\n\n", re.DOTALL)
new_text = re.sub(regex, '', text)

# write updated text
open('working/sshync.py', 'w').write(new_text)
