from configparser import ConfigParser
from curses import A_REVERSE, KEY_DOWN, KEY_UP, curs_set, newwin
from curses.textpad import rectangle, Textbox
from os import environ, listdir, remove
from os.path import exists, expanduser, isfile
from pathlib import Path
from random import randint
from shutil import which
from subprocess import CalledProcessError, PIPE, run
# PORT START UNAME-IMPORT-STWEAK
from os import uname
# PORT END UNAME-IMPORT-STWEAK
home, sshyp_data, stdscr, gm_device_type = expanduser('~'), ConfigParser(interpolation=None), None, None
if isfile(f"{home}/.config/sshyp/sshyp.ini"):
    _exists_flag = True
    sshyp_data.read(f"{home}/.config/sshyp/sshyp.ini")
else:
    _exists_flag = False


# writes data stored in ConfigParser to the correct config file
def write_config(_sshyp_data=sshyp_data):
    with open(f"{home}/.config/sshyp/sshyp.ini", 'w') as configfile:
        _sshyp_data.write(configfile)


# creates a radio selection between the provided options
def curses_radio(_options, _pretext):
    curs_set(0)
    _selected = 0

    while True:
        # clear curses window
        stdscr.clear()
        # get terminal size
        _width = stdscr.getmaxyx()[1]
        # split text based on new lines
        _pretext_lines = _pretext.split('\n')

        # iterate through lines, splitting further (wrapping) as needed, to add to curses window
        _current_line = 0
        for _line in _pretext_lines:
            _remaining = _line
            while len(_remaining) > _width:
                stdscr.addstr(_current_line, 0, _remaining[:_width])
                _remaining = _remaining[_width:]
                _current_line += 1
            stdscr.addstr(_current_line, 0, _remaining)
            _current_line += 1

        # create user-interactive options
        for _i, _option in enumerate(_options):
            _y = _i + _current_line + 1
            if _i == _selected:
                stdscr.addstr(_y, 0, "[*] " + _option, A_REVERSE)
            else:
                stdscr.addstr(_y, 0, "[ ] " + _option)
        stdscr.refresh()

        # update _selected based on user input
        _key = stdscr.getch()
        if _key == KEY_UP:
            _selected = (_selected-1) % len(_options)
        elif _key == KEY_DOWN:
            _selected = (_selected+1) % len(_options)
        elif _key == ord('\n'):
            break
        stdscr.refresh()

    curs_set(1)
    return _selected


# creates a text-box input
def curses_text(_pretext):
    stdscr.clear()
    stdscr.addstr(0, 0, _pretext)
    _width = stdscr.getmaxyx()[1]
    _editwin = newwin(1, _width-2, 3, 1)
    rectangle(stdscr, 2, 0, 4, _width-1)
    stdscr.refresh()
    _box = Textbox(_editwin)
    # let the user edit until ctrl+g/enter is struck
    _box.edit()
    # return resulting contents
    return _box.gather().strip()


# device+sync type selection
def install_type():
    _offline_mode = 'false'
    # PORT START TWEAK-DEVTYPE
    _install_type = curses_radio(('client (ssh-synchronized)', 'client (offline)', 'server'),
                                 'device + sync type configuration')
    # PORT END TWEAK-DEVTYPE
    if _install_type == 2:
        _dev_type = 'server'
        Path(f"{home}/.config/sshyp/deleted").mkdir(mode=0o700, exist_ok=True)
        Path(f"{home}/.config/sshyp/whitelist").mkdir(mode=0o700, exist_ok=True)
        curses_radio(['okay'], 'make sure the ssh service is running and properly configured')
    else:
        _dev_type = 'client'
        if _install_type == 1:
            _offline_mode = 'true'
        if not sshyp_data.has_section('CLIENT-GENERAL'):
            sshyp_data.add_section('CLIENT-GENERAL')
        sshyp_data.set('CLIENT-GENERAL', 'offline_mode_enabled', _offline_mode)
    if not sshyp_data.has_section('GENERAL'):
        sshyp_data.add_section('GENERAL')
    sshyp_data.set('GENERAL', 'device_type', _dev_type)
    write_config()
    return _dev_type, _offline_mode


