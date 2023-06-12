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
        replacement = 'symlink("/data/data/com.termux/files/usr/tmp", f"{home}/.config/sshyp/tmp")\n'
    elif arguments[0] == 'LINUX':
        replacement = 'symlink("/dev/shm", f"{home}/.config/sshyp/tmp")'
else:
    s_exit()

targets = (('UNAME-IMPORT-SSHYP', 'sshyp.py', ''), ('UNAME-IMPORT-STWEAK', 'stweak.py', ''),
           ('UNAME-TMP', 'stweak.py', replacement))

for target in targets:
    # read text from target file
    text, special = open(f"working/{target[1]}", 'r').read(), ''
    # determine text to end regex with
    if target[2] == '':
        regend = '\n'
    # compile regex and modify text
    regex = re.compile(f"# PORT START {target[0]}.*?# PORT END {target[0]}{regend}", re.DOTALL)
    new_text = re.sub(regex, target[2], text)
    # write updated text to target file
    open(f"working/{target[1]}", 'w').write(new_text)
