#!/bin/sh
sed -i 's/[[:space:]]*$//' ./lib/* ./port-jobs/* ./package.sh
git add -f .github extra lib/sshyp.py lib/sshync.py lib/stweak.py lib/clipclear.py port-jobs share LICENSE README.md package.sh commit.sh .gitignore
git commit -m "$1"
git push
