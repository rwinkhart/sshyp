#!/usr/bin/env python3
import re

devtype_replacement = """_install_type = curses_radio(('client (ssh-synchronized)', 'client (offline)'),
                                 'device + sync type configuration')"""

targets = (('SSHYNC-REMOTE', 'sshync.py', '\n', '\n\n', ''), ('WHITELIST-SERVER', 'stweak.py', '\n', '\n\n', ''),
           ('TWEAK-DEVTYPE', 'stweak.py', '', '', devtype_replacement),
           ('ARGS-SERVER', 'sshyp.py', '', '\n\n        ', ''), ('HELP-SERVER', 'sshyp.py', '', '\n', ''))

for target in targets:
    # read text from target file
    text = open(f"working/{target[1]}", 'r').read()
    # compile regex and modify text
    regex = re.compile(f"{target[2]}# PORT START {target[0]}.*?# PORT END {target[0]}{target[3]}", re.DOTALL)
    new_text = re.sub(regex, target[4], text)
    # write updated text to target file
    open(f"working/{target[1]}", 'w').write(new_text)
