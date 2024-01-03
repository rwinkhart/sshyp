#!/usr/bin/env python3
from configparser import ConfigParser, NoOptionError, NoSectionError
from os import chmod, environ, listdir, walk
from os.path import expanduser, isdir, isfile, realpath
from pathlib import Path
from shutil import move
from sshync import delete as offline_delete, run_profile
from subprocess import CalledProcessError, DEVNULL, PIPE, run
from sys import argv, exit as s_exit
# PORT START UNAME-IMPORT-SSHYP
from os import uname
# PORT END UNAME-IMPORT-SSHYP
home = expanduser('~')


# UTILITY FUNCTIONS

# generates and prints full entry list
def entry_list_gen(_directory=f"{home}/.local/share/sshyp/"):
    from shutil import get_terminal_size
    _ran, _width = False, get_terminal_size().columns
    print("\nfor a list of usable commands, run 'sshyp help'\n\n\u001b[38;5;0;48;5;15msshyp entries:\u001b[0m", end='')
    for _root, _dirs, _files in sorted(walk(_directory, topdown=True)):
        _color_alternator = 1
        if _ran:
            print(f"\n\n\u001b[38;5;7;48;5;8m{_root.replace(f'{home}/.local/share/sshyp', '', 1)}/\u001b[0m")
        _char_counter = 0
        for _filename in sorted(_files):
            if _color_alternator > 0:
                _print_string = _filename[:-4]
            else:
                _print_string = f"\u001b[38;5;8m{_filename[:-4]}\u001b[0m"
            # -3 instead of -4 to account for trailing space character
            _char_counter += len(_filename)-3
            if _char_counter >= _width:
                # reset _char_counter to length of first entry in new line
                _char_counter = len(_filename)-3
                print()
            print(_print_string + ' ', end='')
            _color_alternator = _color_alternator * -1
        if _ran and _char_counter < 1:
            print('\u001b[38;5;9m-empty directory-\u001b[0m', end='')
        _ran = True
    print('\n')


# displays the contents of an entry in a readable format
def entry_reader(_decrypted_entry):
    _notes_flag = 0
    if pass_show:
        _entry_password = f'\u001b[38;5;10m{_decrypted_entry[0]}\u001b[0m'
    else:
        _entry_password = f'\u001b[38;5;3mend command in "--show" or "-s" to view\u001b[0m'
    print()
    for _num in range(len(_decrypted_entry)):
        try:
            if _num == 0 and _decrypted_entry[1] != '':
                print(f"\u001b[38;5;7;48;5;8musername:\u001b[0m\n{_decrypted_entry[1]}\n")
            elif _num == 1 and _decrypted_entry[0] != '':
                print(f"\u001b[38;5;7;48;5;8mpassword:\u001b[0m\n{_entry_password}\n")
            elif _num == 2 and _decrypted_entry[2] != '':
                print(f"\u001b[38;5;7;48;5;8murl:\u001b[0m\n{_decrypted_entry[_num]}\n")
            elif _num >= 3 and _decrypted_entry[_num] != '' and _notes_flag != 1:
                _notes_flag = 1
                print('\u001b[38;5;7;48;5;8mnotes:\u001b[0m\n' + _decrypted_entry[_num])
            elif _num >= 3 and _notes_flag == 1:
                print(_decrypted_entry[_num])
            if _notes_flag == 1:
                try:
                    _line_test = _decrypted_entry[_num + 1]
                except IndexError:
                    print()
        except IndexError:
            if _num == 0 and _decrypted_entry[0] != '':
                print(f"\u001b[38;5;7;48;5;8mpassword:\u001b[0m\n{_entry_password}\n")


# generates and returns a random string based on input
def string_gen(_complexity, _length):
    from random import SystemRandom
    import string
    if _complexity == 's':
        _character_pool = string.ascii_letters + string.digits
    elif _complexity == 'f':
        _character_pool = string.digits + string.ascii_letters + string.punctuation.replace('/', '').replace('\\', '')\
            .replace("'", '').replace('"', '').replace('`', '').replace('~', '')
    else:
        _character_pool = string.digits + string.ascii_letters + string.punctuation
    _min_special, _special = round(.2 * _length), 0
    while True:
        _gen = ''.join(SystemRandom().choice(_character_pool) for _ in range(_length))
        for _character in _gen:
            if not _character.isalpha():
                _special += 1
        if _special >= _min_special:
            break
    return _gen


