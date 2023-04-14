#!/bin/sh

version=$(sed -n '1{p;q}' share/doc/sshyp/changelog | cut -c8-)
if [ -z "$2" ]; then
    revision=1
else
    revision="$2"
fi

_create_generic_all() {
    printf '\npackaging as generic (multi-platform/archival, no port jobs)...\n'
    mkdir -p output/generictemp/usr/bin \
         output/generictemp/usr/lib/sshyp/extensions \
         output/generictemp/usr/share/man/man1 \
         output/generictemp/usr/share/bash-completion/completions \
         output/generictemp/usr/share/zsh/functions/Completion/Unix
    cp -r lib/. output/generictemp/usr/lib/sshyp/
    ln -s /usr/lib/sshyp/sshyp.py output/generictemp/usr/bin/sshyp
    cp -r share output/generictemp/usr/
    cp extra/completion.bash output/generictemp/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/generictemp/usr/share/zsh/functions/Completion/Unix/_sshyp
    cp extra/manpage output/generictemp/usr/share/man/man1/sshyp.1
    gzip output/generictemp/usr/share/man/man1/sshyp.1
    XZ_OPT=-e6 tar -C output/generictemp -cvJf output/GENERIC-ALL-sshyp-"$version".tar.xz usr/
    rm -rf output/generictemp
    printf '\ngeneric (multi-platform/archival, no port jobs) packaging complete\n\n'
} &&

_create_generic_linux() {
    printf '\npackaging as generic (Linux)...\n'
    mkdir -p output/linuxtemp/usr/bin \
         output/linuxtemp/usr/lib/sshyp/extensions \
         output/linuxtemp/usr/share/man/man1 \
         output/linuxtemp/usr/share/bash-completion/completions \
         output/linuxtemp/usr/share/zsh/functions/Completion/Unix
    # START PORT
	cp -r lib/. port-jobs/working/
	cd port-jobs
	./CLIPBOARD.py LINUX
	./COMMENTS.py ALL
	./TABS.sh TABS
	cd ..
    cp -r port-jobs/working/. output/linuxtemp/usr/lib/sshyp/
    # END PORT
    ln -s /usr/lib/sshyp/sshyp.py output/linuxtemp/usr/bin/sshyp
    cp -r share output/linuxtemp/usr/
    cp extra/completion.bash output/linuxtemp/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/linuxtemp/usr/share/zsh/functions/Completion/Unix/_sshyp
    cp extra/manpage output/linuxtemp/usr/share/man/man1/sshyp.1
    gzip output/linuxtemp/usr/share/man/man1/sshyp.1
    XZ_OPT=-e6 tar -C output/linuxtemp -cvJf output/GENERIC-LINUX-sshyp-"$version".tar.xz usr/
    rm -rf output/linuxtemp
    sha512="$(sha512sum output/GENERIC-LINUX-sshyp-"$version".tar.xz | awk '{print $1;}')"
    printf '\ngeneric (Linux) packaging complete\n\n'
} &&

