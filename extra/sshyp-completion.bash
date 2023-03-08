#!/usr/bin/env bash

_path_gen() {
    local sshyp_path="$HOME/.local/share/sshyp"
    local sshyp_path_length="$(("${#sshyp_path}" + 1))"
    full_paths=(~/.local/share/sshyp/**/*.gpg)
    for path in "${full_paths[@]}"; do
        trimmed_path=$(echo ${path%????} | cut -c"$sshyp_path_length"-)
        trimmed_paths+=("$trimmed_path")
    done
} &&

# from this point, this completions script was partially generated by
# completely (https://github.com/dannyben/completely)

_sshyp_completions() {
  local cur=${COMP_WORDS[COMP_CWORD]}
  local compwords=("${COMP_WORDS[@]:1:$COMP_CWORD-1}")
  local compline="${compwords[*]}"

  if [ "${#COMP_WORDS[@]}" -gt "2" ] && echo "${COMP_WORDS[@]}" | grep -q 'shear'; then
    return
  elif [ "${#COMP_WORDS[@]}" -gt "3" ] && (! echo "${COMP_WORDS[@]}" | grep -q '/' || echo "${COMP_WORDS[@]}" | grep -q 'shear'); then
    return
  elif [ "${#COMP_WORDS[@]}" -gt "4" ]; then
    return
  fi

  if [[ "$compline" == *'edit'* ]]; then
    while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "relocate username password note url" -- "$cur" )
  elif [[ "$compline" == *'copy'* ]]; then
    while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "username password url note" -- "$cur" )
  elif [[ "$compline" == *'add'* ]]; then
    while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "password note folder" -- "$cur" )
  elif [[ "$compline" == *'gen'* ]]; then
    while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "update" -- "$cur" )
  elif [[ "$compline" == '/'* ]]; then
    while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "add gen edit copy shear" -- "$cur" )
  else
    while read -r; do ITEM=${REPLY// /\\ }; COMPREPLY+=( "$ITEM" ); done < <( compgen -W "help version tweak add gen edit copy shear sync $(printf "'%s' " "${trimmed_paths[@]}")" -- "$cur" )
  fi

} &&
_path_gen && complete -F _sshyp_completions sshyp
