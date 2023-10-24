#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# read arguments
arguments, clip_replacement, clear_replacement = argv[1:], None, None

# define replacement text depending on arguments
if len(arguments) > 0:
    if arguments[0] == 'WSL':
        clip_replacement = """run(('powershell.exe', '-c', "Set-Clipboard '" + _copy_subject.replace("'", "''") + "'"))
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'wsl'), stdout=DEVNULL, stderr=DEVNULL)"""
        clear_replacement = """hash_paste.update(run(('powershell.exe', '-c', 'Get-Clipboard'), stdout=PIPE).stdout.strip())
if argv[1] == hash_paste.hexdigest():
    run(('powershell.exe', '-c', 'Set-Clipboard'))"""
    elif arguments[0] == 'MAC':
        clip_replacement = """run('pbcopy', stdin=Popen(('printf', '%b', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')), stdout=PIPE).stdout)
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'mac'))"""
        clear_replacement = """hash_paste.update(run('pbpaste', stdout=PIPE).stdout.strip())
if argv[1] == hash_paste.hexdigest():
    run('pbcopy', input=b'')"""
    elif arguments[0] == 'HAIKU':
        clip_replacement = """run(('clipboard', '-c', _copy_subject))
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'haiku'))"""
        clear_replacement = """hash_paste.update(run(('clipboard', '-p'), stdout=PIPE).stdout.strip())
if argv[1] == hash_paste.hexdigest():
    run(('clipboard', '-r'))"""
    elif arguments[0] == 'TERMUX':
        clip_replacement = """run(('termux-clipboard-set', _copy_subject))
    Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'termux'))"""
        clear_replacement = """hash_paste.update(run('termux-clipboard-get', stdout=PIPE).stdout.strip())
if argv[1] == hash_paste.hexdigest():
    run(("termux-clipboard-set", "''"))"""
    elif arguments[0] in ('LINUX', 'BSD'):
        clip_replacement = """if 'WAYLAND_DISPLAY' in environ:
        run('wl-copy', stdin=Popen(('printf', '%b', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')), stdout=PIPE).stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'wayland'))
    else:
        run(('xclip', '-sel', 'c'), stdin=Popen(('printf', '%b', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')), stdout=PIPE).stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'x11'))"""
        clear_replacement = """if argv[2] == 'wayland':
    hash_paste.update(run('wl-paste', stdout=PIPE).stdout.strip())
    if argv[1] == hash_paste.hexdigest():
        run(('wl-copy', '-c'))
else:
    hash_paste.update(run(('xclip', '-o', '-sel', 'c'), stdout=PIPE).stdout.strip())
    if argv[1] == hash_paste.hexdigest():
        run(('xclip', '-i', '/dev/null', '-sel', 'c'))"""
else:
    s_exit()

targets = (('CLIPBOARD', 'sshyp.py', '', '', clip_replacement),
           ('CLIPCLEAR', 'clipclear.py', '\n', '', clear_replacement))

for target in targets:
    # read text from target file
    text = open(f"working/{target[1]}", 'r').read()
    # compile regex and modify text
    regex = re.compile(f"{target[2]}# PORT START {target[0]}.*?# PORT END {target[0]}{target[3]}", re.DOTALL)
    new_text = re.sub(regex, target[4], text)
    # write updated text to target file
    open(f"working/{target[1]}", 'w').write(new_text)