_create_pkgbuild() {
    printf '\ngenerating PKGBUILD...\n'
    local source='https://github.com/rwinkhart/sshyp/releases/download/v$pkgver/GENERIC-LINUX-sshyp-$pkgver.tar.xz'
    printf "# Maintainer: Randall Winkhart <idgr at tutanota dot com>
pkgname=sshyp
pkgver="$version"
pkgrel="$revision"
pkgdesc='A light-weight, self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('any')
license=('GPL-3.0-only')
depends=(python gnupg openssh xclip wl-clipboard)
optdepends=('bash-completion: bash completion support')
source=(\""$source"\")
sha512sums=('"$sha512"')

package() {
    tar xf GENERIC-LINUX-sshyp-"\"\$pkgver\"".tar.xz -C "\"\${pkgdir}\""
}
" > output/PKGBUILD
    printf '\nPKGBUILD generated\n\n'
} &&

_create_apkbuild() {
    printf '\ngenerating APKBUILD...\n'
    local source='https://github.com/rwinkhart/sshyp/releases/download/v$pkgver/GENERIC-LINUX-sshyp-$pkgver.tar.xz'
    printf "# Maintainer: Randall Winkhart <idgr@tutanota.com>
pkgname=sshyp
pkgver="$version"
pkgrel="$((revision-1))"
pkgdesc='A light-weight, self-hosted, synchronized password manager'
options=!check
url='https://github.com/rwinkhart/sshyp'
arch='noarch'
license='GPL-3.0-only'
depends='python3 gnupg openssh xclip wl-clipboard'
source=\""$source"\"

package() {
    mkdir -p "\"\$pkgdir\""
    mkdir -p "\"\$srcdir/usr/share/zsh/site-functions"\"
    mv "\"\$srcdir/usr/share/zsh/functions/Completion/Unix/_sshyp"\" "\"\$srcdir/usr/share/zsh/site-functions/_sshyp"\"
    rm -rf "\"\$srcdir/usr/share/zsh/functions"\"
    cp -r "\"\$srcdir/usr/"\" "\"\$pkgdir\""
}

sha512sums=\"
"$sha512'  'GENERIC-LINUX-sshyp-\"\$pkgver\".tar.xz"
\"
" > output/APKBUILD
    printf '\nAPKBUILD generated\n\n'
} &&

_create_hpkg() {
    printf '\npackaging for Haiku...\n'
    mkdir -p output/haikutemp/bin \
         output/haikutemp/lib/sshyp/extensions \
         output/haikutemp/documentation/packages/sshyp \
         output/haikutemp/documentation/man/man1 \
         output/haikutemp/data/bash-completion/completions \
         output/haikutemp/data/zsh/site-functions
    printf "name			sshyp
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
	\"2021-2023 Randall Winkhart\"
}
provides {
	sshyp = "$version"
	cmd:sshyp
}
requires {
	gnupg
	openssh
	python310
}
urls {
	\"https://github.com/rwinkhart/sshyp\"
}
" > output/haikutemp/.PackageInfo
    # START PORT
	cp -r lib/. port-jobs/working/
	cd port-jobs
	./CLIPBOARD.py HAIKU
	./COMMENTS.py ALL
	./TABS.sh TABS
	cd ..
    cp -r port-jobs/working/. output/haikutemp/lib/sshyp/
    # END PORT
    sed -i '1 s/.*/#!\/bin\/env\ python3.10/' output/haikutemp/lib/sshyp/sshync.py
    sed -i '1 s/.*/#!\/bin\/env\ python3.10/' output/haikutemp/lib/sshyp/sshyp.py
    ln -s /system/lib/sshyp/sshyp.py output/haikutemp/bin/sshyp
    cp -r share/doc/sshyp/. output/haikutemp/documentation/packages/sshyp/
    cp -r share/licenses/sshyp/. output/haikutemp/documentation/packages/sshyp/
    cp extra/completion.bash output/haikutemp/data/bash-completion/completions/sshyp
    cp extra/completion.zsh output/haikutemp/data/zsh/site-functions/_sshyp
    cp extra/manpage output/haikutemp/documentation/man/man1/sshyp.1
    gzip output/haikutemp/documentation/man/man1/sshyp.1
    cd output/haikutemp
    package create -b HAIKU-sshyp-"$version"-"$revision"_all.hpkg
    package add HAIKU-sshyp-"$version"-"$revision"_all.hpkg bin lib documentation data
    cd ../..
    mv output/haikutemp/HAIKU-sshyp-"$version"-"$revision"_all.hpkg output/
    rm -rf output/haikutemp
    printf '\nHaiku packaging complete\n\n'
} &&

