# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=rpass
pkgver=2021.09.15.mr4.1
pkgrel=1
pkgdesc="An rsync-based password manager and alternative to GNU pass"
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh rsync xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/rpass/releases/download/v2021.09.15.mr4/rpass-2021.09.15.mr4.tar.xz')
source_aarch64=('https://github.com/rwinkhart/rpass/releases/download/v2021.09.15.mr4/rpass-2021.09.15.mr4.tar.xz')
sha512sums_x86_64=('615537dc49a05d49070f8d51f4a9b2bee8d40b7c85675a0fd860866a235dd2a3ed43186b4378a3db10accbc8d2c75a0d0220a2918afc32425c0ccb7695dc6b4a')
sha512sums_aarch64=('615537dc49a05d49070f8d51f4a9b2bee8d40b7c85675a0fd860866a235dd2a3ed43186b4378a3db10accbc8d2c75a0d0220a2918afc32425c0ccb7695dc6b4a')

package() {

	tar xf rpass-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/rpass

}