# gpg configuration
def gpg_config():
    # gpg key selection
    _uid_list = [_item for _item in run(('gpg', '-k', '--with-colons'),
                                        stdout=PIPE, text=True).stdout.splitlines() if _item.startswith('uid')]
    _named_uid_list = []
    for _uid in _uid_list:
        _named_uid_list.append(_uid.split(':')[9].replace('\\x3a', ':').replace('\\x5c', '\\'))
    _named_uid_list.append('auto-generate')
    _gpg_id_sel = curses_radio(_named_uid_list, 'gpg key selection')
    if _gpg_id_sel == len(_named_uid_list)-1:
        if not isfile(f"{home}/.config/sshyp/gpg-gen"):
            open(f"{home}/.config/sshyp/gpg-gen", 'w').writelines([
                'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
                'Name-Comment: gpg-sshyp\n', 'Name-Email: github.com/rwinkhart/sshyp\n',
                'Expire-Date: 0'])
        try:
            run(('gpg', '-q', '--batch', '--generate-key', f"{home}/.config/sshyp/gpg-gen"), stderr=PIPE, check=True)
        except CalledProcessError as e:
            if 'No pinentry' in e.stderr.decode("utf-8"):
                curses_radio(['okay'], 'either a valid pinentry program is missing or gpg is not configured to use an '
                                       'available pinentry program\n\nsshyp will now exit')
                from sys import exit as s_exit
                s_exit(6)
        remove(f"{home}/.config/sshyp/gpg-gen")
        _gpg_id = run(('gpg', '-k', '--with-colons'), stdout=PIPE, text=True).stdout.splitlines()[-1].split(':')[9]
    else:
        _gpg_id = _named_uid_list[_gpg_id_sel]

    # lock file generation
    if isfile(f"{home}/.config/sshyp/lock.gpg"):
        remove(f"{home}/.config/sshyp/lock.gpg")
    open(f"{home}/.config/sshyp/lock", 'w')
    run(('gpg', '-qr', _gpg_id, '-e', f"{home}/.config/sshyp/lock"))
    remove(f"{home}/.config/sshyp/lock")

    if not sshyp_data.has_section('CLIENT-GENERAL'):
        sshyp_data.add_section('CLIENT-GENERAL')
    sshyp_data.set('CLIENT-GENERAL', 'gpg_id', _gpg_id)
    write_config()


# text editor configuration
def editor_config(_env_mode):
    if _env_mode:
        # set default text editor to value of EDITOR environment variable, otherwise default to vi
        if 'EDITOR' in environ:
            _editor = environ['EDITOR']
        else:
            _editor = 'vi'
    else:
        _editor = curses_text('enter the name of your preferred text editor:\n\n\n\n\n(ctrl+g/enter to confirm)'
                              '\n\nthis will be used for writing notes\n\nexample input: vim')
    if not sshyp_data.has_section('CLIENT-GENERAL'):
        sshyp_data.add_section('CLIENT-GENERAL')
    sshyp_data.set('CLIENT-GENERAL', 'text_editor', _editor)
    write_config()