# prompts the user for necessary information to generate a password and passes it to string_gen
def pass_gen():
    _length = 9
    while True:
        try:
            _length = int(input('\npassword length: '))
        except ValueError:
            continue
        else:
            if _length < 1:
                continue
            else:
                break
    _complexity = str(input('\npassword complexity - simple (for compatibility) or complex (for security)? (s/C) '))
    if _complexity not in ('s', 'S'):
        _complexity = 'c'
    _gen = string_gen(_complexity.lower(), _length)
    return _gen


# creates a temporary file to allow notes to be edited by standard editors
def edit_note(_note_lines, _exit_on_match=False):
    from tempfile import NamedTemporaryFile
    _joined_note_lines = '\n'.join(_note_lines)
    with NamedTemporaryFile(mode='w+') as _tmp:
        _tmp.write(_joined_note_lines)
        _tmp.seek(0)
        try:
            run((editor, _tmp.name))
        except FileNotFoundError:
            print(f"\n\u001b[38;5;9merror: the configured text editor ({editor}) cannot be found on this system\n\n"
                  f"please either install the editor or re-configure the active editor using 'sshyp tweak'\u001b[0m\n")
        _tmp.seek(0)
        _new_note = _tmp.read().rstrip()
    if _exit_on_match and _joined_note_lines == _new_note:
        s_exit(0)
    return _new_note


# encrypts an entry and cleans up the temporary files
def encrypt(_entry_data, _entry_dir, _gpg_id):
    _bytes_data = '\n'.join(_entry_data).rstrip().encode()
    _encrypted_data = run(('gpg', '-qr', str(_gpg_id), '-e'), input=_bytes_data, stdout=PIPE).stdout
    open(_entry_dir + '.gpg', 'wb').write(_encrypted_data)


# decrypts an entry to a temporary directory
def decrypt(_entry_dir, _quick_verify=None, _quick_pass=None):
    _contents = None

    # check quick-unlock status, fetch passphrase
    if _quick_verify:
        _quick_pass = whitelist_verify(port, username_ssh, ip, client_device_id, identity)
    else:
        if _quick_pass is None:
            _quick_pass = False

    # set decryption method based on quick-unlock availability
    if not isinstance(_quick_pass, bool):
        _cmd = ['gpg', '--pinentry-mode', 'loopback', '--passphrase', _quick_pass, '-qd']
    else:
        _cmd = ['gpg', '-qd']

    # set decryption target based on lock file availability
    if _entry_dir is None:
        _dec_target = [f"{home}/.config/sshyp/lock.gpg"]
    else:
        _dec_target = [f"{_entry_dir}.gpg"]

    # run decryption command
    try:
        _contents = run(_cmd + _dec_target, stderr=DEVNULL, stdout=PIPE, text=True, check=True).stdout
    except CalledProcessError:
        if not isinstance(_quick_pass, bool):
            print('\n\u001b[38;5;9merror: quick-unlock failed as a result of an incorrect passphrase, an unreachable '
                  'sshyp server, or an invalid configuration\n\nfalling back to standard unlock\u001b[0m\n')
            try:
                _contents = run(['gpg', '-qd'] + _dec_target, stderr=DEVNULL, stdout=PIPE, text=True, check=True).stdout
            except CalledProcessError:
                print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
                s_exit(4)
        else:
            print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
            s_exit(4)
    return _contents.rstrip().split('\n')


