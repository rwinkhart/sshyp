# sshyp
A very simple self-hosted, synchronized password manager. Alternative to GNU pass.

# Mission Statement
sshyp aims to make it as simple as possible to manage passwords and notes via CLI across multiple devices in a self-hosted fashion.

# Installation
Arch Linux (x86_64, aarch64)

sshyp releases are available in the Arch User Repository as 'sshyp'.

Install with your preferred AUR helper or use:

```
git clone https://aur.archlinux.org/sshyp.git
cd sshyp
makepkg -si
```

Packaging for other distributions coming soon.

# Usage
Upon initial installation, be sure to run:

```
sshyp config
```

This command will allow you to configure the settings necessary for rpass to function.
As of right now, rpass is rapidly changing, and as such, it is a good idea to run "rpass config" after each update.

All available options can be found with:

```
sshyp --help
```

# Roadmap
Short-term Goals:

- re-write bad, leftover "rpass" code
- create new file list w/color and w/o file extensions
- create a man page
- overhaul argument system
- fix lots of bugs!
- make lots of optimizations!

Medium-term Goals:

- create minimal GUI apps (Linux x86_64, Linux aarch64, Android aarch64)
- auto-completion on tab for CLI version

Long-term Goals:

- seize the thrones, shear the humans
