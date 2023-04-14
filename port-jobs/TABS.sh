#!/bin/sh
if [ "$1" = 'TABS' ]; then
    unexpand -t 4 working/sshyp.py > working/sshyp.py.new
    unexpand -t 4 working/sshync.py > working/sshync.py.new
    mv working/sshyp.py.new working/sshyp.py
    mv working/sshync.py.new working/sshync.py
    chmod +x working/sshyp.py working/sshync.py
elif [ "$(grep -qP '\t' "$1" && echo TABS)" = 'TABS' ]; then
    printf "$1 contains tab characters...\n"
    read -rp 'replace with (4) spaces? (Y/n) ' replace
    if [ "$replace" != 'n' ] && [ "$replace" != 'N' ]; then
        expand -t 4 "$1" > "$1".new
        chmod --reference="$1" "$1".new
        mv "$1".new "$1"
    fi
fi
