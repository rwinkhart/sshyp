#!/bin/bash
# This script packages sshyp (from source) for Arch Linux.
# In the future, it will also package for Alpine, Debian, Termux.
# NOTE It is recommended to instead use the latest officially packaged and tagged release.
# NOTE If using Arch, it is recommended to install from the AUR or from the PKGBUILD attatched to the latest official release.
# NOTE As of release fr3, sshync will become a separate package and thus a dependency for sshyp.

#echo -e '\nOptions (please enter the number only):\n\n1. Alpine Linux\n2. Arch Linux\n3. Debian Linux\n4. Termux (Android)\n5. Generic (used for AUR version)\n6. All (will create all types of packages)\n'
#read -n 1 -r -p "Distribution: " distro
distro=5  # TODO remove when other distros are supported

echo -e '\nThe value entered in this field will only affect the version reported to the package manager. The latest source is used regardless.\n'
read -r -p "Version number: " version

if [ "$distro" == "5" ] || [ "$distro" == "6" ]; then
    echo -e '\nPackaging as generic...'
    mkdir -p var/lib/sshyp
    mkdir -p usr
    cp -r bin usr/
    cp -r share usr/
    mkdir -p usr/share/man/man1
    cp extra/manpage usr/share/man/man1/sshyp.1
    gzip usr/share/man/man1/sshyp.1
    tar -cf sshyp-"$version".tar.xz usr/ var/
    rm -rf usr/ var/
    echo -e '\nsha512 sum:'
    sha512sum sshyp-"$version".tar.xz
    echo -e "\nPackaging complete.\n"
fi
