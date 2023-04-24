#!/bin/sh
if [ "$1" = 'TABS' ]; then
    unexpand -t 3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63,67,71,75,79,83,87,91,95,99,103,107,111,115,119,123 working/sshyp.py > working/sshyp.py.new
    unexpand -t 3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63,67,71,75,79,83,87,91,95,99,103,107,111,115,119,123 working/sshync.py > working/sshync.py.new
    mv working/sshyp.py.new working/sshyp.py
    mv working/sshync.py.new working/sshync.py
    chmod +x working/sshyp.py working/sshync.py
elif [ "$(grep -qP '\t' "$1" && echo TABS)" = 'TABS' ]; then
    printf "$1 contains tab characters...\n"
    read -rp 'replace with (4) spaces? (Y/n) ' replace
    if [ "$replace" != 'n' ] && [ "$replace" != 'N' ]; then
        expand -t 3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63,67,71,75,79,83,87,91,95,99,103,107,111,115,119,123 "$1" > "$1".new
        chmod --reference="$1" "$1".new
        mv "$1".new "$1"
    fi
fi
