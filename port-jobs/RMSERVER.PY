#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# SSHYNC-REMOTE
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

# WHITELIST-SERVER
# define PORT target
string1 = '# PORT START WHITELIST-SERVER'
string2 = '# PORT END WHITELIST-SERVER'

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"\n{string1}.*?{string2}\n\n", re.DOTALL)
new_text = re.sub(regex, '', text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)

# TWEAK-DEVTYPE
# define PORT target
string1 = '# PORT START TWEAK-DEVTYPE'
string2 = '# PORT END TWEAK-DEVTYPE'

# set replacement text
replacement = """if True:
        _sshyp_data = ['client']
        Path(f"{home}/.local/share/sshyp").mkdir(mode=0o700, parents=True, exist_ok=True)"""

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}", re.DOTALL)
new_text = re.sub(regex, replacement, text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)

# ARGS-SERVER
# define PORT target
string1 = '# PORT START ARGS-SERVER'
string2 = '# PORT END ARGS-SERVER'

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}\n\n        ", re.DOTALL)
new_text = re.sub(regex, '', text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)

# HELP-SERVER
# define PORT target
string1 = '# PORT START HELP-SERVER'
string2 = '# PORT END HELP-SERVER'

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}\n", re.DOTALL)
new_text = re.sub(regex, '', text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)
