![sshyp](https://github.com/rwinkhart/sshyp-labs/blob/main/extra/artwork/sshyp-banner.png)

[![release](https://img.shields.io/github/v/release/rwinkhart/sshyp)](https://github.com/rwinkhart/sshyp/releases)
![python](https://img.shields.io/badge/python-3.8--3.12-yellow)

pronounced as: 'sheep', 'shēp'

sshyp is a very simple self-hosted, synchronized password manager for UNIX(-like) systems (currently Haiku/FreeBSD/Linux).

sshyp is compatible with entries created by pass/password-store, as its original goal was to be like pass/password-store, but far more user-friendly to synchronize with a self-hosted server.

sshyp makes use of a custom sftp wrapper, called sshync (ssh+sync), to reliably sync user entries with a local or remote server.

The name "sshyp" is a combination of its synchronization library, "sshync", and "passwords".

# WARNING
It is your responsibility to assess the security and stability of sshyp and to ensure it meets your needs before using it.
I am not responsible for any data loss or breaches of your information resulting from the use of sshyp.
sshyp has not been extensively tested by the public; safety and security are priorities, but they cannot be guaranteed.

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

The successor to sshyp is currently being developed in private. The repository will be made public once it is in a state I find to be respectable. It is being developed in Go and features a very similar design to sshyp.

Some key differences are:
- Modularity/Maintainability
    - sshyp's successor is being designed to be usable as a library to build different front-ends off of
    - Due to the modularity of the code, there will be no more "extension" support
        - sshyp-mfa functionality is built into the successor
    - Server and client code are now two completely separate projects
        - This greatly simplifies the code and makes it easier to maintain
        - This also means that third-party clients do not need to maintain separate server code
- Stability
    - sshyp has a track-record of making breaking changes in most of its updates
        - This will not be the case with its successor (starting with release v1.0.0)
- Efficiency
    - sshyp's successor is written in a compiled language (Go)
        - This means that encryption and SSH-sync can be done natively in Go rather than relying on GnuPG/OpenSSH (this is possible with Python, but it would require users to install third-party libraries)
    - sshyp's successor makes small tweaks to the design of sshyp to make user interactions less frustrating
- Platform support
    - sshyp's successor is being built from the ground-up to support both UNIX-like platforms AND Windows
        - Unfortunately, using Go means dropping Haiku support, as newer versions of Go do not (yet) support Haiku

Progress is already _well underway_. sshyp's successor is already developed to the point of being at feature-parity with sshyp (without online syncing _just yet_). From this point forward, sshyp will only receive minimal support (as needed) and transitional updates.