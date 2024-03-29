# sshyp(1) completion

_path_gen() {
    local sshyp_path="$HOME/.local/share/sshyp"
    local glob_status=$(shopt -p globstar)
    [ -z "${glob_status##*u*}" ] && shopt -s globstar  # if recursive globbing is disabled, enable it
    local full_paths=("$sshyp_path"/**/*.gpg)
    $glob_status  # set recursive globbing to user default
    for scan_path in "${full_paths[@]}"; do
      trimmed_paths+=("${scan_path:${#sshyp_path}:-4}")
    done
    if [ "${trimmed_paths[0]}" == '/**/*' ]; then trimmed_paths[0]=help; fi
} &&

_sshyp_completions() {
  local cur=${COMP_WORDS[COMP_CWORD]}
  local prev=${COMP_WORDS[COMP_CWORD-1]}

  case $prev in
    sshyp )
      while read -r; do ITEM=${REPLY// /\\ }; COMPREPLY+=( "$ITEM" ); done < <( compgen -W "$(printf "'%s' " "${trimmed_paths[@]}")" -- "$cur" )
      ;;
    /* )
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "add gen edit copy shear" -- "$cur" )
      ;;
    add )
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "password note folder" -- "$cur" )
      ;;
    copy )
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "password username url note" -- "$cur" )
      ;;
    edit )
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "password username url note relocate" -- "$cur" )
      ;;
    gen )
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "update" -- "$cur" )
      ;;
  esac

} &&
_path_gen && complete -F _sshyp_completions sshyp
