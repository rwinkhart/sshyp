#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# read arguments
arguments = argv[1:]

# define PORT target
string1 = '# PORT START CLIPTOOL'
string2 = '# PORT END CLIPTOOL'

# define replacement text depending on arguments
if len(arguments) > 0:
    regex = re.compile(f"{string1}.*?{string2}", re.DOTALL)
    replacement = """# check for clipboard tool and display warning if missing
    if 'WAYLAND_DISPLAY' in environ:
        _display_server, _clipboard_tool, _clipboard_package = 'Wayland', 'wl-copy', 'wl-clipboard'
    else:
        _display_server, _clipboard_tool, _clipboard_package = 'X11', 'xclip', 'xclip'
    from shutil import which
    if which(_clipboard_tool) is None:
        print(f'''\u001b[38;5;9mwarning: you are using {_display_server} and "{_clipboard_tool}" is not present -
copying entry fields will not function until "{_clipboard_package}" is installed\u001b[0m
        ''')"""
else:
    regex = re.compile(f"{string1}.*?{string2}\n\n", re.DOTALL)
    replacement = ''

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
new_text = re.sub(regex, replacement, text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)
