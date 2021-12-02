# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=sshyp
pkgver=2021.12.01.fr2.1
pkgrel=1
pkgdesc='A self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh nano xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.12.01.fr2.1/sshyp-2021.12.01.fr2.1.tar.xz')
source_aarch64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.12.01.fr2.1/sshyp-2021.12.01.fr2.1.tar.xz')
sha512sums_x86_64=('fdef7455fd48d190794d2323b3e8d75251d21a472cffb72757e1422c532731492234f250c292e6f27955f6670aa528c609ad786f4abab79a5b4a4d070ce6343b')
sha512sums_aarch64=('fdef7455fd48d190794d2323b3e8d75251d21a472cffb72757e1422c532731492234f250c292e6f27955f6670aa528c609ad786f4abab79a5b4a4d070ce6343b')

package() {

	tar xf sshyp-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/sshyp

}
