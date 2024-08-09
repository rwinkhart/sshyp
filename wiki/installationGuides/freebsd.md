## Installation (FreeBSD)
The FreeBSD package is actively tested on the latest version of FreeBSD 14 and should be fully functional on at least FreeBSD 13+.
***
1. Download the *.pkg file from the [latest tagged release of sshyp](https://github.com/rwinkhart/sshyp/releases)

2. Run `sudo pkg add <path/to/*.pkg>`

   ^ the install may fail if you are missing any dependencies - please install the dependencies reported by the package manager and try again

3. sshyp is now installed - run `sshyp init` to get started!
