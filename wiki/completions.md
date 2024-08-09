## Shell Completions Troubleshooting
ZSH completions not working? Make sure your ~/.zshrc contains the following:
```
autoload -Uz compinit && compinit
```
...and then restart your shell.
***
Bash completions not working? Install your distribution's 'bash-completion' package or source the completion script manually.

For most environments, this would mean adding the following to your ~/.bashrc:
```
source /usr/share/bash-completion/completions/sshyp
```
Note that this directory is different on FreeBSD and Haiku.

FreeBSD:
```
source /usr/local/share/bash-completion/completions/sshyp
```
Haiku:
```
source /system/data/bash-completion/completions/sshyp
```
...and then restart your shell.

*Please note that Bash completions are slightly more limited than ZSH completions, and as such, new entries will not be auto-completed until the completions script is re-sourced.*