_create_deb() {
    printf '\npackaging for Debian/Ubuntu...\n'
    mkdir -p output/debiantemp/sshyp_"$version"-"$revision"_all/DEBIAN \
         output/debiantemp/sshyp_"$version"-"$revision"_all/usr/lib/sshyp/extensions \
         output/debiantemp/sshyp_"$version"-"$revision"_all/usr/bin \
         output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1 \
         output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/bash-completion/completions \
         output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/zsh/functions/Completion/Unix
    printf "Package: sshyp
Version: $version
Section: utils
Architecture: all
Maintainer: Randall Winkhart <idgr at tutanota dot com>
Description: A light-weight, self-hosted, synchronized password manager
Depends: python3, gnupg, openssh-client, xclip, wl-clipboard
Suggests: bash-completion
Priority: optional
Installed-Size: 14584
" > output/debiantemp/sshyp_"$version"-"$revision"_all/DEBIAN/control
    # START PORT
	cp -r lib/. port-jobs/working/
	cd port-jobs
	./CLIPBOARD.py LINUX
	./COMMENTS.py ALL
	./TABS.sh TABS
	cd ..
    cp -r port-jobs/working/. output/debiantemp/sshyp_"$version"-"$revision"_all/usr/lib/sshyp/
    # END PORT
    ln -s /usr/lib/sshyp/sshyp.py output/debiantemp/sshyp_"$version"-"$revision"_all/usr/bin/sshyp
    cp -r share output/debiantemp/sshyp_"$version"-"$revision"_all/usr/
    cp extra/completion.bash output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/zsh/functions/Completion/Unix/_sshyp
    cp extra/manpage output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1/sshyp.1
    gzip output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group output/debiantemp/sshyp_"$version"-"$revision"_all/
    mv output/debiantemp/sshyp_"$version"-"$revision"_all.deb output/DEBIAN-sshyp_"$version"-"$revision"_all.deb
    rm -rf output/debiantemp
    printf '\nDebian/Ubuntu packaging complete\n\n'
} &&

_create_termux() {
    printf '\npackaging for Termux...\n'
    mkdir -p output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/DEBIAN \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/lib/sshyp/extensions \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/bin \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1 \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/bash-completion/completions \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/zsh/functions/Completion/Unix
    printf "Package: sshyp
Version: $version
Section: utils
Architecture: all
Maintainer: Randall Winkhart <idgr at tutanota dot com>
Description: A light-weight, self-hosted, synchronized password manager
Depends: python, gnupg, openssh, termux-api, termux-am
Suggests: bash-completion
Priority: optional
Installed-Size: 14584
" > output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/DEBIAN/control
    # START PORT
	cp -r lib/. port-jobs/working/
	cd port-jobs
	./CLIPBOARD.py TERMUX
	./COMMENTS.py ALL
	./TABS.sh TABS
	cd ..
    cp -r port-jobs/working/. output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/lib/sshyp/
    # END PORT
    ln -s /data/data/com.termux/files/usr/lib/sshyp/sshyp.py output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/bin/sshyp
    cp -r share output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/
    cp extra/completion.bash output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/zsh/functions/Completion/Unix/_sshyp
    cp extra/manpage output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    gzip output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/
    mv output/termuxtemp/sshyp_"$version"-"$revision"_all_termux.deb output/TERMUX-sshyp_"$version"-"$revision"_all_termux.deb
    rm -rf output/termuxtemp
    printf '\nTermux packaging complete\n\n'
} &&

_create_rpm() {
    printf '\npackaging for Fedora...\n'
    rm -rf ~/rpmbuild
    rpmdev-setuptree
    cp output/GENERIC-LINUX-sshyp-"$version".tar.xz ~/rpmbuild/SOURCES
    printf "Name:           sshyp
Version:        "$version"
Release:        "$revision"
Summary:        A light-weight, self-hosted, synchronized password manager
BuildArch:      noarch
License:        GPL-3.0-only
URL:            https://github.com/rwinkhart/sshyp
Source0:        GENERIC-sshyp-"$version".tar.xz
Requires:       python gnupg openssh-clients wl-clipboard
Recommends:     bash-completion
%description
sshyp is a password-store compatible CLI password manager available for UNIX(-like) systems - its primary goal is to make syncing passwords and notes across devices as easy as possible via CLI.
%install
tar xf %{_sourcedir}/GENERIC-LINUX-sshyp-"$version".tar.xz -C %{_sourcedir}
cp -r %{_sourcedir}/usr %{buildroot}
%files
/usr/bin/sshyp
/usr/lib/sshyp/sshyp.py
/usr/lib/sshyp/sshync.py
/usr/share/bash-completion/completions/sshyp
/usr/share/zsh/functions/Completion/Unix/_sshyp
%license /usr/share/licenses/sshyp/license
%doc
/usr/share/doc/sshyp/changelog
/usr/share/man/man1/sshyp.1.gz
" > ~/rpmbuild/SPECS/sshyp.spec
rpmbuild -bb ~/rpmbuild/SPECS/sshyp.spec
mv ~/rpmbuild/RPMS/noarch/sshyp-"$version"-"$revision".noarch.rpm output/FEDORA-sshyp-"$version"-"$revision".noarch.rpm
rm -rf ~/rpmbuild
printf '\nFedora packaging complete\n\n'
} &&

