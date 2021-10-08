# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=rpass
pkgver=2021.10.07.mr5
pkgrel=1
pkgdesc='An rsync-based password manager and alternative to GNU pass'
url='https://github.com/rwinkhart/rpass'
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh rsync nano xclip wl-clipboard)

source_x86_64=('https://github.com/rwinkhart/rpass/releases/download/v"$pkgver"/rpass-"$pkgver".tar.xz')
source_aarch64=('https://github.com/rwinkhart/rpass/releases/download/v"$pkgver"/rpass-"$pkgver".tar.xz')
sha512sums_x86_64=('abc1e265d474866c8d538afae923227a9023e6fc508106ca3c29b86627cd28062a3a446029b958afc6dda987a037860156d7c3d34d67afddc71b4d3ae84169b0')
sha512sums_aarch64=('abc1e265d474866c8d538afae923227a9023e6fc508106ca3c29b86627cd28062a3a446029b958afc6dda987a037860156d7c3d34d67afddc71b4d3ae84169b0')

package() {

	tar xf rpass-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/rpass

}
