#!/usr/bin/env python3
import re
from sys import argv, exit as s_exit

# read arguments
arguments, replacement = argv[1:], None

# define replacement text depending on arguments
if len(arguments) > 0:
    if arguments[0] == 'WSL':
        replacement = """run(('powershell.exe', '-c', "Set-Clipboard '" + _copy_subject.replace("'", "''") + "'"))
    Popen("sleep 30; temp=$(echo \\"$(powershell.exe -Command \\'Get-FileHash -InputStream $([IO.MemoryStream]"
          "::new([byte[]][char[]]\\"$(Get-Clipboard)\\")) -Algorithm SHA512 | Select-Object -ExpandProperty "
          f"Hash\\')\\" | dos2unix); test \\'{_hash.hexdigest().upper()}\\' = \\"$temp\\" && powershell.exe -c "
          "Set-Clipboard", shell=True, stdout=DEVNULL, stderr=DEVNULL)"""
    elif arguments[0] == 'MAC':
        replacement = """run('pbcopy', stdin=Popen(('printf', _copy_subject.replace('\\\\\\', '\\\\\\\\\\\\\\')
        .replace('%', '%%')), stdout=PIPE).stdout)
    Popen("sleep 30; printf '' | pbcopy", shell=True)"""
    elif arguments[0] == 'HAIKU':
        replacement = """run(('clipboard', '-c', _copy_subject))
    Popen('sleep 30; clipboard -r', shell=True)"""
    elif arguments[0] == 'TERMUX':
        replacement = """run(('termux-clipboard-set', _copy_subject))
    Popen("sleep 30; termux-clipboard-set ''", shell=True)"""
    elif arguments[0] == 'LINUX':
        replacement = """if 'WAYLAND_DISPLAY' in environ:
        run('wl-copy', stdin=Popen(('printf', _copy_subject
        .replace('\\\\\\', '\\\\\\\\\\\\\\').replace('%', '%%')), stdout=PIPE).stdout)
        Popen(f"sleep 30; test \\'{_hash.hexdigest() + 2*' ' + '-'}\\' = \\"$(printf \\"$(wl-paste)\\" | sha512sum)\\" "
               "&& wl-copy -c", shell=True)
    else:
        run(('xclip', '-sel', 'c'), stdin=Popen(('printf', _copy_subject
        .replace('\\\\\\', '\\\\\\\\\\\\\\').replace('%', '%%')), stdout=PIPE).stdout)
        Popen("sleep 30; printf '' | xclip -sel c", shell=True)"""
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
