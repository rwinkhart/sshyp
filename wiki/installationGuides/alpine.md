## Installation (Alpine Linux)
The Alpine Linux package is actively tested on the latest stable release of Alpine Linux.
***
1. Download the *.apk file from the [latest tagged release of sshyp](https://github.com/rwinkhart/sshyp/releases)

2. Run `doas apk add --allow-untrusted <path/to/*.apk`

3. sshyp is now installed - run `sshyp init` to get started!
***

Creating a package from an APKBUILD? Just use `abuild -r` in the same directory as the APKBUILD.