# checks the user's whitelist status and fetches the full gpg key password if possible
def whitelist_verify(_port, _username_ssh, _ip, _client_device_id, _identity):
    try:
        run(('gpg', '--pinentry-mode', 'cancel', '-qd', '--output', '/dev/null',
             f"{home}/.config/sshyp/lock.gpg"), stderr=DEVNULL, check=True)
        return False
    except CalledProcessError:
        _i, _full_password = 0, ''
        _server_whitelist = run(('ssh', '-i', _identity, '-p', _port, f"{_username_ssh}@{_ip}",
                                 f'python3 -c \'from os import listdir; print(*listdir("/home/{_username_ssh}'
                                 f'/.config/sshyp/whitelist"))\''), stdout=PIPE, text=True).stdout.rstrip().split()
        for _device_id in _server_whitelist:
            if _device_id == _client_device_id:
                from getpass import getpass
                _quick_unlock_password = getpass(prompt='\nquick-unlock pin: ')
                _quick_unlock_password_excluded = \
                    run(('ssh', '-i', _identity, '-p',  _port, f"{_username_ssh}@{_ip}",
                         f"gpg --pinentry-mode loopback --passphrase '{_quick_unlock_password}' "
                         f"-qd ~/.config/sshyp/excluded.gpg"), stdout=PIPE, text=True).stdout.rstrip()
                while _i < len(_quick_unlock_password_excluded):
                    try:
                        _full_password += _quick_unlock_password_excluded[_i]
                    except IndexError:
                        pass
                    try:
                        _full_password += _quick_unlock_password[_i]
                    except IndexError:
                        pass
                    _i += 1
                break
    return _full_password


# returns True if expected and reality align, otherwise error
def target_exists_check(_target_name, _expected_presence):
    if isfile(f"{directory}{_target_name}.gpg") or isdir(f"{directory}{_target_name}"):
        if _expected_presence:
            return True
        else:
            print(f"\n\u001b[38;5;9merror: (/{_target_name}) already exists\u001b[0m\n")
            s_exit(3)
    else:
        if not _expected_presence:
            return True
        else:
            print(f"\n\u001b[38;5;9merror: (/{_target_name}) does not exist\u001b[0m\n")
            s_exit(2)
        

# returns target type (entry == True, folder == False, null == None), optional errors
def target_type_check(_target_name, _expected_type=True, _error=False):
    if isfile(f"{directory}{_target_name}.gpg"):
        if _error and not _expected_type:
            print(f"\n\u001b[38;5;9merror: (/{_target_name}) is an entry\u001b[0m\n")
            s_exit(2)
        return True
    elif isdir(f"{directory}{_target_name}"):
        if _error and _expected_type:
            print(f"\n\u001b[38;5;9merror: (/{_target_name}) is a folder\u001b[0m\n")
            s_exit(2)
        return False
    else:
        print(f"\n\u001b[38;5;9merror: (/{_target_name}) does not exist\u001b[0m\n")
        s_exit(2)


# ensures an edited entry is optimized for best compatibility
def line_edit(_lines, _edit_data, _edit_line):
    # ensure enough lines are present for edited field
    while len(_lines) < _edit_line + 1:
        _lines.append('')
    # write the edited field
    _lines[_edit_line] = _edit_data.rstrip()
    return _lines


# attempts to connect to the user's server via ssh to register the device for syncing
def copy_id_check(_port, _username_ssh, _ip, _client_device_id, _identity, _sshyp_data):
    from stweak import write_config
    if not _sshyp_data.has_section('CLIENT-ONLINE'):
        _sshyp_data.add_section('CLIENT-ONLINE')
    try:
        run(('ssh', '-o', 'ConnectTimeout=3', '-i', _identity, '-p', _port, f"{_username_ssh}@{_ip}",
             f'python3 -c \'from pathlib import Path; Path("/home/{_username_ssh}/.config/sshyp/devices/'
             f'{_client_device_id}").touch(mode=0o400, exist_ok=True)\''), stderr=DEVNULL, check=True)
    except CalledProcessError:
        print(f'\n\u001b[38;5;9mwarning: ssh connection could not be made - ensure the public key ({_identity}) is '
              'registered on the remote server and that the entered ip, port, and username are correct\n\nsyncing '
              'functionality will be disabled until this is addressed\u001b[0m\n')
        _sshyp_data.set('CLIENT-ONLINE', 'ssh_error', 'true')
        write_config(_sshyp_data)
        return True
    _sshyp_data.set('CLIENT-ONLINE', 'ssh_error', 'false')
    write_config(_sshyp_data)
    return False


# ARGUMENT-SPECIFIC FUNCTIONS

