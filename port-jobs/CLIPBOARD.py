#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# read arguments
arguments, replacement = argv[1:], None

# define replacement text depending on arguments
if len(arguments) > 0:
    if arguments[0] == 'WSL':
        replacement = """run(('powershell.exe', '-c', "Set-Clipboard '" + _copy_subject.replace("'", "''") + "'"))
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'wsl'), stdout=DEVNULL, stderr=DEVNULL)"""
    elif arguments[0] == 'MAC':
        replacement = """run('pbcopy', stdin=Popen(('printf', '%b', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')), stdout=PIPE).stdout)
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'mac'))"""
    elif arguments[0] == 'HAIKU':
        replacement = """run(('clipboard', '-c', _copy_subject))
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'haiku'))"""
    elif arguments[0] == 'TERMUX':
        replacement = """run(('termux-clipboard-set', _copy_subject))
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'termux'))"""
    elif arguments[0] in ('LINUX', 'BSD'):
        replacement = """if 'WAYLAND_DISPLAY' in environ:
        run('wl-copy', stdin=Popen(('printf', '%b', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')), stdout=PIPE).stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'wayland'))
    else:
        run(('xclip', '-sel', 'c'), stdin=Popen(('printf', '%b', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')), stdout=PIPE).stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'x11'))"""
else:
    s_exit()

# define PORT target
string1 = '# PORT START CLIPBOARD'
string2 = '# PORT END CLIPBOARD'

# read input file
text = open('working/sshyp.py', 'r').read()

# find and replace the defined PORT target
regex = re.compile(f"{string1}.*?{string2}", re.DOTALL)
new_text = re.sub(regex, replacement, text)

# write updated text
open('working/sshyp.py', 'w').write(new_text)
