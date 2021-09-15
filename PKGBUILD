# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=rpass
pkgver=2021.09.15.mr4.1
pkgrel=1
pkgdesc="An rsync-based password manager and alternative to GNU pass"
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh rsync xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/rpass/releases/download/v2021.09.15.mr4.1/rpass-2021.09.15.mr4.1.tar.xz')
source_aarch64=('https://github.com/rwinkhart/rpass/releases/download/v2021.09.15.mr4.1/rpass-2021.09.15.mr4.1.tar.xz')
sha512sums_x86_64=('fb162031b2bff1896a4ae2c6c78889ead6c278ec7e5cb6134ec8ccf08004bf87f38839f0cab952ce2047c53a075b0802ec882410048b04b4ababc89a68de71f8')
sha512sums_aarch64=('fb162031b2bff1896a4ae2c6c78889ead6c278ec7e5cb6134ec8ccf08004bf87f38839f0cab952ce2047c53a075b0802ec882410048b04b4ababc89a68de71f8')

package() {

	tar xf rpass-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/rpass

}