# ssh+sshync configuration
def ssh_config():
    # private key selection/generation
    _keys = []
    # ensure ~/.ssh directory exists
    Path(f"{home}/.ssh").mkdir(mode=0o700, exist_ok=True)
    for _file in listdir(f"{home}/.ssh"):
        if not _file.startswith('.') and _file not in ('known_hosts', 'known_hosts.old', 'authorized_keys') \
                and not _file.endswith('.pub') and isfile(f"{home}/.ssh/{_file}"):
            _keys.append(f"{home}/.ssh/{_file}")
    _keys.extend(['auto-generate', 'other (type the location)'])
    _key_selected_num = curses_radio(_keys, 'which private ssh key would you like to use for sshyp?')
    _gen_index = len(_keys)-2
    if _key_selected_num >= _gen_index:
        _ssh_key = expanduser(curses_text('enter the location for your private ssh key:\n\n\n\n\n(ctrl+g/enter to '
                                          'confirm)\n\nexample input:\n\n~/.ssh/privkey'))
        if _key_selected_num == _gen_index:
            _passphrase = curses_text('enter your desired ssh keyfile passphrase:\n\n\n\n\n(ctrl+g/enter to confirm)'
                                      '\n\ntip: you can leave this blank to use the keyfile without a passphrase')
            run(('ssh-keygen', '-q', '-t', 'ed25519', '-N', _passphrase, '-f', _ssh_key))
    else:
        _ssh_key = _keys[_key_selected_num]
    
    # ssh+sshync configuration
    _uiport = curses_text('enter the username, ip, and ssh port of your sshyp server:\n\n\n\n\n(ctrl+g/enter to '
                          'confirm)\n\nexample inputs:\n\n ipv4: user@10.10.10.10:22\n ipv6: user@[2000:2000:2000:2000'
                          ':2000:2000:2000:2000]:22\n domain: user@mydomain.com:22')
    _uiport_split = _uiport.split('@')
    _username_ssh = _uiport_split[0]
    _iport = _uiport_split[1].lstrip('[').replace(']', '').rsplit(':', 1)

    if not sshyp_data.has_section('SSHYNC'):
        sshyp_data.add_section('SSHYNC')
    sshyp_data.set('SSHYNC', 'user', _username_ssh)
    sshyp_data.set('SSHYNC', 'ip', _iport[0])
    sshyp_data.set('SSHYNC', 'port', _iport[1])
    sshyp_data.set('SSHYNC', 'local_dir', f"{home}/.local/share/sshyp/")
    sshyp_data.set('SSHYNC', 'remote_dir', f"/home/{_username_ssh}/.local/share/sshyp/")
    sshyp_data.set('SSHYNC', 'identity_file', _ssh_key)
    write_config()
    return _iport[1], _username_ssh, _iport[0], _ssh_key


# device id configuration
def dev_id_config(_ip, _username_ssh, _port, _identity):
    from sshyp import copy_id_check, string_gen
    _device_id_prefix = curses_text('name this device:\n\n\n\n\n(ctrl+g/enter to confirm)\n\nimportant: this '
                                    'id must be unique amongst your client devices\n\nthis is used to keep track of '
                                    'database syncing and quick-unlock permissions\n')
    _device_id_suffix = string_gen('f', randint(24, 48))
    _device_id = _device_id_prefix + '-' + _device_id_suffix
    # remove existing device ids
    for _id in listdir(f"{home}/.config/sshyp/devices"):
        remove(f"{home}/.config/sshyp/devices/{_id}")
    open(f"{home}/.config/sshyp/devices/{_device_id}", 'w')
    # test server connection and attempt to register device id
    copy_id_check(_ip, _username_ssh, _port, _device_id, _identity, sshyp_data)


# quick-unlock configuration
def quick_unlock_config(_default):
    if _default:
        _enabled = 'false'
    else:
        _quick_unlock_sel = curses_radio(('no', 'yes'), 'WARNING: quick-unlock is only as secure as the environment you'
                                                        ' use it in\n\nquick-unlock allows you to use a shorter version'
                                                        ' of your gpg key passphrase and\nrequires a constant '
                                                        'connection to your sshyp server to authenticate\n\na '
                                                        'compromised program on your computer could scan the process '
                                                        'list in the\nbrief period during decryption to retrieve the '
                                                        'necessary information to decrypt your entries\n\nenable '
                                                        'quick-unlock?')
        if _quick_unlock_sel == 1:
            _enabled = 'true'
        else:
            _enabled = 'false'
    if not sshyp_data.has_section('CLIENT-ONLINE'):
        sshyp_data.add_section('CLIENT-ONLINE')
    sshyp_data.set('CLIENT-ONLINE', 'quick_unlock_enabled', _enabled)
    write_config()
    return _enabled


