## Installation (Termux)
**Missing features:** For technical reasons, the Termux version of sshyp cannot be used as a server (it only functions as a client). Additionally, the Termux package does not support the extension management system, so extensions still must be installed as separate packages.

The Termux package is minimally tested. Attempts to maintain compatibility are made and it should be fully functional on the latest versions of Termux+Termux:API (F-Droid versions), but newer features are more likely to be broken than on other platforms.
***
1. Install the Termux application from [F-Droid](https://f-droid.org/en/packages/com.termux/)

2. Install the Termux API from [F-Droid](https://f-droid.org/en/packages/com.termux.api/) (for clipboard support)

3. From within Termux, run `curl -L <github/link/to/latest/*_termux.deb> -o sshyp.deb`

   ^ copy the required download link from the [latest tagged release of sshyp](https://github.com/rwinkhart/sshyp/releases)

4. From within Termux, run `dpkg -i sshyp.deb; pkg install -f`

5. sshyp is now installed - run `sshyp init` to get started!
