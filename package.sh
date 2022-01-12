#!/bin/bash
# This script packages sshyp (from source) for Arch Linux.
# In the future, it will also package for Alpine, Debian, Termux.
# NOTE It is recommended to instead use the latest officially packaged and tagged release.
# NOTE If using Arch, it is recommended to install from the AUR or from the PKGBUILD attatched to the latest official release.
# NOTE As of release fr4, sshync will become a separate package and thus a dependency for sshyp. sshync is automatically installed with the PKGBUILD version.

echo -e '\nOptions (please enter the number only):\n\n1. Alpine Linux\n2. Arch Linux (PKGBUILD)\n3. Debian Linux\n4. Termux\n5. Generic (used for PKGBUILD)\n6. All (will create all types of packages)\n'
read -n 1 -r -p "Distribution: " distro

echo -e '\nThe value entered in this field will only affect the version reported to the package manager. The latest source is used regardless.\n'
read -r -p "Version number: " version

read -r -p "Revision number: " revision

mkdir packages

if [ "$distro" == "2" ] || [ "$distro" == "6" ]; then
    echo -e '\nGenerating PKGBUILD...'
    mkdir -p sshyp_"$version"-"$revision"_termux/{data,DEBIAN}
    mkdir -p sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/var
    mkdir -p usr/share/man/man1
    echo '# Maintainer: Randall Winkhart <idgr at tutanota dot com>

        pkgname=sshyp
        pkgver='"$version"'
        pkgrel='"$revision"'
        pkgdesc='A light-weight, self-hosted, synchronized password manager'
        url='https://github.com/rwinkhart/sshyp'
        arch=('any')
        license=('GPL3')
        depends=( python gnupg openssh nano xclip wl-clipboard)

        source=("https://github.com/rwinkhart/sshyp/releases/download/v$pkgver/sshyp-$pkgver.tar.xz")
        sha512sums=('be6695cc231f4414322f2c4b919caf0759f4111e50259b3a6bbcb6e90a0ceba5d094c8766c287e5443c61adfdf414c1a93bc70e505dfd4bf34097c713b6e7d2f')

        package() {

            tar xf sshyp-"$pkgver".tar.xz -C "${pkgdir}"
            chown -R "$USER" ${pkgdir}/var/lib/sshyp

        }
        ' > packages/PKGBUILD
    echo -e "\nPKGBUILD generated.\n"
fi

if [ "$distro" == "4" ] || [ "$distro" == "6" ]; then
    echo -e '\nPackaging for Termux...'
    mkdir -p sshyp_"$version"-"$revision"_termux/{data,DEBIAN}
    mkdir -p sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/var
    mkdir -p usr/share/man/man1
    echo "Package: sshyp
        Version: $version
        Section: utils
        Architecture: all
        Maintainer: Randall Winkhart <idgr at tutanota dot com>
        Description: A light-weight, self-hosted, synchronized password manager
        Depends: python, gnupg, openssh, nano, termux-api, termux-am
        " > sshyp_"$version"-"$revision"_termux/DEBIAN/control
    cp -r bin sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/
    cp -r share sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/
    touch sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/var/flag_termux
    cp extra/manpage sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    gzip sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group sshyp_"$version"-"$revision"_termux/
    mv sshyp_"$version"-"$revision"_termux.deb packages/
    echo -e "\nTermux packaging complete.\n"
fi

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
    echo -e '\nsha256 sum:'
    sha256sum sshyp-"$version".tar.xz
    echo -e "\nGeneric packaging complete.\n"
fi
