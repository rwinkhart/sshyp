#compdef sshyp

sshyp_path="$HOME/.local/share/sshyp"
full_paths=("$sshyp_path"/**/*.gpg)
for scan_path in "${full_paths[@]}"; do
    trimmed_paths+=("${${scan_path#$sshyp_path}%????}")
done

case ${words[-2]} in
  sshyp )
    compadd $trimmed_paths
    ;;
  /* )
    compadd {add,gen,edit,copy,shear}
    ;;
  add )
    compadd {password,note,folder}
    ;;
  copy )
    compadd {password,username,url,note}
    ;;
  edit )
    compadd {password,username,url,note,relocate}
    ;;
  gen )
    compadd update
    ;;
esac
