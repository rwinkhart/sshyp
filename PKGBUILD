# Maintainer: Randall Winkhart <idgr at tutanota dot com>

pkgname=rpass
pkgver=2021.09.14.pr4a4
pkgrel=1
pkgdesc="An rsync-based password manager and alternative to GNU pass"
arch=('x86_64' 'aarch64')
license=('GPL3')
depends=( python gnupg openssh rsync xclip wl-clipboard)

source_x86_64=('https://cloud.watergateserver.xyz/api/public/dl/b-k72YGN')
source_aarch64=('https://cloud.watergateserver.xyz/api/public/dl/b-k72YGN')
sha512sums_x86_64=('c2ab708d63ccb6b2cf5818bbcd4bd320f07405ce3527433daf3688c8acc68dbc7166fe2a6cd57bf4abbf4f1ad0278c5906a3065c6f0465c1db92a3f0162dc7b2')
sha512sums_aarch64=('c2ab708d63ccb6b2cf5818bbcd4bd320f07405ce3527433daf3688c8acc68dbc7166fe2a6cd57bf4abbf4f1ad0278c5906a3065c6f0465c1db92a3f0162dc7b2')

package() {

    mv b-k72YGN rpass-"$pkgver".tar.xz
	tar xf rpass-"$pkgver".tar.xz -C "${pkgdir}"
	chown -R "$USER" ${pkgdir}/var/lib/rpass

}
