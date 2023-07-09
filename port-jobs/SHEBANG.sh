#!/bin/sh
if [ "$1" = 'PREP' ]; then
    sed -i '1 s/.*/#!\/bin\/env\ python3.10/' ./*.py
else
    sed -i '1 s/.*/#!\/bin\/env\ python3.10/' ./working/sshyp.py
fi
