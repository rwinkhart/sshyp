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
sha512sums_x86_64=('88b1db43a0234e00cc9b2b5aa6aff642a350109e101a1ebc95e06e7ebc294b09c8369eead06fd16bbffd1f6ce564fb1e8736685ee716f7806532710d7357a5cb')
sha512sums_aarch64=('88b1db43a0234e00cc9b2b5aa6aff642a350109e101a1ebc95e06e7ebc294b09c8369eead06fd16bbffd1f6ce564fb1e8736685ee716f7806532710d7357a5cb')

package() {

	tar xf sshyp-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/sshyp

}
