# rpass
A password manager with rsync integration - alternative to GNU pass

# Installation

Arch Linux (x86_64, aarch64)

rpass releases are available in the Arch User Repository as 'rpass'.

Install with your preferred AUR helper or use:

git clone https://aur.archlinux.org/rpass.git
cd rpass
makepkg -si

Packaging for other distributions coming soon.

# Usage

Upon initial installation, be sure to run:

rpass config

This command will allow you to configure the settings necessary for rpass to function.

All available options can be found with:

rpass --help
