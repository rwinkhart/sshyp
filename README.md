![sshyp](https://github.com/rwinkhart/sshyp-labs/blob/main/extra/artwork/sshyp-banner.png)
![release](https://img.shields.io/github/v/release/rwinkhart/sshyp)![python](https://img.shields.io/badge/python-3.7--3.11-yellow)![downloads](https://img.shields.io/github/downloads/rwinkhart/sshyp/total)[![CodeQL](https://github.com/rwinkhart/sshyp/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/rwinkhart/sshyp/actions/workflows/codeql-analysis.yml)

pronounced as: 'sheep', 'shēp'

sshyp is a very simple self-hosted, synchronized password manager for UNIX(-like) systems (currently Haiku/FreeBSD/Linux).

sshyp is compatible with entries created by pass/password-store, as its original goal was to be like pass/password-store, but far more user-friendly to synchronize with a self-hosted server.

sshyp is (as of writing) the only password-store compatible CLI password manager available for Haiku.

sshyp makes use of a custom sftp wrapper, called sshync (ssh+sync), to reliably sync user entries with a local or remote server.

The name "sshyp" is a combination of its syncing library, "sshync", and "passwords".

# WARNING
It is your responsibility to assess the security and stability of "sshyp" before using it and ensure it meets your needs.
I am not responsible for any data loss or breaches of your information resulting from the use of "sshyp".
"sshyp" is a new project that is constantly being updated, and though safety and security are priorities, they cannot be guaranteed.

# Mission Statement
sshyp aims to make it as simple as possible to manage passwords and notes via CLI across multiple devices in a secure, self-hosted fashion.

What sshyp can do:

- securely manage a collection of encrypted passwords and notes via CLI
- generate new, secure passwords to the user's choice in length and complexity
- securely sync said passwords and notes seamlessly between devices (or just manage them offline)
- utilize [extensions](https://github.com/rwinkhart/sshyp-labs) to interact with your entries is additional ways (such as generating TOTP keys or managing your entries in a GUI)
- everything above with entries created by pass/password-store!
- everything above on Haiku, FreeBSD, Linux, and Termux (an Android terminal emulator)!

What sshyp definitely won't do:

- Non-UNIX(-like) support, e.g. Windows (I'd be happy to link to third-party ports, if someone were to make them)

# Installation
Please see the [installation guide](https://github.com/rwinkhart/sshyp/wiki/Installation) in the sshyp wiki for directions specific to your distribution/OS.

Pre-built packages exist for Haiku, FreeBSD, Alpine Linux, Arch Linux, Debian/Ubuntu Linux, Fedora Linux, and Termux. These can be downloaded from the releases page.

Requests for additional distribution/OS support can be filed as issues.

Extensions are available in the [sshyp-labs](https://github.com/rwinkhart/sshyp-labs) repository.

Bash completions can be enabled by installing your distribution's "bash-completion" package and restarting your terminal.

# Building
Since sshyp is written entirely in Python, it doesn't need to be compiled. It does, however, need to be packaged for installation.

A packaging script is included in the root directory of the repo in order to package sshyp for your distribution. To package sshyp from source, simply run:

```
git clone https://github.com/rwinkhart/sshyp.git
cd sshyp
./package.sh [target] <revision>
```

The packaging script has been tested on Arch Linux with "dpkg" as a dependency for Debian/Ubuntu and Termux packaging and "freebsd-pkg" as a dependency for FreeBSD packaging.

Haiku and Fedora packaging must be done on their own respective distributions.

The AUR version and the packages attatched to the release tags were already packaged using this script.

Currently, the script can create packages for Haiku, FreeBSD, Alpine Linux (APKBUILD), Arch Linux (PKGBUILD), Debian/Ubuntu Linux, Fedora Linux, Termux, and generic.

# Usage
Upon initial installation (on both the server and client devices), be sure to run:

```
sshyp tweak
```

This command will allow you to configure the settings necessary for sshyp to function. To ensure configuration compatibility, it is a good idea to run 'sshyp tweak' after each major update.

Please note that decrypting and reading entries is disabled on server devices for security reasons. Only devices configured as clients can use the gpg key to decrypt entries.

All available options can be found with:

```
sshyp --help
```

Or alternatively, in the manpage:

```
man sshyp
```

# Roadmap
Short-term Goals:

- a minimal GUI app - being made as an [extension](https://github.com/rwinkhart/sshyp-labs)
- improved extension integration (allow extensions to add new arguments)

Long-term Goals:

- a fun surprise
- seize the thrones, shear the humans
