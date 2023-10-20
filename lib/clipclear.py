#!/usr/bin/env python3
from hashlib import sha512
from subprocess import PIPE, run
from sys import argv
from time import sleep

# set period of time to wait before attempting to clear clipboard
sleep(30)

# store a hash of the current clipboard contents for later comparison
_hash_paste = sha512()
_hash_paste.update(run('wl-paste', stdout=PIPE).stdout.strip())

# if the supplied hash matches the hash of the current clipboard contents, clear the clipboard
if argv[1] == _hash_paste.hexdigest():
    if argv[2] == 'wsl':
        run(('powershell.exe', '-c', 'Set-Clipboard'))
    elif argv[2] == 'wayland':
        run(('wl-copy', '-c'))
    elif argv[2] == 'haiku':
        run(('clipboard', '-r'))
    elif argv[2] == 'mac':
        run('pbcopy', input=b'')
    elif argv[2] == 'termux':
        run(("termux-clipboard-set", "''"))
    elif argv[2] == 'x11':
        run(('xclip', '-i', '/dev/null', '-sel', 'c'))
