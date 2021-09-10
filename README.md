# rpass
A very simple password manager with rsync (and soon libsecret) integration - alternative to GNU pass

-----

rpass will likely be renamed due to the mass quantity of other terminal-based password managers named the same thing.

The new name may be 'rpazz', 'sspass', or something else.

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

All available options can be found with:

```
rpass --help
```

# Roadmap

Short-term Goals:

- overhaul error messages
- create new file list w/color and w/o file extensions
- create a man page
- allow for multi-line notes
- overhaul argument system
- fix lots of bugs!

Medium-term Goals:

- add libsecret integration to allow rpass to act as a gnome-keyring alternative
- create a minimal GUI app optimized for the Pinephone (also compatible with x86_64)

Long-term Goals:

- make an Android port (including GUI)
- make a minimal Windows port
- investigate auto-completion on tab
