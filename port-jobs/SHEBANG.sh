#!/bin/sh
if [ "$1" = 'HAIKU' ]; then
    sed -i '1 s/.*/#!\/bin\/env\ python3.10/' ./working/sshync.py
    sed -i '1 s/.*/#!\/bin\/env\ python3.10/' ./working/sshyp.py
fi
