#!/bin/sh
if [ "$1" = 'PREP' ]; then
    sed -i '1 s/.*/#!\/bin\/env\ python3.11/' ./*.py
else
    sed -i '1 s/.*/#!\/bin\/env\ python3.11/' ./working/sshyp.py ./working/clipclear.py
fi
