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
sha512sums_x86_64=('e5dce9b93010b78f451de0e48b5fdc78db15f2475b6aff06e508caebf1be4cc92dfa673f627d7b1b2d4332d856c3e151391245c035ae85d60b4c08297d1d5629')
sha512sums_aarch64=('e5dce9b93010b78f451de0e48b5fdc78db15f2475b6aff06e508caebf1be4cc92dfa673f627d7b1b2d4332d856c3e151391245c035ae85d60b4c08297d1d5629')

package() {

	tar xf rpass-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/rpass

}
