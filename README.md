# rpass
A very simple password manager with rsync integration - alternative to GNU pass

# Installation
Arch Linux (x86_64, aarch64)

rpass releases are available in the Arch User Repository as 'rpass'.

Install with your preferred AUR helper or use:

```
git clone https://aur.archlinux.org/rpass.git 
cd rpass
makepkg -si
```

Packaging for other distributions coming soon.

# Usage
Upon initial installation, be sure to run:

```
rpass config
```

This command will allow you to configure the settings necessary for rpass to function.
As of right now, rpass is rapidly changing, and as such, it is a good idea to run "rpass config" after each update.

All available options can be found with:

```
rpass --help
```

# Roadmap
Short-term Goals:

- create new file list w/color and w/o file extensions
- create a man page
- overhaul argument system
- add a system to mask names of entries from other programs/users
- fix lots of bugs!
- make lots of optimizations!

Medium-term Goals:

- create minimal GUI apps (Linux x86_64, Linux aarch64, Android aarch64)
- auto-completion on tab for CLI version

Long-term Goals:

- world domination
