#!/usr/bin/env python3
from hashlib import sha512
from subprocess import PIPE, run
from sys import argv
from time import sleep

# set period of time to wait before attempting to clear clipboard
sleep(30)
# enable the storing of clipboard contents hash for later comparison
_hash_paste = sha512()

# PORT START CLIPCLEAR
if argv[2] == 'wsl':
    _hash_paste.update(run(('powershell.exe', '-c', 'Get-Clipboard'), stdout=PIPE).stdout.strip())
    if argv[1] == _hash_paste.hexdigest():
        run(('powershell.exe', '-c', 'Set-Clipboard'))

elif argv[2] == 'wayland':
    _hash_paste.update(run('wl-paste', stdout=PIPE).stdout.strip())
    if argv[1] == _hash_paste.hexdigest():
        run(('wl-copy', '-c'))

elif argv[2] == 'haiku':
    _hash_paste.update(run(('clipboard', '-p'), stdout=PIPE).stdout.strip())
    if argv[1] == _hash_paste.hexdigest():
        run(('clipboard', '-r'))

elif argv[2] == 'mac':
    _hash_paste.update(run(('pbpaste'), stdout=PIPE).stdout.strip())
    if argv[1] == _hash_paste.hexdigest():
        run('pbcopy', input=b'')

elif argv[2] == 'termux':
    _hash_paste.update(run(('termux-clipboard-get'), stdout=PIPE).stdout.strip())
    if argv[1] == _hash_paste.hexdigest():
        run(("termux-clipboard-set", "''"))

elif argv[2] == 'x11':
    _hash_paste.update(run(('xclip', '-o', '-sel', 'c'), stdout=PIPE).stdout.strip())
    if argv[1] == _hash_paste.hexdigest():
        run(('xclip', '-i', '/dev/null', '-sel', 'c'))
# PORT END CLIPCLEAR
