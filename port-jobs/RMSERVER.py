#!/usr/bin/env python3
import re

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
replacement = """_install_type = curses_radio(('client (ssh-synchronized)', 'client (offline)'),
                                 'device + sync type configuration')"""

## read input file
text = open('working/stweak.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}", re.DOTALL)
new_text = re.sub(regex, replacement, text)

# write updated text
open('working/stweak.py', 'w').write(new_text)

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
