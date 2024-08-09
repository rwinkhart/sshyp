#!/bin/sh
sed -i 's/[[:space:]]*$//' ./lib/* ./port-jobs/* ./package.sh
git commit -am "$1"
git push
