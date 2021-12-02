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
Arch Linux (x86_64, aarch64)

Note: currently unavailable in the AUR (the older version, "rpass", will remain available until sshyp is stable)

sshyp releases will be available in the Arch User Repository as 'sshyp'.

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
sshyp tweak
```

This command will allow you to configure the settings necessary for sshyp to function.
As of right now, sshyp is rapidly changing, and as such, it is a good idea to run "sshyp tweak" after each update.

All available options can be found with:

```
sshyp --help
```

# Roadmap
Short-term Goals:

- create new file list w/color and w/o file extensions
- create a man page
- overhaul argument system
- fix lots of bugs!
- make lots of optimizations!

Medium-term Goals:

- create minimal GUI apps (Linux x86_64, Linux aarch64)
- auto-completion on tab for CLI version

Long-term Goals:

- seize the thrones, shear the humans

# Known Issues
Broken Features in Latest Release:

- the 'gen' function uses the older notetaking system

Broken Features in Source:

- the 'gen' function uses the older notetaking system
