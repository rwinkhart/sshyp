#!/bin/sh
if [ "$1" = 'TABS' ]; then
    unexpand -t 4 working/sshyp.py > working/sshyp.py.new
    unexpand -t 4 working/sshync.py > working/sshync.py.new
else
    expand -t 4 working/sshyp.py > working/sshyp.py.new
    expand -t 4 working/sshync.py > working/sshync.py.new
fi
mv working/sshyp.py.new working/sshyp.py
mv working/sshync.py.new working/sshync.py
chmod +x working/sshyp.py working/sshync.py