# prints help text based on argument
def print_info():
    if arguments[0] in ('version', '-v'):
        _blank = '\u001b[38;5;7;48;5;8m\\\u001b[38;5;15;48;5;15m' + 55*' ' + '\u001b[38;5;7;48;5;8m/\u001b[0m'
        _border = '\u001b[38;5;7;48;5;8m' + 14*'<>' + '-' + 14*'<>' + '\u001b[0m\n'
        print(f"""\nsshyp is a simple, self-hosted, sftp-synchronized\npassword manager for unix(-like) systems\n
{9*' '}..{15*' '}\u001b[38;5;12m♥♥ \u001b[38;5;9m♥♥\u001b[0m{15*' '}..
{8*' '}/()\\''.''.{7*' '}\u001b[38;5;12m♥♥♥\u001b[0m♥♥♥♥\u001b[0m{7*' '}.''.''/()\\{3*' '}_)
{5*' '}_.{3*' '}:{7*' '}*{7*' '}\u001b[38;5;9m♥♥♥♥♥\u001b[0m{7*' '}*{7*' '}:{3*' '}<[◎]|_|=
 }}-}}-*]{4*' '}`..'..'{9*' '}\u001b[0m♥♥♥\u001b[0m{9*' '}`..'..'{6*' '}|
{4*' '}◎-◎{4*' '}//{3*' '}\\\\{10*' '}\u001b[38;5;9m♥\u001b[0m{10*' '}//{3*' '}\\\\{5*' '}/|\\""")
        print(f"{_border}{_blank}\n\u001b[38;5;7;48;5;8m\\\u001b[38;5;15;48;5;15m{18*' '}\u001b[38;5;15;48;5;8msshyp "
              f"version 1.5.2\u001b[38;5;15;48;5;15m{18*' '}\u001b[38;5;7;48;5;8m/\u001b[0m")
        print(f"\u001b[38;5;7;48;5;8m\\\u001b[38;5;15;48;5;15m{14*' '}\u001b[38;5;15;48;5;8mthe fortified flock"
              f" update\u001b[38;5;15;48;5;15m{15*' '}\u001b[38;5;7;48;5;8m/\u001b[0m\n{_blank}")
        print(f"\u001b[38;5;7;48;5;8m\\\u001b[38;5;15;48;5;15m{9*' '}\u001b[38;5;15;48;5;8mcopyright 2021-2024 ", 
              f"randall winkhart\u001b[38;5;15;48;5;15m{9*' '}\u001b[38;5;7;48;5;8m/\u001b[0m")
        print(f"{_blank}\n{_border}\nsee https://github.com/rwinkhart/sshyp for more information\n")
    elif arguments[0] == 'license':
        print('\nThis program is free software: you can redistribute it and/or modify it under the terms of\nversion 3 '
              '(only) of the GNU General Public License as published by the Free Software Foundation.\n\nThis program '
              'is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;\nwithout even the implied '
              'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\nSee the GNU General Public License '
              'for more details:\nhttps://opensource.org/licenses/GPL-3.0\n')
    elif arguments[0] == 'add' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp /<entry name> add <option>\u001b[0m\n
\u001b[1moptions:\u001b[0m
 add:
  password/-p{12*' '}add a password entry
  note/-n{16*' '}add a note entry
  folder/-f{14*' '}add a new folder for entries\n""")
    elif arguments[0] == 'edit' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp /<entry name> edit <option>\u001b[0m\n
\u001b[1moptions:\u001b[0m
 edit:
  rename/relocate/-r{5*' '}rename or relocate an entry
  username/-u{12*' '}change the username of an entry
  password/-p{12*' '}change the password of an entry
  url/-l{17*' '}change the url attached to an entry
  note/-n{16*' '}change the note attached to an entry\n""")
    elif arguments[0] == 'copy' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp /<entry name> copy <option>\u001b[0m\n
\u001b[1moptions:\u001b[0m
 copy:
  username/-u{12*' '}copy the username of an entry to your clipboard
  password/-p{12*' '}copy the password of an entry to your clipboard
  url/-l{17*' '}copy the url of an entry to your clipboard
  note/-n{16*' '}copy the note of an entry to your clipboard\n""")
    elif arguments[0] == 'gen' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp /<entry name> gen [option]\u001b[0m\n
\u001b[1moptions:\u001b[0m
 gen:
  update/-u{14*' '}generate a password for an existing entry\n""")
    else:
        print("\n\u001b[1msshyp ", "copyright (c) 2021-2024 ", """randall winkhart\u001b[0m
this is free software, and you are welcome to redistribute it under certain conditions;
this program comes with absolutely no warranty; type 'sshyp license' for details""")
        if device_type == 'client':
            print(f"""\n\u001b[1musage:\u001b[0m sshyp [/<entry name> [argument] [option]] | [argument]\n
\u001b[1marguments:\u001b[0m
 help/-h{17*' '}bring up this menu
 version/-v{14*' '}display sshyp version info
 init{20*' '}set up sshyp
 tweak{19*' '}change configuration options/manage extensions and updates
 add{21*' '}add an entry
 gen{21*' '}generate a new password
 edit{20*' '}edit an existing entry
 copy{20*' '}copy details of an entry to your clipboard
 shear{19*' '}delete an existing entry
 sync{20*' '}manually sync the entry directory via sshync
\n\u001b[1moptions:\u001b[0m
 add:
  password/-p{12*' '}add a password entry
  note/-n{16*' '}add a note entry
  folder/-f{14*' '}add a new folder for entries
 edit:
  rename/relocate/-r{5*' '}rename or relocate an entry
  username/-u{12*' '}change the username of an entry
  password/-p{12*' '}change the password of an entry
  url/-l{17*' '}change the url attached to an entry
  note/-n{16*' '}change the note attached to an entry
 copy:
  username/-u{12*' '}copy the username of an entry to your clipboard
  password/-p{12*' '}copy the password of an entry to your clipboard
  url/-l{17*' '}copy the url of an entry to your clipboard
  note/-n{16*' '}copy the note of an entry to your clipboard
 gen:
  update/-u{14*' '}generate a password for an existing entry
\n\u001b[1mtip 1:\u001b[0m you can quickly read an entry with 'sshyp /<entry name>'
\u001b[1mtip 2:\u001b[0m type 'sshyp' to view a list of saved entries\n""")
        # PORT START HELP-SERVER
        else:
            print(f"""\n\u001b[1musage:\u001b[0m sshyp <argument>\n
\u001b[1marguments:\u001b[0m
 help/-h{17*' '}bring up this menu
 version/-v{14*' '}display sshyp version info
 init{20*' '}set up sshyp
 tweak{19*' '}change configuration options/manage extensions and updates\n""")
        # PORT END HELP-SERVER


# shortcut to quickly read an entry
def read_shortcut():
    target_type_check(entry_name, True, True)
    entry_reader(decrypt(directory + entry_name, _quick_verify=quick_unlock_enabled))


# calls sshync to sync changes to the user's server
def sync(_start_text=''):
    print(f"{_start_text}syncing entries with the server device...\n")
    # set permissions before uploading
    for _root, _dirs, _files in walk(f"{home}/.local/share/sshyp"):
        for _path in _root.splitlines():
            chmod(_path, 0o700)
        for _file in _files:
            chmod(_root + '/' + _file, 0o600)
    run_profile(f"{home}/.config/sshyp/sshyp.ini", silent_sync)


# adds a new entry
def add_entry():
    # make sure the add target does not already exist
    target_exists_check(entry_name, False)

    # note entry
    if arguments[2] in ('note', '-n'):
        _password, _username, _url, _note = '', '', '', edit_note([])
    else:
        # password entry
        from getpass import getpass
        _username = str(input('\nusername: '))
        _password = str(getpass(prompt='\npassword: '))
        _url = str(input('\nurl: '))
        if input('\nadd a note to this entry? (y/N) ').lower() == 'y':
            _note = edit_note([])
        else:
            _note = ''
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader([_password, _username, _url, _note])
    encrypt([_password, _username, _url, _note], directory + entry_name, gpg_id)


# creates a new folder
def add_folder():
    Path(directory + entry_name).mkdir(mode=0o700, parents=True, exist_ok=True)
    if not ssh_error:
        run(('ssh', '-i', identity, '-p', port, f"{username_ssh}@{ip}",
             f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{entry_name}")'
             f'.mkdir(mode=0o700, parents=True, exist_ok=True)\''))


# renames an entry or folder
def rename():
    from shutil import copy

    # check if the renaming target is an entry (file) or a folder
    _file = target_type_check(entry_name)

    # collect the new name for the target from user input
    _new_name = str(input('new name: ')).strip('/')

    # check if the new name already exists
    target_exists_check(_new_name, False)

    # if renaming a file
    if _file:
        if not ssh_error:
            copy(f"{directory}{entry_name}.gpg", f"{directory}{_new_name}.gpg")
        else:
            move(f"{directory}{entry_name}.gpg", f"{directory}{_new_name}.gpg")
    else:

        # if renaming a folder
        if not ssh_error:
            Path(f"{directory}{_new_name}").mkdir(mode=0o700, parents=True, exist_ok=True)
            run(('ssh', '-i', identity, '-p', port, f"{username_ssh}@{ip}",
                 f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{entry_name}")'
                 f'.rename(Path("{directory_ssh}{_new_name}"))\''))                 
        else:
            move(f"{directory}{entry_name}", f"{directory}{_new_name}")
    if not ssh_error:
        run(('ssh', '-i', identity, '-p', port, f"{username_ssh}@{ip}",
             f'cd /usr/lib/sshyp; python3 -c \'from sshync import delete; delete("{entry_name}", "remotely", True)\''))


# edits the contents of an entry
def edit():
    # set to avoid PEP8 warnings
    _detail, _edit_line = None, None
    
    # ensure the edit target is an entry
    target_type_check(entry_name, True, True)

    if arguments[2] in ('username', '-u'):
        _detail, _edit_line = str(input('\nusername: ')), 1
    elif arguments[2] in ('password', '-p'):
        from getpass import getpass
        _detail, _edit_line = str(getpass(prompt='\npassword: ')), 0
    elif arguments[2] in ('url', '-l'):
        _detail, _edit_line = str(input('\nurl: ')), 2
    if arguments[2] in ('note', '-n'):
        _old_lines = decrypt(directory + entry_name, _quick_verify=quick_unlock_enabled)
        _new_lines = _old_lines[0:3] + edit_note(_old_lines[3:], True).split('\n')
    else:
        _new_lines = line_edit(decrypt(directory + entry_name, _quick_verify=quick_unlock_enabled), _detail,
                               _edit_line)
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(_new_lines)
    encrypt(_new_lines, directory + entry_name, gpg_id)


# generates a password for a new or an existing entry
def gen():
    # set to avoid PEP8 warnings
    _username, _url, _notes = None, None, None
    # gen update
    if arg_count == 3 and arguments[2] in ('update', '-u'):
        # ensure the gen update target is an entry        
        target_type_check(entry_name, True, True)
        _new_lines = line_edit(decrypt(directory + entry_name, _quick_verify=quick_unlock_enabled), pass_gen(), 0)
    # gen
    else:
        # make sure the gen target does not already exist
        target_exists_check(entry_name, False)
        _username = str(input('\nusername: '))
        _password = pass_gen()
        _url = str(input('\nurl: '))
        if input('\nadd a note to this entry? (y/N) ').lower() == 'y':
            _note = edit_note([])
        else:
            _note = ''
        _new_lines = [_password, _username, _url, _note]
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(_new_lines)
    encrypt(_new_lines, directory + entry_name, gpg_id)


# copies a specified field of an entry to the clipboard
def copy_data():
    from hashlib import sha512
    from subprocess import Popen
    # ensure the copy target is an entry
    target_type_check(entry_name, True, True)
    _index = 0
    if arguments[2] in ('username', '-u'):
        _index = 1
    elif arguments[2] in ('password', '-p'):
        _index = 0
    elif arguments[2] in ('url', '-l'):
        _index = 2
    elif arguments[2] in ('note', '-n'):
        _index = 3
    _copy_subject = decrypt(directory + entry_name, _quick_verify=quick_unlock_enabled)[_index]
    # ensure field is not blank
    if _copy_subject == '':
        raise IndexError

    # store hashed _copy_subject for later comparison
    _hash = sha512()
    _hash.update(_copy_subject.encode('utf-8'))

    # PORT START CLIPBOARD
    # WSL clipboard detection
    if 'WSL_DISTRO_NAME' in environ:
        run(('powershell.exe', '-c', "Set-Clipboard '" + _copy_subject.replace("'", "''") + "'"))
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'wsl'), stdout=DEVNULL,
              stderr=DEVNULL)
    # Wayland clipboard detection
    elif 'WAYLAND_DISPLAY' in environ:
        run('wl-copy', stdin=Popen(('printf', '%b', _copy_subject.replace('\\', '\\\\')), stdout=PIPE).stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'wayland'))
    # Haiku clipboard detection
    elif uname()[0] == 'Haiku':
        run(('clipboard', '-c', _copy_subject))
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'haiku'))
    # MacOS clipboard detection
    elif uname()[0] == 'Darwin':
        run('pbcopy', stdin=Popen(('printf', '%b', _copy_subject.replace('\\', '\\\\')), stdout=PIPE).stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'mac'))
    # Termux (Android) clipboard detection
    elif isdir("/data/data/com.termux"):
        run(('termux-clipboard-set', _copy_subject))
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'termux'))
    # X11 clipboard detection
    elif 'DISPLAY' in environ:
        run(('xclip', '-sel', 'c'), stdin=Popen(('printf', '%b', _copy_subject.replace('\\', '\\\\')), stdout=PIPE)
            .stdout)
        Popen((realpath(__file__).rsplit('/', 1)[0] + "/clipclear.py", _hash.hexdigest(), 'x11'))
    else:
        print('\n\u001b[38;5;9merror: clipboard tool could not be determined\n\nnote that the clipboard does not '
              'function in a raw tty\u001b[0m\n')
    # PORT END CLIPBOARD


