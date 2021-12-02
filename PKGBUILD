# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=sshyp
pkgver=2021.12.01.fr2.2
pkgrel=1
pkgdesc='A self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh nano xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.12.01.fr2.2/sshyp-2021.12.01.fr2.2.tar.xz')
source_aarch64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.12.01.fr2.2/sshyp-2021.12.01.fr2.2.tar.xz')
sha512sums_x86_64=('470f7b4fd2bb0cc34a98e8ab5506ae4bc82e311616e2a81ee4fc559dd9e2c2e46a05517a49ba4d4fe108f341f92250bd1d63acca134d277b37d2475e03713adf')
sha512sums_aarch64=('470f7b4fd2bb0cc34a98e8ab5506ae4bc82e311616e2a81ee4fc559dd9e2c2e46a05517a49ba4d4fe108f341f92250bd1d63acca134d277b37d2475e03713adf')

package() {

	tar xf sshyp-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/sshyp

}
