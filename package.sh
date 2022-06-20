#!/bin/bash

# This script packages sshyp (from source) for various UNIX(-like) environments.
# Dependencies (Arch Linux): dpkg (packaging for Debian/Termux), freebsd-pkg (packaging for FreeBSD)
# Dependencies (Fedora) (can only package for self): rpmdevtools
# NOTE It is recommended to instead use the latest officially packaged and tagged release.

echo -e '\nOptions (please enter the number only):'
echo -e '\nPackage Formats:\n\n1. Haiku\n2. Debian&Ubuntu Linux\n3. Fedora Linux\n4. FreeBSD\n5. Termux\n6. Generic (used for PKGBUILD/APKBUILD)'
echo -e '\nBuild Scripts:\n\n7. Arch Linux (PKGBUILD)'
echo -e '\nOther:\n\n8. All (generates all distribution packages (excluding Haiku and Fedora, as these must be packaged on their respective distributions) and build scripts)\n'
read -n 1 -r -p "Distribution: " distro

echo -e '\n\nThe value entered in this field will only affect the version reported to the package manager. The latest source is used regardless.\n'
read -r -p "Version number: " version

echo -e '\nThe value entered in this field will only affect the revision number for build scripts.\n'
read -r -p "Revision number: " revision

if [ "$distro" == "7" ] || [ "$distro" == "8" ]; then
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
    mkdir -p packages/haikutemp/documentation/{man/man1,packages/sshyp}
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

if [ "$distro" == "2" ] || [ "$distro" == "8" ]; then
    echo -e '\nPackaging for Debian...\n'
    mkdir -p packages/debiantemp/sshyp_"$version"-"$revision"_all/{DEBIAN,usr/share/man/man1}
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

if [ "$distro" == "5" ] || [ "$distro" == "8" ]; then
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

if [ "$distro" == "3" ] || [ "$distro" == "4" ] || [ "$distro" == "6" ] || [ "$distro" == "7" ] || [ "$distro" == "8" ]; then
    echo -e '\nPackaging as generic...\n'
    mkdir -p packages/archtemp/usr/share/man/man1
    cp -r bin packages/archtemp/usr/
    cp -r share packages/archtemp/usr/
    cp extra/manpage packages/archtemp/usr/share/man/man1/sshyp.1
    gzip packages/archtemp/usr/share/man/man1/sshyp.1
    tar -C packages/archtemp -cvf packages/sshyp-"$version".tar.xz usr/
    rm -rf packages/archtemp
    sha512="$(sha512sum packages/sshyp-"$version".tar.xz | awk '{print $1;}')"
    echo -e "\nsha512 sum:\n$sha512"
    echo -e "\nGeneric packaging complete.\n"
fi

if [ "$distro" == "3" ] || [ "$distro" == "8" ]; then
    echo -e '\nPackaging for Fedora...\n'
    rm -rf ~/rpmbuild
    rpmdev-setuptree
    cp packages/sshyp-"$version".tar.xz ~/rpmbuild/SOURCES
    echo "Name:           sshyp
Version:        "$version"
Release:        "$revision"
Summary:        A light-weight, self-hosted, synchronized password manager
BuildArch:      noarch

License:        GPL3
URL:            https://github.com/rwinkhart/sshyp
Source0:        sshyp-"$version".tar.xz

Requires:       python gnupg openssh nano wl-clipboard 

%description
sshyp is a password-store compatible CLI password manager available for UNIX(-like) systems - its primary goal is to make syncing passwords and notes across devices as easy as possible via CLI.

%install
tar xf %{_sourcedir}/sshyp-"$version".tar.xz -C %{_sourcedir}
cp -r %{_sourcedir}/usr %{buildroot}

%files
/usr/bin/sshyp
/usr/bin/sshync.py
/usr/bin/sshypRemote.py
%license /usr/share/licenses/sshyp/license
%doc /usr/share/doc/sshyp/changelog
%doc /usr/share/man/man1/sshyp.1.gz
" > ~/rpmbuild/SPECS/sshyp.spec
rpmbuild -bb ~/rpmbuild/SPECS/sshyp.spec
mv ~/rpmbuild/RPMS/noarch/* packages/
rm -rf ~/rpmbuild
echo -e "\nFedora packaging complete.\n"
fi

if [ "$distro" == "4" ] || [ "$distro" == "8" ]; then
    echo -e '\nPackaging for FreeBSD...\n'
    mkdir -p packages/FreeBSDtemp/bin
    tar xf packages/sshyp-"$version".tar.xz -C packages/FreeBSDtemp
    ln -s /usr/local/bin/python3 packages/FreeBSDtemp/bin/python3
    echo "name: sshyp
version: \""$version"\"
abi = \"FreeBSD:13:*\";
arch = \"freebsd:13:*\";
origin: security/sshyp
comment: \"a password manager\"
desc: \"a light-weight, self-hosted, synchronized password manager\"
maintainer: <idgr at tutanota dot com>
www: https://github.com/rwinkhart/sshyp
prefix: /
\"deps\" : {
                   \"python\" : {
                      \"origin\" : \"lang/python\"
                   },
                   \"gnupg\" : {
                      \"origin\" : \"security/gnupg\"
                   },
                   \"nano\" : {
                      \"origin\" : \"editors/nano\"
                   },
                   \"xclip\" : {
                      \"origin\" : \"x11/xclip\"
                   },
                   \"wl-clipboard\" : {
                      \"origin\" : \"x11/wl-clipboard\"
                   },
                },
" > packages/FreeBSDtemp/+MANIFEST
echo "/bin/python3
/usr/bin/sshync.py
/usr/bin/sshyp
/usr/bin/sshypRemote.py
/usr/share/doc/sshyp/changelog
/usr/share/licenses/sshyp/license
/usr/share/man/man1/sshyp.1.gz
" > packages/FreeBSDtemp/plist
pkg create -m packages/FreeBSDtemp/ -r packages/FreeBSDtemp/ -p packages/FreeBSDtemp/plist -o packages/
rm -rf packages/FreeBSDtemp
echo -e "\nFreeBSD packaging complete.\n"
fi

if [ "$distro" == "7" ] || [ "$distro" == "8" ]; then
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
