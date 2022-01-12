# sshyp
A very simple self-hosted, synchronized password manager. Alternative to GNU pass.

"sshyp" stands for "sshync passwords", or "ssh sync passwords".
"sshync" is the custom syncing backend (based on sftp) used by "sshyp".

# WARNING
It is your responsibility to assess the security and stability of "sshyp" before using it and ensure it meets your needs.
I am not responsible for any data loss or breaches of your information resulting from the use of "sshyp".
"sshyp" is a new project that is constantly being updated, and though safety and security are priorities, they cannot be guaranteed.

# Mission Statement
sshyp aims to make it as simple as possible to manage passwords and notes via CLI across multiple devices in a secure, self-hosted fashion.

What sshyp can do:

- securely manage a collection of encrypted passwords and notes via CLI
- generate new, secure passwords to the user's choice in length and complexity
- securely sync said passwords and notes seamlessly between multiple POSIX compliant Unix devices

What sshyp will do:

- everything it already does, but also in a GUI for Linux/Android
- have a distinct retro theme
- receive many usability enhancements

What sshyp definitely won't do:

- 2FA/MFA (for security purposes, this should not be handled by your password manager)
- Windows support (I don't use Windows and I have no interest in developing for it)

# Installation
Arch Linux (all ISAs)

sshyp releases are available in the Arch User Repository as 'sshyp'.

Install with your preferred AUR helper or use:

```
git clone https://aur.archlinux.org/sshyp.git
cd sshyp
makepkg -si
```

Packaging for other distributions coming soon.

# Building
Since sshyp is written entirely in Python, it doesn't need to be compiled. It does, however, need to be packaged for installation.

A packaging script is included in the root directory of the repo in order to package sshyp for your distribution (currently only a generic package used for the AUR PKGBUILD is supported). To package sshyp from source, simply run:

```
git clone https://github.com/rwinkhart/sshyp.git
cd sshyp
./package.sh
```

The AUR version and the packages attatched to the release tags were already packaged using this script.

Packaging for other distributions coming soon.

# Usage
Upon initial installation (on both the server and client devices), be sure to run:

```
sshyp tweak
```

This command will allow you to configure the settings necessary for sshyp to function.
As of right now, sshyp is rapidly changing, and as such, it is a good idea to run "sshyp tweak" after each update.

Please note that decrypting and reading entries is disabled on server devices for security reasons. Only devices configured as clients can use the gpg key to decrypt entries.

All available options can be found with:

```
sshyp --help
```

Or alternatively, in the new manpage:

```
man sshyp
```

# Roadmap
Short-term Goals:

- create new file list w/color and w/o file extensions
- overhaul argument system
- fix lots of bugs!
- make lots of optimizations!

Medium-term Goals:

- create minimal GUI apps (Linux x86_64, Linux aarch64)
- auto-completion on tab for CLI version

Long-term Goals:

- seize the thrones, shear the humans

# Known Issues

Currently, files deleted from a client or server may re-appear if another client that had the same file reconnects and later re-uploads it to the server. This will be addressed.

Currently, if a client is missing folders that exist on the server, the contents of the missing folders will fail to download. A temporary workaround is to manually create the folders on the client. This will be addressed.
