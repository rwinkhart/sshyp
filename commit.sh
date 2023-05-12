#!/bin/sh
git add -f extra lib/sshyp.py lib/sshync.py lib/stweak.py port-jobs share LICENSE README.md package.sh commit.sh .gitignore
git commit -m "$1"
git push
