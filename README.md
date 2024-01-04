![sshyp](https://github.com/rwinkhart/sshyp-labs/blob/main/extra/artwork/sshyp-banner.png)

[![release](https://img.shields.io/github/v/release/rwinkhart/sshyp)](https://github.com/rwinkhart/sshyp/releases)
![python](https://img.shields.io/badge/python-3.7--3.12-yellow)
[![downloads](https://img.shields.io/github/downloads/rwinkhart/sshyp/total)](https://github.com/rwinkhart/sshyp/releases)

[![CodeQL](https://github.com/rwinkhart/sshyp/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/rwinkhart/sshyp/actions/workflows/codeql-analysis.yml)

pronounced as: 'sheep', 'shēp'

sshyp is a very simple self-hosted, synchronized password manager for UNIX(-like) systems (currently Haiku/FreeBSD/Linux).

sshyp is compatible with entries created by pass/password-store, as its original goal was to be like pass/password-store, but far more user-friendly to synchronize with a self-hosted server.

sshyp makes use of a custom sftp wrapper, called sshync (ssh+sync), to reliably sync user entries with a local or remote server.

The name "sshyp" is a combination of its synchronization library, "sshync", and "passwords".

# WARNING
It is your responsibility to assess the security and stability of "sshyp" before using it and ensure it meets your needs.
I am not responsible for any data loss or breaches of your information resulting from the use of "sshyp".
"sshyp" is a new project that is constantly being updated, and though safety and security are priorities, they cannot be guaranteed.

Always check the [known bugs](https://github.com/rwinkhart/sshyp/wiki/Known-Bugs) list before updating or installing sshyp.

# Mission Statement
sshyp aims to make it as simple as possible to manage passwords and notes via CLI across multiple devices in a secure, self-hosted fashion.

What sshyp can do:

- securely manage a collection of encrypted passwords and notes via CLI
- generate new, secure passwords to the user's choice in length and complexity
- securely sync said passwords and notes seamlessly between devices (or just manage them offline)
- utilize [extensions](https://github.com/rwinkhart/sshyp-labs) to interact with your entries is additional ways (such as generating TOTP keys or managing your entries in a GUI)
- everything above with entries created by pass/password-store!
- everything above on Haiku, FreeBSD, Linux, and Termux!

# Installation
**Important:** *Shell completions (both Bash and ZSH) may require additional configuration on some distributions - please see [this page](https://github.com/rwinkhart/sshyp/wiki/Completions) of the wiki for support.*

Please see the [installation guide](https://github.com/rwinkhart/sshyp/wiki/Installation) in the sshyp wiki for directions specific to your distribution/OS.

Pre-built packages exist for Haiku, FreeBSD, Alpine Linux, Debian/Ubuntu Linux, Fedora Linux, Termux, and WSL. These can be downloaded from the releases page.

Additionally, sshyp is distributed on the AUR.

Extensions can be installed from the `sshyp tweak` menu on most supported platforms.

For Haiku and Termux, extensions must instead be installed through the [system package manager](https://github.com/rwinkhart/sshyp-labs/releases).

# Building
A packaging script is included in the root directory of the repo in order to package sshyp for your distribution. To package sshyp from source, simply run:

```
git clone https://github.com/rwinkhart/sshyp.git
cd sshyp
./package.sh [target] <revision>
```

The packaging script has been tested on Arch Linux with "dpkg" as a dependency for Debian/Ubuntu/Termux packaging and "freebsd-pkg" as a dependency for FreeBSD packaging.

Haiku and Fedora packaging must be done on their own respective distributions.

The AUR version and the packages attached to the release tags were already packaged using this script.

Currently, the script can create packages for Haiku, FreeBSD, Alpine Linux (APKBUILD), Arch Linux (PKGBUILD), Debian/Ubuntu Linux, Fedora Linux, Termux, and WSL.

# Usage
Upon initial installation (on both the server and client devices), run `sshyp init` to configure the settings necessary for sshyp to function.

In order to configure optional settings or change already configured settings, run `sshyp tweak`.

Please note that decrypting and reading entries is disabled on server devices for security reasons. Only devices configured as clients can use the GPG key to decrypt entries.

All available options can be found with `sshyp help`, or alternatively, in the man page.

# Roadmap
Short-term Goals:

- implement a method for tracking how long it has been since a password has been changed (password aging)
- find and fix more bugs

Long-term Goals:

- migrate from gpg to a better-suited utility focused on symmetric cipher encryption
- seize the thrones, shear the humans