# deletes an entry from the server and flags it for local deletion on sync
def remove_data():
    decrypt(None, _quick_verify=quick_unlock_enabled)
    if not ssh_error:
        run(('ssh', '-i', identity, '-p', port, f"{username_ssh}@{ip}",
             f'cd /usr/lib/sshyp; python3 -c \'from sshync import delete; delete("{entry_name}", "remotely", True)\''))
    else:
        offline_delete(entry_name, 'locally', silent_sync)


# checks extension config files for matches to argument, runs extensions
def extension_runner():
    _output_com, _extension_dir = None, realpath(__file__).rsplit('/', 1)[0] + '/extensions/'
    if isdir(_extension_dir):
        for _extension in listdir(_extension_dir):
            _extension_config = ConfigParser(interpolation=None)
            _extension_config.read(_extension_dir + _extension)
            _input_com = _extension_config.get('config', 'input').split()
            if _input_com == arguments[arg_start:]:
                _output_com = _extension_config.get('config', 'output').split()
                if arg_start == 1:
                    _output_com.append(arguments[0])
        if _output_com is not None:
            run(_output_com)
        else:
            print_info()
    else:
        print_info()
    s_exit()


if __name__ == "__main__":
    try:
        # set default states
        ssh_error, success_flag, sync_flag, silent_sync, pass_show = False, False, False, False, False
        
        # set to avoid PEP8 warnings
        arg_start, device_type, offline_mode_enabled = None, None, None
        
        # retrieve typed argument
        arguments = argv[1:]
        arg_count = len(arguments)

        # check if an entry name is correctly supplied
        if arg_count < 1 or (arg_count > 0 and arguments[0] != 'init'):
            if arg_count > 0 and arguments[0].startswith('/'):
                arg_start = 1
                entry_name = arguments[0].strip('/')
                # determine whether to show passwords in entry previews
                if arg_count > 1 and arguments[arg_count-1] in ('--show', '-s'):
                    del arguments[-1]
                    arg_count -= 1
                    pass_show = True
            else:
                arg_start = 0

            # import saved userdata
            try:
                sshyp_data = ConfigParser(interpolation=None)
                sshyp_data.read(f"{home}/.config/sshyp/sshyp.ini")
                device_type = sshyp_data.get('GENERAL', 'device_type')
                if device_type == 'client':
                    directory = f"{home}/.local/share/sshyp/"
                    gpg_id = sshyp_data.get('CLIENT-GENERAL', 'gpg_id')
                    editor = sshyp_data.get('CLIENT-GENERAL', 'text_editor')
                    offline_mode_enabled = sshyp_data.getboolean('CLIENT-GENERAL', 'offline_mode_enabled')
                    if offline_mode_enabled:
                        ssh_error = True
                        quick_unlock_enabled = False
                    else:
                        quick_unlock_enabled = sshyp_data.getboolean('CLIENT-ONLINE', 'quick_unlock_enabled')
                        username_ssh = sshyp_data.get('SSHYNC', 'user')
                        ip = sshyp_data.get('SSHYNC', 'ip')
                        port = sshyp_data.get('SSHYNC', 'port')
                        directory_ssh = sshyp_data.get('SSHYNC', 'remote_dir')
                        identity = sshyp_data.get('SSHYNC', 'identity_file')
                        client_device_id = listdir(f"{home}/.config/sshyp/devices")[0]
                        ssh_error = sshyp_data.getboolean('CLIENT-ONLINE', 'ssh_error')
                        if ssh_error:
                            ssh_error = copy_id_check(port, username_ssh, ip, client_device_id, identity, sshyp_data)
            except (FileNotFoundError, NoSectionError, NoOptionError):
                print(f"\n{73*'!'}")
                print("not all necessary configurations have been made - please run 'sshyp init'")
                print(f"{73*'!'}\n")
                s_exit(1)
        else:
            from stweak import wrapped_entry
            wrapped_entry(False, 'additional configuration options:')
            s_exit()

        # run function based on arguments
        if device_type == 'client':
            if arg_count < 1:
                entry_list_gen()

            elif arg_count == 3 and arg_start == 1:
                if arguments[1] == 'copy':
                    if arguments[2] in ('username', '-u', 'password', '-p', 'url', '-l', 'note', '-n'):
                        try:
                            success_flag = 1
                            copy_data()
                        except IndexError:
                            print('\n\u001b[38;5;9merror: field does not exist in entry\u001b[0m\n')
                            s_exit(2)
                elif arguments[1] == 'add':
                    if arguments[2] in ('note', '-n', 'password', '-p'):
                        success_flag, sync_flag = True, True
                        add_entry()
                    elif arguments[2] in ('folder', '-f'):
                        success_flag = 1
                        add_folder()
                elif arguments[1] == 'edit':
                    if arguments[2] in ('rename', 'relocate', '-r'):
                        success_flag, sync_flag, silent_sync = True, True, True
                        rename()
                    elif arguments[2] in ('username', '-u', 'password', '-p', 'url', '-l', 'note', '-n'):
                        success_flag, sync_flag = True, True
                        edit()
                elif arguments[1] == 'gen' and arguments[2] in ('update', '-u'):
                    success_flag, sync_flag = True, True
                    gen()

            elif arg_count == 2 and arg_start == 1:
                if arguments[1] == 'gen':
                    success_flag, sync_flag = True, True
                    gen()
                elif arguments[1] == 'shear':
                    success_flag = True
                    remove_data()

            elif arg_count == 1:
                if arg_start == 1:
                    success_flag = True
                    read_shortcut()
                elif arguments[0] == 'tweak':
                    success_flag = True
                    from stweak import wrapped_entry
                    wrapped_entry(device_type)
       
            if arg_count > 0 and success_flag == 0 and arguments[0] != 'sync':
                if arguments[0] not in ('help', '-h', 'version', '-v', 'license'):
                    extension_runner()
                else:
                    print_info()
            elif not ssh_error:
                if sync_flag: 
                    sync()
                elif (arg_count > 0 and arguments[0] == 'sync') or (arg_count > 1 and arguments[1] == 'shear'):
                    sync('\n')
            elif arg_count > 0 and arguments[0] == 'sync' and offline_mode_enabled:
                print("\n\u001b[38;5;9mwarning: sshyp is currently configured in offline mode - ssh synchronization is "
                      "disabled\u001b[0m\n")

        # PORT START ARGS-SERVER
        # server arguments
        else:
            if arg_count == 1 and arguments[0] == 'tweak':
                success_flag = True
                from stweak import wrapped_entry
                wrapped_entry(device_type)
            else:
                if arg_count < 1:
                    arguments.append('help')
                print_info()
        # PORT END ARGS-SERVER

    except KeyboardInterrupt:
        print('\n')