# re-encrypt/optimize all entries
def refresh_encryption():
    _directory = f"{home}/.local/share/sshyp"

    # warn the user of potential data loss and prompt to continue
    _proceed = curses_radio(('no', 'yes'), "WARNING: proceeding with this action will remove/overwrite any directories"
                                           f" matching the following:\n\n{home}/.local/share/sshyp.old\n{home}/.local/"
                                           "share/sshyp.new\n\nare you sure you wish to re-encrypt all entries?")
    if _proceed != 1:
        return 3    

    # set new gpg key
    gpg_config()

    from os import walk
    from os.path import isdir
    from shutil import move, rmtree
    from sshyp import decrypt, encrypt

    # prompt for unlock and display do not close warning
    decrypt(None)
    curses_radio(['okay'], 'entry optimization may take some time - select "okay" to start - '
                           'do not terminate this process!')

    # remove existing conflicts
    for _extension in ('.new', '.old'):
        if exists(f"{_directory}{_extension}"):
            rmtree(f"{_directory}{_extension}")
    
    # decrypt, optimize, and re-encrypt each entry with the newly selected key
    if isdir(_directory):
        _gpg_id = sshyp_data.get('CLIENT-GENERAL', 'gpg_id')
        for _root, _dirs, _files in sorted(walk(_directory, topdown=True)):
            for _filename in _files:
                Path(_root.replace(_directory, _directory + '.new', 1)).mkdir(0o700, parents=True, exist_ok=True)
                encrypt(decrypt(f"{_root}/{_filename[:-4]}"),
                        f"{_root.replace(_directory, _directory + '.new', 1)}/{_filename[:-4]}", _gpg_id)

        # create a backup of the original version and activate the new version        
        move(_directory, _directory + '.old')
        move(_directory + '.new', _directory)
        return 1
    else:
        return 2
    

