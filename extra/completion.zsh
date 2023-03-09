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
    compadd {add,edit,copy,gen,shear}
    ;;
  add )
    compadd {folder,note,password}
    ;;
  copy )
    compadd {note,password,url,username}
    ;;
  edit )
    compadd {note,password,relocate,url,username}
    ;;
  gen )
    compadd update
    ;;
esac
