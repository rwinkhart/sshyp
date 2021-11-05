# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=sshyp
pkgver=2021.11.05.fr1
pkgrel=1
pkgdesc='A self-hosted, synchronized password manager'
url='https://github.com/rwinkhart/sshyp'
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh nano xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.11.05.fr1/sshyp-2021.11.05.fr1.tar.xz')
source_aarch64=('https://github.com/rwinkhart/sshyp/releases/download/v2021.11.05.fr1/sshyp-2021.11.05.fr1.tar.xz')
sha512sums_x86_64=('823913d64e757223826301481d92a866bcf66026d4eb869249963758046555525d8d629fa8f2a12fa539032e27d6eb75e08e66973d6f2f8d0735797df6da1a69')
sha512sums_aarch64=('823913d64e757223826301481d92a866bcf66026d4eb869249963758046555525d8d629fa8f2a12fa539032e27d6eb75e08e66973d6f2f8d0735797df6da1a69')

package() {

	tar xf sshyp-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/sshyp

}
