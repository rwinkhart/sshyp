## Postmortem
### Reflecting on the Flaws of sshyp
Due to being my introduction to the world of programming, sshyp contains many flaws that have been addressed with the creation of [MUTN](https://github.com/rwinkhart/MUTN).

Many of these flaws are the result of a lack of direction for the project.
In the beginning, sshyp was actually called "rpass" and was meant to be a simple wrapper for pass/password-store with rsync integration for synchronization.
I quickly ran into issues using rsync and pivoted to using sftp, thus necessitating the rebrand to "sshyp".
sshyp grew to become its own standalone password manager with no relation to pass/password-store (except for entry import compatibility).

In terms of technical flaws resulting from a lack of experience, here is a non-exhaustive list:
- Port jobs are unnecessarily complex and difficult to maintain; they made working on the project into a chore
- Extensions are unnecessarily complex and their functionality is better left to third-party clients
    - Delegating functionality to extensions meant poor integration with the entry format, help menus, and shell completions
- Due to sshyp being a program with no underlying library, third-party clients are not very feasible
    - Not having a library with the goal of change stability led to breaking changes in nearly every release of sshyp
- Python was a poor choice for my personal desire of portability, as dependencies must be independently installed on each system
    - This led to me avoiding all non-standard libraries, which meant relying on system binaries for things like GPG and SSH
        - This meant taking into account the versions of these binaries shipped by each distribution
        - Because of this, sshyp was tied to OpenSSH (no support for other SSH implementations)
        - This also meant launching separate SSH processes for each item being synchronized, making sshyp's synchronization _very_ slow
- Dynamically typed languages are a poor choice for beginners, as they allow for poor programming practices that create bugs
    - With sshyp, I attempted to "save memory" by re-using variables for multiple purposes
    - sshyp also checks variable types, rather than values, as a shortcut for determining a function's exit status
- sshyp combined the client and server into one package, resulting in lots of unreadable spaghetti code (especially with argument parsing)
- sshyp was designed in a way where it would be very difficult to port to non-UNIX-like platforms (it would basically necessitate a complete rewrite)

Developing [the successor to sshyp](https://github.com/rwinkhart/MUTN) forced me to confront these flaws and make a better product. It also allowed me the chance to re-consider each design decision; I found a better way of doing nearly everything.
