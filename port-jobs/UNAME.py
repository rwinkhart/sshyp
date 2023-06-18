#!/usr/bin/env python3
import re

targets = (('UNAME-IMPORT-SSHYP', 'sshyp.py', ''), ('UNAME-IMPORT-STWEAK', 'stweak.py', ''))

for target in targets:
    # read text from target file
    text, special = open(f"working/{target[1]}", 'r').read(), ''
    # compile regex and modify text
    regex = re.compile(f"# PORT START {target[0]}.*?# PORT END {target[0]}\n", re.DOTALL)
    new_text = re.sub(regex, target[2], text)
    # write updated text to target file
    open(f"working/{target[1]}", 'w').write(new_text)