_create_freebsd_pkg() {
    printf '\npackaging for FreeBSD...\n'
    mkdir -p output/freebsdtemp/usr/lib/sshyp/extensions \
         output/freebsdtemp/usr/bin \
         output/freebsdtemp/usr/share/man/man1 \
         output/freebsdtemp/usr/local/share/bash-completion/completions \
         output/freebsdtemp/usr/local/share/zsh/site-functions
    printf "name: sshyp
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
                   \"xclip\" : {
                      \"origin\" : \"x11/xclip\"
                   },
                   \"wl-clipboard\" : {
                      \"origin\" : \"x11/wl-clipboard\"
                   },
                },
" > output/freebsdtemp/+MANIFEST
printf "/usr/bin/sshyp
/usr/lib/sshyp/sshync.py
/usr/lib/sshyp/sshyp.py
/usr/local/share/bash-completion/completions/sshyp
/usr/local/share/zsh/site-functions/_sshyp
/usr/share/doc/sshyp/changelog
/usr/share/licenses/sshyp/license
/usr/share/man/man1/sshyp.1.gz
" > output/freebsdtemp/plist
    # START PORT
	cp -r lib/. port-jobs/working/
	cd port-jobs
	./CLIPBOARD.py TERMUX
	./COMMENTS.py ALL
	./TABS.sh TABS
	cd ..
    cp -r port-jobs/working/. output/freebsdtemp/usr/lib/sshyp/
    # END PORT
    ln -s /usr/lib/sshyp/sshyp.py output/freebsdtemp/usr/bin/sshyp
    cp -r share output/freebsdtemp/usr/
    cp extra/completion.bash output/freebsdtemp/usr/local/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/freebsdtemp/usr/local/share/zsh/site-functions/_sshyp
    cp extra/manpage output/freebsdtemp/usr/share/man/man1/sshyp.1
    gzip output/freebsdtemp/usr/share/man/man1/sshyp.1
    pkg create -m output/freebsdtemp/ -r output/freebsdtemp/ -p output/freebsdtemp/plist -o output/
    mv output/sshyp-"$version".pkg output/FREEBSD-sshyp-"$version"-"$revision".pkg
    rm -rf output/freebsdtemp
    printf '\nFreeBSD packaging complete\n\n'
} &&

case "$1" in
    generic)
        _create_generic
        ;;
    pkgbuild)
        _create_generic_linux
        _create_pkgbuild
        ;;
    apkbuild)
        _create_generic_linux
        _create_apkbuild
        ;;
    haiku)
        _create_hpkg
        ;;
    debian)
        _create_deb
        ;;
    termux)
        _create_termux
        ;;
    fedora)
        _create_generic_linux
        _create_rpm
        ;;
    freebsd)
        _create_freebsd_pkg
        ;;
    buildable-arch)
        _create_generic_linux
        _create_arch
        _create_alpine
        case "$(pacman -Q dpkg)" in
            dpkg*)
            _create_deb
            _create_termux
            ;;
        esac
        case "$(pacman -Q freebsd-pkg)" in
            freebsd-pkg*)
            _create_freebsd_pkg
            ;;
        esac
        ;;
    *)
    printf '\nusage: package.sh [target] <revision>\n\ntargets:\n mainline: pkgbuild apkbuild fedora debian haiku freebsd\n experimental: termux\n groups: buildable-arch\n\n'
    ;;
esac
