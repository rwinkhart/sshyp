![sshyp](https://github.com/rwinkhart/sshyp-labs/blob/main/extra/artwork/sshyp-banner.png)

[![release](https://img.shields.io/github/v/release/rwinkhart/sshyp)](https://github.com/rwinkhart/sshyp/releases)
![python](https://img.shields.io/badge/python-3.8--3.12-yellow)

pronounced as: 'sheep', 'shēp'

sshyp is a self-hosted, synchronized password manager for UNIX(-like) systems (currently Haiku/FreeBSD/Linux). It has been succeeded by [MUTN](https://github.com/rwinkhart/MUTN).

sshyp is compatible with entries created by pass/password-store, as its original goal was to be like pass/password-store, but far more user-friendly to synchronize with a self-hosted server.

sshyp makes use of a custom sftp wrapper, called sshync (ssh+sync), to reliably sync user entries with a local or remote server.

The name "sshyp" is a combination of its synchronization library, "sshync", and "passwords".

# WARNING
It is your responsibility to assess the security and stability of sshyp and to ensure it meets your needs before using it.
I am not responsible for any data loss or breaches of your information resulting from the use of sshyp.
sshyp has not been extensively tested by the public; safety and security are priorities, but they cannot be guaranteed.

# Installation
**Important:** *Shell completions (both Bash and ZSH) may require additional configuration on some distributions - please see [this page](https://github.com/rwinkhart/sshyp/blob/main/wiki/completions.md) of the wiki for support.*

Please see the [installation guide](https://github.com/rwinkhart/sshyp/blob/main/wiki/install.md) in the sshyp wiki for directions specific to your distribution/OS.

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

# Roadmap (successor)

[MUTN](https://github.com/rwinkhart/MUTN) has been developed as a direct successor to sshyp. It is not yet at release v1.0.0, therefore breaking changes will be made.

If you're interested in migrating to MUTN early, please see the [migration guide](https://github.com/rwinkhart/libmutton/blob/main/wiki/migration.md).

Some key differences are:
- Modularity/Maintainability
    - MUTN is based off of [libmutton](https://github.com/rwinkhart/libmutton), enabling third-party clients
    - Due to the modularity of the code, there will be no more "extension" support
        - sshyp-mfa functionality is built into the successor
    - Server and client code are now two completely separate projects
        - This greatly simplifies the code and makes it easier to maintain
        - This also means that third-party clients do not need to maintain separate server code
- Stability
    - sshyp has a track record of making breaking changes in most of its updates
        - This will not be the case with MUTN (starting with release v1.0.0)
- Efficiency
    - MUTN is written in a compiled language (Go)
        - This means that encryption and SSH-sync can be done natively in Go rather than relying on GnuPG/OpenSSH (this is possible with Python, but it would require users to install third-party libraries)
    - MUTN makes small tweaks to the design established by sshyp to make user interactions less frustrating
- Platform support
    - MUTN was built from the ground-up to support both UNIX-like platforms AND Windows
        - Unfortunately, using Go means dropping Haiku support, as newer versions of Go do not (yet) support Haiku

From this point forward, sshyp will only receive minimal support (as needed) and transitional updates.
