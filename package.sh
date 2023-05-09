#!/bin/sh

version=$(sed -n '1{p;q}' share/doc/sshyp/changelog | cut -c8-)
if [ -z "$2" ]; then
    revision=1
else
    revision="$2"
fi

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
    ./UNAME.py LINUX
    ./COMMENTS.py ALL
    ./BLANKS.py
    ./TABS.sh TABS
    cd ..
    mv port-jobs/working/* output/linuxtemp/usr/lib/sshyp/
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
    if [ "$1" = 'Deb' ]; then
        local source='https://github.com/rwinkhart/sshyp/releases/download/v"$pkgver"/UBUNTU-sshyp_"$pkgver"-"$pkgrel"_all.deb'
        local decomp_target='data.tar.xz'
    else
        local source='https://github.com/rwinkhart/sshyp/releases/download/v"$pkgver"/GENERIC-LINUX-sshyp-"$pkgver".tar.xz'
        local decomp_target='GENERIC-LINUX-sshyp-"$pkgver".tar.xz'
    fi
    printf "# Maintainer: Randall Winkhart <idgr at tutanota dot com>
pkgname=sshyp
pkgver="$version"
pkgrel="$revision"
pkgdesc='A light-weight, self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('any')
license=('GPL-3.0-only')
depends=(python gnupg openssh)
optdepends=(
    'wl-clipboard: wayland clipboard support'
    'xclip: x11 clipboard support'
    'bash-completion: bash completion support'
)
source=(\""$source"\")
sha512sums=('"$sha512"')

package() {
    tar -xf $decomp_target -C "\"\${pkgdir}\""
}
" > output/PKGBUILD
    printf '\nPKGBUILD generated\n\n'
} &&

_create_apkbuild() {
    printf '\ngenerating APKBUILD...\n'
    if [ "$1" = 'Deb' ]; then
        local source="https://github.com/rwinkhart/sshyp/releases/download/v\"\$pkgver\"/UBUNTU-sshyp_\"\$pkgver\"-"$revision"_all.deb"
        local sumsname="UBUNTU-sshyp_\"\$pkgver\"-"$revision"_all.deb"
        local processing='mkdir -p "$pkgdir"
    7z x "$srcdir"/* -o"$srcdir"
    tar -xf "$srcdir"/data.tar -C "$pkgdir"
    mkdir -p "$pkgdir/usr/share/zsh/site-functions"
    mv "$pkgdir/usr/share/zsh/functions/Completion/Unix/_sshyp" "$pkgdir/usr/share/zsh/site-functions/_sshyp"
    rm -rf "$pkgdir/usr/share/zsh/functions"'
    else
        local source='https://github.com/rwinkhart/sshyp/releases/download/v"$pkgver"/GENERIC-LINUX-sshyp-"$pkgver".tar.xz'
        local sumsname='GENERIC-LINUX-sshyp-"$pkgver".tar.xz'
        local processing='mkdir -p "$pkgdir"
    mkdir -p "$srcdir/usr/share/zsh/site-functions"
    mv "$srcdir/usr/share/zsh/functions/Completion/Unix/_sshyp" "$srcdir/usr/share/zsh/site-functions/_sshyp"
    rm -rf "$srcdir/usr/share/zsh/functions"
    cp -r "$srcdir/usr/" "$pkgdir"'
    fi
    printf "# Maintainer: Randall Winkhart <idgr@tutanota.com>
pkgname=sshyp
pkgver="$version"
pkgrel="$((revision-1))"
pkgdesc='A light-weight, self-hosted, synchronized password manager'
options=!check
url='https://github.com/rwinkhart/sshyp'
arch='noarch'
license='GPL-3.0-only'
depends='python3 gnupg openssh'
source=\""$source"\"

package() {
    $processing
}

sha512sums=\"
"$sha512"  "$sumsname"
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
    printf "name            sshyp_client
version         "$version"-"$revision"
architecture        any
summary         \"A light-weight, self-hosted, synchronized password manager (client only)\"
description     \"The fully-featured client for the sshyp password manager ported for Haiku. This is just a client: server hosting functionality is only available on Linux/BSD.\"
packager        \"Randall Winkhart <idgr at tutanota dot com>\"
vendor          \"Randall Winkhart\"
licenses {
    \"GNU GPL v3\"
}
copyrights {
    \"2021-2023 Randall Winkhart\"
}
provides {
    sshyp_client = "$version"
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
    ./SHEBANG.sh
    ./RMSERVER.py
    ./CLIPBOARD.py HAIKU
    ./COMMENTS.py ALL
    ./UNAME.py TMP
    ./BLANKS.py
    ./TABS.sh TABS
    cd ..
    mv port-jobs/working/* output/haikutemp/lib/sshyp/
    # END PORT
    ln -s /system/lib/sshyp/sshyp.py output/haikutemp/bin/sshyp
    cp -r share/licenses/sshyp/. output/haikutemp/documentation/packages/sshyp/
    cp extra/completion.bash output/haikutemp/data/bash-completion/completions/sshyp
    cp extra/completion.zsh output/haikutemp/data/zsh/site-functions/_sshyp
    cp extra/manpage output/haikutemp/documentation/man/man1/sshyp.1
    gzip output/haikutemp/documentation/man/man1/sshyp.1
    cd output/haikutemp
    package create -b HAIKU-sshyp-client-"$version"-"$revision"_all.hpkg
    package add HAIKU-sshyp-client-"$version"-"$revision"_all.hpkg bin lib documentation data
    cd ../..
    mv output/haikutemp/HAIKU-sshyp-client-"$version"-"$revision"_all.hpkg output/
    rm -rf output/haikutemp
    printf '\nHaiku packaging complete\n\n'
} &&

_create_deb() {
    printf "\npackaging for $1...\n"
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
Depends: python3, gnupg, openssh-client
Suggests: wl-clipboard, xclip, bash-completion
Priority: optional
Installed-Size: 71680
" > output/debiantemp/sshyp_"$version"-"$revision"_all/DEBIAN/control
    # START PORT
    cp -r lib/. port-jobs/working/
    cd port-jobs
    if [ "$1" = 'Debian' ]; then
        ./CLIPBOARD.py LINUX
        special=UBUNTU
    else
        ./CLIPBOARD.py WSL
        special=WSL-ONLY-UBUNTU
    fi
    ./UNAME.py LINUX
    ./COMMENTS.py ALL
    ./BLANKS.py
    ./TABS.sh TABS
    cd ..
    mv port-jobs/working/* output/debiantemp/sshyp_"$version"-"$revision"_all/usr/lib/sshyp/
    # END PORT
    ln -s /usr/lib/sshyp/sshyp.py output/debiantemp/sshyp_"$version"-"$revision"_all/usr/bin/sshyp
    cp -r share output/debiantemp/sshyp_"$version"-"$revision"_all/usr/
    cp extra/completion.bash output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/zsh/functions/Completion/Unix/_sshyp
    cp extra/manpage output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1/sshyp.1
    gzip output/debiantemp/sshyp_"$version"-"$revision"_all/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group -z6 -Sextreme -Zxz output/debiantemp/sshyp_"$version"-"$revision"_all/
    mv output/debiantemp/sshyp_"$version"-"$revision"_all.deb output/"$special"-sshyp_"$version"-"$revision"_all.deb
    rm -rf output/debiantemp
    sha512="$(sha512sum output/"$special"-sshyp_"$version"-"$revision"_all.deb | awk '{print $1;}')"
    printf "\n$1 packaging complete\n\n"
} &&

_create_termux() {
    printf '\npackaging for Termux...\n'
    mkdir -p output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/DEBIAN \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/lib/sshyp/extensions \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/bin \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1 \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/bash-completion/completions \
         output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/zsh/site-functions
    printf "Package: sshyp
Version: $version
Section: utils
Architecture: all
Maintainer: Randall Winkhart <idgr at tutanota dot com>
Description: A light-weight, self-hosted, synchronized password manager
Depends: python, gnupg, openssh, termux-api, termux-am
Suggests: bash-completion
Priority: optional
Installed-Size: 71680
" > output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/DEBIAN/control
    # START PORT
    cp -r lib/. port-jobs/working/
    cd port-jobs
    ./CLIPBOARD.py TERMUX
    ./UNAME.py TERMUX
    ./COMMENTS.py ALL
    ./BLANKS.py
    ./TABS.sh TABS
    cd ..
    mv port-jobs/working/* output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/lib/sshyp/
    # END PORT
    ln -s /data/data/com.termux/files/usr/lib/sshyp/sshyp.py output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/bin/sshyp
    cp -r share output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/
    cp extra/completion.bash output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/zsh/site-functions/_sshyp
    cp extra/manpage output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    gzip output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/data/data/com.termux/files/usr/share/man/man1/sshyp.1
    dpkg-deb --build --root-owner-group -z6 -Sextreme -Zxz output/termuxtemp/sshyp_"$version"-"$revision"_all_termux/
    mv output/termuxtemp/sshyp_"$version"-"$revision"_all_termux.deb output/TERMUX-sshyp_"$version"-"$revision"_all_termux.deb
    rm -rf output/termuxtemp
    printf '\nTermux packaging complete\n\n'
} &&

_create_rpm() {
    printf '\npackaging for Fedora...\n'
    rm -rf ~/rpmbuild
    rpmdev-setuptree
    mkdir -p output/fedoratemp/usr/bin \
         output/fedoratemp/usr/lib/sshyp/extensions \
         output/fedoratemp/usr/share/man/man1 \
         output/fedoratemp/usr/share/bash-completion/completions \
         output/fedoratemp/usr/share/zsh/site-functions
    printf "Name:           sshyp
Version:        "$version"
Release:        "$revision"
Summary:        A light-weight, self-hosted, synchronized password manager
BuildArch:      noarch
License:        GPL-3.0-only
URL:            https://github.com/rwinkhart/sshyp
Source0:        GENERIC-FEDORA-sshyp-"$version".tar.xz
Requires:       python gnupg openssh-clients
Recommends:     wl-clipboard xclip bash-completion
%%description
sshyp is a password-store compatible CLI password manager available for UNIX(-like) systems - its primary goal is to make syncing passwords and notes across devices as easy as possible via CLI.
%%install
tar xf %%{_sourcedir}/GENERIC-FEDORA-sshyp-"$version".tar.xz -C %%{_sourcedir}
cp -r %%{_sourcedir}/usr %%{buildroot}
%%files
/usr/bin/sshyp
/usr/lib/sshyp/sshyp.py
/usr/lib/sshyp/sshync.py
/usr/share/bash-completion/completions/sshyp
/usr/share/zsh/site-functions/_sshyp
%%license /usr/share/licenses/sshyp/license
%%doc
/usr/share/man/man1/sshyp.1.gz
" > ~/rpmbuild/SPECS/sshyp.spec
    # START PORT
    cp -r lib/. port-jobs/working/
    cd port-jobs
    ./CLIPBOARD.py LINUX
    ./UNAME.py LINUX
    ./COMMENTS.py ALL
    ./BLANKS.py
    ./TABS.sh TABS
    cd ..
    mv port-jobs/working/* output/fedoratemp/usr/lib/sshyp/
    # END PORT
    ln -s /usr/lib/sshyp/sshyp.py output/fedoratemp/usr/bin/sshyp
    cp -r share output/fedoratemp/usr/
    cp extra/completion.bash output/fedoratemp/usr/share/bash-completion/completions/sshyp
    cp extra/completion.zsh output/fedoratemp/usr/share/zsh/site-functions/_sshyp
    cp extra/manpage output/fedoratemp/usr/share/man/man1/sshyp.1
    gzip output/fedoratemp/usr/share/man/man1/sshyp.1
    XZ_OPT=-e6 tar -C output/fedoratemp -cvJf output/GENERIC-FEDORA-sshyp-"$version".tar.xz usr/
    rm -rf output/fedoratemp
    cp output/GENERIC-FEDORA-sshyp-"$version".tar.xz ~/rpmbuild/SOURCES
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
                },
" > output/freebsdtemp/+MANIFEST
printf "/usr/bin/sshyp
/usr/lib/sshyp/sshync.py
/usr/lib/sshyp/sshyp.py
/usr/local/share/bash-completion/completions/sshyp
/usr/local/share/zsh/site-functions/_sshyp
/usr/share/licenses/sshyp/license
/usr/share/man/man1/sshyp.1.gz
" > output/freebsdtemp/plist
    # START PORT
    cp -r lib/. port-jobs/working/
    cd port-jobs
    ./CLIPBOARD.py TERMUX
    ./UNAME.py TMP
    ./COMMENTS.py ALL
    ./BLANKS.py
    ./TABS.sh TABS
    cd ..
    mv port-jobs/working/* output/freebsdtemp/usr/lib/sshyp/
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
    pkgbuild)
        _create_generic_linux
        _create_pkgbuild Generic
        ;;
    pkgbuild-deb)
        _create_deb Debian
        _create_pkgbuild Deb
        ;;
    apkbuild)
        _create_generic_linux
        _create_apkbuild Generic
        ;;
    apkbuild-deb)
        _create_deb Debian
        _create_apkbuild Deb
        ;;
    haiku)
        _create_hpkg
        ;;
    debian)
        _create_deb Debian
        ;;
    wsl)
        _create_deb WSL
        ;;
    termux)
        _create_termux
        ;;
    fedora)
        _create_rpm
        ;;
    freebsd)
        _create_freebsd_pkg
        ;;
    buildable-arch)
        _create_generic_linux
        _create_pkgbuild Generic
        _create_apkbuild Generic
        case "$(pacman -Q dpkg)" in
            dpkg*)
            _create_termux
            _create_deb WSL
            _create_deb Debian
            ;;
        esac
        case "$(pacman -Q freebsd-pkg)" in
            freebsd-pkg*)
            _create_freebsd_pkg
            ;;
        esac
        ;;
    buildable-arch-deb)
        _create_termux
        _create_deb WSL
        _create_deb Debian
        _create_pkgbuild Deb
        _create_apkbuild Deb
        case "$(pacman -Q freebsd-pkg)" in
            freebsd-pkg*)
            _create_freebsd_pkg
            ;;
        esac
        ;;
    *)
    printf '\nusage: package.sh [target] <revision>\n\ntargets:\n mainline: pkgbuild pkgbuild-deb apkbuild apkbuild-deb fedora debian wsl haiku freebsd\n experimental: termux\n groups: buildable-arch buildable-arch-deb\n\n'
    ;;
esac
