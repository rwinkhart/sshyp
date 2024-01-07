#!/usr/bin/env python3
import re

targets = (('TWEAK-EXTEND-FUNCTIONS', 'stweak.py', '\n', '\n\n', ''),
           ('TWEAK-EXTEND-OPTION', 'stweak.py', '', '', "curses_radio(['okay'], "
            "'extension management is not supported on this platform\\\\n\\\\ninstead, you may install and manage "
            "extensions through your system package manager\\\\n\\\\nofficial extension packages are available "
            "at https://github.com/rwinkhart/sshyp-labs/releases')"))

for target in targets:
    # read text from target file
    text = open(f"working/{target[1]}", 'r').read()
    # compile regex and modify text
    regex = re.compile(f"{target[2]}# PORT START {target[0]}.*?# PORT END {target[0]}{target[3]}", re.DOTALL)
    new_text = re.sub(regex, target[4], text)
    # write updated text to target file
    open(f"working/{target[1]}", 'w').write(new_text)
