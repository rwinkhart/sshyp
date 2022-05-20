#!/bin/bash

# This script packages sshyp (from source) for various UNIX environments.

# NOTE It is recommended to instead use the latest officially packaged and tagged release.
# NOTE If using Arch, it is recommended to install from the AUR or from the PKGBUILD attatched to the latest official release.

echo -e '\nOptions (please enter the number only):'
echo -e '\nDistribution Packages:\n\n1. Haiku\n2. Debian\n3. Termux\n4. Generic (used for PKGBUILD/APKBUILD)'
echo -e '\nBuild Scripts:\n\n5. Alpine Linux (APKBUILD)\n6. Arch Linux (PKGBUILD, also builds local generic package)'
echo -e '\nOther:\n\n7. All (generates all distribution packages (excluding Haiku, as this must be done on Haiku) and build scripts)\n'
read -n 1 -r -p "Distribution: " distro

echo -e '\n\nThe value entered in this field will only affect the version reported to the package manager. The latest source is used regardless.\n'
read -r -p "Version number: " version

echo -e '\nThe value entered in this field will only affect the revision number for build scripts.\n'
read -r -p "Revision number: " revision

if [ "$distro" == "5" ] || [ "$distro" == "6" ] || [ "$distro" == "7" ]; then
    echo -e '\nOptions (please enter the number only):'
    echo -e '\n1. GitHub Release Tag\n2. Local\n'
    read -r -p "Source (for build scripts): " source

    if [ "$source" == "1" ]; then
        source='https://github.com/rwinkhart/sshyp/releases/download/v$pkgver/sshyp-$pkgver.tar.xz'
    else
        source=local://sshyp-"$version".tar.xz
    fi
fi

mkdir -p packages

if [ "$distro" == "1" ]; then
    echo -e '\nPackaging for Haiku...\n'
    mkdir -p packages/haikutemp/documentation/man/man1
    mkdir -p packages/haikutemp/documentation/packages/sshyp
    echo "name			sshyp
version			"$version"-"$revision"
architecture		any
summary			\"A light-weight, self-hosted, synchronized password manager\"
description		\"sshyp is the only password-store compatible CLI password manager available for Haiku - it is also available on Linux/Android (via Termux) so that you can sync your entries across all of your devices.\"
packager		\"Randall Winkhart <idgr at tutanota dot com>\"
vendor			\"Randall Winkhart\"
licenses {
	\"GNU GPL v3\"
}
copyrights {
	\"2021-2022 Randall Winkhart\"
}
provides {
	sshyp = "$version"
	cmd:sshyp
}
requires {
	gnupg
	openssh
	python3
	nano
}
urls {
	\"https://github.com/rwinkhart/sshyp\"
}
" > packages/haikutemp/.PackageInfo
    cp -r bin packages/haikutemp/
    cp -r share/doc/sshyp/ packages/haikutemp/documentation/packages/
    cp -r share/licenses/sshyp/ packages/haikutemp/documentation/packages/
    cp extra/manpage packages/haikutemp/documentation/man/man1/sshyp.1
    gzip packages/haikutemp/documentation/man/man1/sshyp.1
    cd packages/haikutemp
    package create -b sshyp-"$version"-"$revision"_all.hpkg
    package add sshyp-"$version"-"$revision"_all.hpkg bin documentation
    cd ../..
    mv packages/haikutemp/sshyp-"$version"-"$revision"_all.hpkg packages/
    rm -rf packages/haikutemp
    echo -e "\nHaiku packaging complete.\n"
fi

if [ "$distro" == "2" ] || [ "$distro" == "7" ]; then
    echo -e '\nPackaging for Debian...\n'
    mkdir -p packages/debiantemp/sshyp_"$version"-"$revision"_all/{DEBIAN,usr}
    mkdir -p packages/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1
    echo "Package: sshyp
Version: $version
Section: utils
Architecture: all
Maintainer: Randall Winkhart <idgr at tutanota dot com>
Description: A light-weight, self-hosted, synchronized password manager
Depends: python3, gnupg, openssh-client, nano, xclip, wl-clipboard
Priority: optional
Installed-Size: 35
" > packages/debiantemp/sshyp_"$version"-"$revision"_all/DEBIAN/control
    cp -r bin packages/debiantemp/sshyp_"$version"-"$revision"_all/usr/
    cp -r share packages/debiantemp/sshyp_"$version"-"$revision"_all/usr/
    cp extra/manpage packages/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1/sshyp.1
    gzip packages/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group packages/debiantemp/sshyp_"$version"-"$revision"_all/
    mv packages/debiantemp/sshyp_"$version"-"$revision"_all.deb packages/
    rm -rf packages/debiantemp
    echo -e "\nDebian packaging complete.\n"
fi

if [ "$distro" == "3" ] || [ "$distro" == "7" ]; then
    echo -e '\nPackaging for Termux...\n'
    mkdir -p packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/{data,DEBIAN}
    mkdir -p packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1
    echo "Package: sshyp
Version: $version
Section: utils
Architecture: all
Maintainer: Randall Winkhart <idgr at tutanota dot com>
Description: A light-weight, self-hosted, synchronized password manager
Depends: python, gnupg, openssh, nano, termux-api, termux-am
Priority: optional
Installed-Size: 35
" > packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/DEBIAN/control
    cp -r bin packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/
    cp -r share packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/
    cp extra/manpage packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    gzip packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux/
    mv packages/termuxtemp/sshyp_"$version"-"$revision"_all_termux.deb packages/
    rm -rf packages/termuxtemp
    echo -e "\nTermux packaging complete.\n"
fi

if [ "$distro" == "4" ] || [ "$distro" == "6" ] || [ "$distro" == "7" ]; then
    echo -e '\nPackaging as generic...\n'
    mkdir -p packages/archtemp/usr
    cp -r bin packages/archtemp/usr/
    cp -r share packages/archtemp/usr/
    mkdir -p packages/archtemp/usr/share/man/man1
    cp extra/manpage packages/archtemp/usr/share/man/man1/sshyp.1
    gzip packages/archtemp/usr/share/man/man1/sshyp.1
    tar -C packages/archtemp -cvf packages/sshyp-"$version".tar.xz usr/
    rm -rf packages/archtemp
    sha512="$(sha512sum packages/sshyp-"$version".tar.xz | awk '{print $1;}')"
    echo -e "\nsha512 sum:\n$sha512"
    echo -e "\nGeneric packaging complete.\n"
fi

if [ "$distro" == "6" ] || [ "$distro" == "7" ]; then
    echo -e '\nGenerating PKGBUILD...'
    echo "# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=sshyp
pkgver="$version"
pkgrel="$revision"
pkgdesc='A light-weight, self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('any')
license=('GPL3')
depends=(python gnupg openssh nano xclip wl-clipboard)

source=(\""$source"\")
sha512sums=('"$sha512"')

package() {

    tar xf sshyp-"\"\$pkgver\"".tar.xz -C "\"\${pkgdir}\""

}
" > packages/PKGBUILD
    echo -e "\nPKGBUILD generated.\n"
fi

if [ "$distro" == "4" ]; then
    echo -e '\nThis packaging format is not yet supported, but will be in the near future!\n'
fi
