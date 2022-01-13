#!/bin/bash
# This script packages sshyp (from source) for various Linux environments.

# NOTE It is recommended to instead use the latest officially packaged and tagged release.
# NOTE If using Arch, it is recommended to install from the AUR or from the PKGBUILD attatched to the latest official release.
# NOTE As of release fr4, sshync will become a separate package and thus a dependency for sshyp. sshync is automatically installed with the PKGBUILD version.

echo -e '\nOptions (please enter the number only):'
echo -e '\nDistribution Packages:\n\n1. Debian Linux\n2. Termux\n3. Generic (used for PKGBUILD/APKBUILD)'
echo -e '\nBuild Scripts:\n\n4. Alpine Linux (APKBUILD)\n5. Arch Linux (PKGBUILD)'
echo -e '\nOther:\n\n6. All (generates all distribution packages and build scripts)\n'
read -n 1 -r -p "Distribution: " distro

echo -e '\n\nThe value entered in this field will only affect the version reported to the package manager. The latest source is used regardless.\n'
read -r -p "Version number: " version

if [ "$distro" == "4" ] || [ "$distro" == "5" ] || [ "$distro" == "6" ]; then
    echo -e '\nThe value entered in this field will only affect the revision number for build scripts.\n'
    read -r -p "Revision number: " revision
fi

mkdir -p packages

if [ "$distro" == "2" ] || [ "$distro" == "6" ]; then
    echo -e '\nPackaging for Termux...\n'
    mkdir -p packages/termuxtemp/sshyp_"$version"-"$revision"_termux/{data,DEBIAN}
    mkdir -p packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/var
    mkdir -p packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/share/man/man1
    echo "Package: sshyp
Version: $version
Section: utils
Architecture: all
Maintainer: Randall Winkhart <idgr at tutanota dot com>
Description: A light-weight, self-hosted, synchronized password manager
Depends: python, gnupg, openssh, nano, termux-api, termux-am
" > packages/termuxtemp/sshyp_"$version"-"$revision"_termux/DEBIAN/control
    cp -r bin packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/
    cp -r share packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/
    touch packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/var/flag_termux
    cp extra/manpage packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    gzip packages/termuxtemp/sshyp_"$version"-"$revision"_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group packages/termuxtemp/sshyp_"$version"-"$revision"_termux/
    mv packages/termuxtemp/sshyp_"$version"-"$revision"_termux.deb packages/
    rm -rf packages/termuxtemp
    echo -e "\nTermux packaging complete.\n"
fi

if [ "$distro" == "3" ] || [ "$distro" == "6" ]; then
    echo -e '\nPackaging as generic...\n'
    mkdir -p packages/archtemp/var/lib/sshyp
    mkdir -p packages/archtemp/usr
    cp -r bin packages/archtemp/usr/
    cp -r share packages/archtemp/usr/
    mkdir -p packages/archtemp/usr/share/man/man1
    cp extra/manpage packages/archtemp/usr/share/man/man1/sshyp.1
    gzip packages/archtemp/usr/share/man/man1/sshyp.1
    tar -C packages/archtemp -cvf packages/sshyp-"$version".tar.xz usr/ var/
    rm -rf packages/archtemp
    echo -e '\nsha512 sum:'
    sha512sum packages/sshyp-"$version".tar.xz
    echo -e '\nsha256 sum:'
    sha256sum packages/sshyp-"$version".tar.xz
    echo -e "\nGeneric packaging complete.\n"
fi

if [ "$distro" == "5" ] || [ "$distro" == "6" ]; then
    echo -e '\nGenerating PKGBUILD...'
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

if [ "$distro" == "1" ] || [ "$distro" == "4" ]; then
    echo -e '\nThis packaging format is not yet supported, but will be in the near future!\n\nCurrently supported options are:\nTermux\nGeneric\nArch (PKGBUILD)\n'
fi
