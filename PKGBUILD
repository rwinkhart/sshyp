# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=sshyp
pkgver=2021.12.01.fr2
pkgrel=1
pkgdesc='A self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh nano xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.12.01.fr2/sshyp-2021.12.01.fr2.tar.xz')
source_aarch64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.12.01.fr2/sshyp-2021.12.01.fr2.tar.xz')
sha512sums_x86_64=('dcc2fe2e751120ffed86cad5f170bdf6ba4ef96df4c4cc784496289c7fda1ccef5ded030ce20f4ea6571a0def5bc185037b39f0958958a1aadb1ead63291b879')
sha512sums_aarch64=('dcc2fe2e751120ffed86cad5f170bdf6ba4ef96df4c4cc784496289c7fda1ccef5ded030ce20f4ea6571a0def5bc185037b39f0958958a1aadb1ead63291b879')

package() {

	tar xf sshyp-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/sshyp

}