# PORT START WHITELIST-SERVER
# takes input from the user to set up quick-unlock pin
def whitelist_setup():
    _gpg_password_temp = str(curses_text('full gpg passphrase:\n\n\n\n\n(ctrl+g/enter to confirm)'))
    _half_length = int(len(_gpg_password_temp)/2)
    try:
        _short_password_length = int(curses_text(f"quick unlock pin length ({_half_length}):\n\n\n\n\n(ctrl+g/enter "
                                                 "to confirm)\n\npin must be half the length of the gpg passphrase "
                                                 "or less\n\ncannot be a negative number"))
        if not 0 <= _short_password_length <= _half_length:
            _short_password_length = _half_length
    except ValueError:
        _short_password_length = _half_length
    _i, _quick_unlock_password, _quick_unlock_password_excluded = 0, '', ''
    for _char in _gpg_password_temp:
        if _i % 2 == 1 and _i < _short_password_length*2:
            _quick_unlock_password += _char
        else:
            _quick_unlock_password_excluded += _char
        _i += 1

    # create assembly key
    open(f"{home}/.config/sshyp/gpg-gen", 'w').writelines([
        'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
        'Name-Comment: gpg-sshyp-whitelist\n', 'Name-Email: github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
    run(('gpg', '-q', '--pinentry-mode', 'loopback', '--batch', '--generate-key', '--passphrase',
         _quick_unlock_password, f"{home}/.config/sshyp/gpg-gen"))
    remove(f"{home}/.config/sshyp/gpg-gen")
    _gpg_id = run(('gpg', '-k', '--with-colons'), stdout=PIPE, text=True).stdout.splitlines()[-1].split(':')[9]

    # encrypt excluded with the assembly key
    from sshyp import encrypt
    encrypt(_quick_unlock_password_excluded, f"{home}/.config/sshyp/excluded", _gpg_id)
    curses_radio(['okay, I have it memorized'], f"your quick-unlock pin: {_quick_unlock_password}")


# adds or removes quick-unlock whitelisted device ids
def whitelist_manage(_action):
    _whitelisted_ids = listdir(f"{home}/.config/sshyp/whitelist")
    _device_ids = listdir(f"{home}/.config/sshyp/devices")

    # a value of True indicates adding
    if _action:
        _unwhitelisted_ids = []    
        for _id in _device_ids:
            if _id not in _whitelisted_ids:
                _unwhitelisted_ids.append(_id)
        _unwhitelisted_ids.append('cancel')
        _add_id = curses_radio(_unwhitelisted_ids, 'id to add to whitelist:')
        if _add_id == len(_unwhitelisted_ids)-1:
            return
        open(f"{home}/.config/sshyp/whitelist/{_unwhitelisted_ids[_add_id]}", 'w').write('')
    else:
        _whitelisted_choices = _whitelisted_ids + ['cancel']
        _del_id = curses_radio(_whitelisted_choices, 'id to remove from whitelist:')
        if _del_id == len(_whitelisted_choices)-1:
            return
        remove(f"{home}/.config/sshyp/whitelist/{_whitelisted_ids[_del_id]}")

    # prune deleted device ids from whitelist
    for _id in _whitelisted_ids:
        if _id not in _device_ids:
            remove(f"{home}/.config/sshyp/whitelist/{_id}")


# runs quick-unlock configuration menu
def whitelist_menu():
    while True:
        _choice = curses_radio(('setup/create pin', 'add to whitelist', 'remove from whitelist', 
                                'BACK'), 'quick-unlock/whitelist management')
        if _choice == 0:
            whitelist_setup()
        elif _choice == 1:
            whitelist_manage(True)
        elif _choice == 2:
            whitelist_manage(False)
        else:
            break
# PORT END WHITELIST-SERVER


# PORT START TWEAK-EXTEND-FUNCTIONS
# downloads/updates extensions
def extension_downloader():
    from os import chmod
    from tempfile import gettempdir
    from urllib.request import urlopen, urlretrieve
    # the version listed below will NOT always match the version of sshyp being used
    # it is only updated if new extensions are incompatible with previous sshyp versions
    _file_data = urlopen("https://raw.githubusercontent.com/rwinkhart/sshyp-labs/main/pointers/v1.5.2").read()
    _pointer = ConfigParser(interpolation=None)
    _pointer.read_string(_file_data.decode('utf-8'))
    _extensions = _pointer.sections()
    _extensions.append('CANCEL')
    _choice = curses_radio(_extensions, 'select an extension for more info')
    if _choice == len(_extensions)-1:
        return False
    _selected = _extensions[_choice]
    _divider = (stdscr.getmaxyx()[1])*'-'
    _choice = curses_radio(('no', 'yes'), '/description/\n' + _divider + '\n\n' + _pointer.get(_selected, 'desc') +
                           '\n\n/usage/\n' + _divider + '\n\n' + _pointer.get(_selected, 'usage').replace('<br>', '\n')
                           + '\n\n' + _divider + '\n\ninstall ' + _selected + '?')
    # if installing the extension...
    if _choice == 1:
        # download extension files to temporary directory
        _exe_dir, _ini_dir = f"{gettempdir()}/sshyp_exe", f"{gettempdir()}/sshyp_ini"
        _ext_exe = urlretrieve(_pointer.get(_selected, 'exe'), _exe_dir)
        _ext_ini = urlretrieve(_pointer.get(_selected, 'ini'), _ini_dir)
        # set permissions under active user
        chmod(_exe_dir, 0o755)
        chmod(_ini_dir, 0o644)
        return _selected
    return False


# uninstalls/deletes selected extensions
def extension_remover():
    _installed = []
    for _extension in listdir('/usr/lib/sshyp/extensions'):
        _installed.append(_extension[:-4])
    _installed.append('CANCEL')
    _choice = curses_radio(_installed, 'select an extension to uninstall')
    if _choice == len(_installed)-1:
        return False
    _sure = curses_radio(('no', 'yes'), f"are you sure you want to remove {_installed[_choice]}?")
    if _sure == 0:
        return False
    return _installed[_choice]


# provides options for managing extensions
def extension_menu():
    _ext_name, _action = False, False
    # determine which of the supported privilege escalation utilities is installed
    if which('doas') is not None:
        _escalator = 'doas'
    elif which('sudo') is not None:
        _escalator = 'sudo'
    else:
        # throw an error if no supported privilege escalation utility is found
        raise ChildProcessError
    while True:
        _choice = curses_radio(('download/update extensions', 'remove extensions', 'BACK'), 'extension management')
        if _choice == 0:
            _ext_name = extension_downloader()
            if _ext_name:
                # True represents installation
                _action = True
                break
        elif _choice == 1:
            _ext_name = extension_remover()
            if _ext_name:
                break
        else:
            break
    return _ext_name, _escalator, _action
# PORT END TWEAK-EXTEND-FUNCTIONS


# runs secondary configuration menu
def global_menu(_scr, _device_type, _top_message):
    global stdscr
    # only set global stdscr if running as entry point
    if not isinstance(_scr, bool):
        stdscr = _scr

    while True:
        _options, _choice, _exit_signal = ['change device/synchronization types'], 0, False
        if _device_type == 'client':
            _options.extend(['change gpg key', 're-configure ssh(ync)', 'change device name',
                             '[OPTIONAL, RECOMMENDED] set custom text editor',
                             '[OPTIONAL] enable/disable quick-unlock',
                             '[OPTIONAL] re-encrypt/optimize entries',
                             '[OPTIONAL] extension management'])
        else:
            _options.extend(['manage quick-unlock/whitelist'])
        _options.extend(['EXIT/DONE'])
        _choice += curses_radio(_options, _top_message)

        if _choice == 0:
            _dev_sync_types = install_type()
            # if switching to client mode...
            if _dev_sync_types[0] == 'client':
                # ...and gpg settings are missing
                if not sshyp_data.has_option('CLIENT-GENERAL', 'gpg_id'):
                    gpg_config()
                # ...and text editor settings are missing
                if not sshyp_data.has_option('CLIENT-GENERAL', 'text_editor'):
                    editor_config(True)
                # ...and online (synced) mode is enabled...
                if _dev_sync_types[1] == 'false':
                    # ...and quick-unlock settings are missing
                    if not sshyp_data.has_option('CLIENT-ONLINE', 'quick_unlock_enabled'):
                        quick_unlock_config(True)
                    # set to None to check if modified later
                    _ip, _username_ssh, _port, _identity = None, None, None, None
                    # ...and there is no sshync config present
                    if not sshyp_data.has_section('SSHYNC'):
                        _ip, _username_ssh, _port, _identity = ssh_config()
                    # ...and there is no device ID present
                    if not listdir(f"{home}/.config/sshyp/devices"):
                        if None in (_ip, _username_ssh, _port):
                            _ip, _username_ssh, _port, _identity = ssh_config()
                        dev_id_config(_ip, _username_ssh, _port, _identity)
                    # ...or ssh_error is missing
                    elif not sshyp_data.has_option('CLIENT-ONLINE', 'ssh_error'):
                        sshyp_data.set('CLIENT-ONLINE', 'ssh_error', '1')    
                        write_config()
            _device_type = _dev_sync_types[0]
        elif _choice == 1:
            if _device_type == 'client':
                gpg_config()
            else:
                whitelist_menu()
        elif _choice == 2:
            if _device_type == 'client':
                ssh_config()
            else:
                _exit_signal = True
        elif _choice == 3:
            if not sshyp_data.has_section('SSHYNC'):
                ssh_config()
            dev_id_config(sshyp_data.get('SSHYNC', 'ip'), sshyp_data.get('SSHYNC', 'user'),
                          sshyp_data.get('SSHYNC', 'port'), sshyp_data.get('SSHYNC', 'identity_file'))
        elif _choice == 4:
            editor_config(False)
        elif _choice == 5:
            _enabled = quick_unlock_config(False)
            if _enabled == 'true':
                curses_radio(['okay'], 'quick-unlock has been enabled client-side - in order for this feature to '
                                       'function,\nyou must first log in to the sshyp server and run:\n\nsshyp tweak\n'
                                       '\nfrom there you can create a quick-unlock pin and add this device to the '
                                       'whitelist')
        elif _choice == 6:
            _success = refresh_encryption()
            if _success == 1:
                curses_radio(['okay'], "a backup of your previous entry directory has been created:\n\n"
                                       f"{home}/.local/share/sshyp.old")
            elif _success == 2:
                curses_radio(['okay'], '\u001b[38;5;9merror: re-encryption failed: entry directory not found\u001b[0m')
        elif _choice == 7:
            # PORT START TWEAK-EXTEND-OPTION
            _ext_name, _escalator, _action = extension_menu()
            # if root is needed for extension management...
            if _ext_name:
                return _ext_name, _escalator, _action
            # PORT END TWEAK-EXTEND-OPTION
        else:
            _exit_signal = True
        if _exit_signal:
            break
    return None, None, None


# runs initial configuration wizard
def initial_setup(_scr):
    global stdscr
    stdscr = _scr

    # required directory creation
    Path(f"{home}/.config/sshyp/devices").mkdir(mode=0o700, parents=True, exist_ok=True)
    Path(f"{home}/.local/share/sshyp").mkdir(mode=0o700, parents=True, exist_ok=True)

    # removal of old config files
    if _exists_flag:
        sshyp_data.clear()

    # curses menu tree
    # device+sync type selection
    _dev_sync_types = install_type()

    if _dev_sync_types[0] == 'client':

        # gpg configuration
        gpg_config()

        # text editor configuration (automated)
        editor_config(True)

        # quick-unlock configuration (disabled by default)
        quick_unlock_config(True)

        # online (synchronized mode) configuration
        if _dev_sync_types[1] != 'true':

            # ssh+sshync configuration
            _ip, _username_ssh, _port, _identity = ssh_config()

            # device id configuration
            dev_id_config(_ip, _username_ssh, _port, _identity)

        # PORT START CLIPTOOL
        # check for clipboard tool and display warning if missing
        if uname()[0] in ('Linux', 'FreeBSD') and 'WSL_DISTRO_NAME' not in environ \
                and not exists("/data/data/com.termux"):
            _display_server, _clipboard_tool, _clipboard_package = None, None, None
            if 'WAYLAND_DISPLAY' in environ:
                _display_server, _clipboard_tool, _clipboard_package = 'Wayland', 'wl-copy', 'wl-clipboard'
            elif 'DISPLAY' in environ:
                _display_server, _clipboard_tool, _clipboard_package = 'X11', 'xclip', 'xclip'
            if _display_server is not None and which(_clipboard_tool) is None:
                curses_radio(['okay'], f'WARNING: you are using {_display_server} and "{_clipboard_tool}" is not '
                                       'present - \ncopying entry fields will not function until '
                                       f'"{_clipboard_package}" is installed')
        # PORT END CLIPTOOL

    # run optional configuration menu
    curses_radio(['okay'], 'required configuration complete\n\na menu for additional (optional) configuration will be '
                           'displayed\n\nthis menu can be safely exited at any time')

    # set gm_device_type so that after the init menu is terminated the global menu knows the device type
    global gm_device_type
    gm_device_type = _dev_sync_types[0]
    return


# runs the specified entry function (menu start point) within a curses wrapper
def wrapped_entry(_gm_device_type, _gm_top_message='configuration options:'):
    from curses import wrapper, use_default_colors

    global gm_device_type
    gm_device_type = _gm_device_type

    # a boolean value represents init
    if isinstance(gm_device_type, bool):
        wrapper(lambda _wrap_stdscr: (use_default_colors(), initial_setup(_wrap_stdscr)))
    # any other value will be interpreted as the global menu device type
    # this code still runs when called for init once the init menu terminates
    _repeat = True
    while _repeat:
        try:
            _ext_name, _escalator, _action = \
                wrapper(lambda _wrap_stdscr: (use_default_colors(),
                                              global_menu(_wrap_stdscr, gm_device_type, _gm_top_message)))[1]
        except ChildProcessError:
            print("\n\u001b[38;5;9merror: privilege escalation required\n\nneither 'doas' nor 'sudo' were found in "
                  "the system's $PATH\u001b[0m\n")
            return
        # only run if privilege escalation is needed
        if _action is not None:
            if _action:
                # install with privilege escalation (outside of curses)
                from tempfile import gettempdir
                _exe_dir, _ini_dir = f"{gettempdir()}/sshyp_exe", f"{gettempdir()}/sshyp_ini"
                run((_escalator, 'chown', 'root:root', _exe_dir, _ini_dir))
                run((_escalator, 'mv', _exe_dir, f"/usr/lib/sshyp/{_ext_name}"))
                run((_escalator, 'mv', _ini_dir, f"/usr/lib/sshyp/extensions/{_ext_name}.ini"))
            else:
                # uninstall with privilege escalation (outside of curses)
                run((_escalator, 'rm', f"/usr/lib/sshyp/{_ext_name}",
                     f"/usr/lib/sshyp/extensions/{_ext_name}.ini"))
        else:
            _repeat = False
