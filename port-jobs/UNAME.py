#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# read arguments
arguments = argv[1:]

# define replacement text depending on arguments
if len(arguments) > 0:
    if arguments[0] == 'TMP':
        replacement = 'symlink("/tmp", f"{home}/.config/sshyp/tmp")'
    elif arguments[0] == 'TERMUX':
        replacement = 'symlink("/data/data/com.termux/files/usr/tmp", f"{home}/.config/sshyp/tmp")'
    elif arguments[0] == 'LINUX':
        replacement = 'symlink("/dev/shm", f"{home}/.config/sshyp/tmp")'
else:
    s_exit()

# UNAME-IMPORT
# define PORT target
string1 = '# PORT START UNAME-IMPORT'
string2 = '# PORT END UNAME-IMPORT'

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}\n", re.DOTALL)
new_text = re.sub(regex, '', text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)

# UNAME-TMP
# define PORT target
string1 = '# PORT START UNAME-TMP'
string2 = '# PORT END UNAME-TMP'

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}", re.DOTALL)
new_text = re.sub(regex, replacement, text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)
