#!/usr/bin/env python3
from configparser import ConfigParser, NoSectionError
from os import chmod, environ, listdir, remove, walk
from os.path import expanduser, isdir, isfile, realpath
from pathlib import Path
from random import randint
from shutil import move, rmtree
from sshync import delete as offline_delete, run_profile
from subprocess import CalledProcessError, DEVNULL, PIPE, run
from sys import argv, exit as s_exit
# PORT START UNAME-IMPORT-SSHYP
from os import uname
# PORT END UNAME-IMPORT-SSHYP
home = expanduser("~")


# UTILITY FUNCTIONS

# generates and prints full entry list
def entry_list_gen(_directory=f"{home}/.local/share/sshyp/"):
    from shutil import get_terminal_size
    from textwrap import fill
    _ran = False
    print("\nfor a list of usable commands, run 'sshyp help'\n\n\u001b[38;5;0;48;5;15msshyp entries:\u001b[0m\n")
    for _root, _dirs, _files in sorted(walk(_directory, topdown=True)):
        _entry_list, _color_alternator = [], 1
        if _ran:
            print(f"\u001b[38;5;15;48;5;238m{_root.replace(f'{home}/.local/share/sshyp', '', 1)}/\u001b[0m")
        for filename in sorted(_files):
            if _color_alternator > 0:
                _entry_list.append(filename[:-4])
            else:
                _entry_list.append(f"\u001b[38;5;8m{filename[:-4]}\u001b[0m")
            _color_alternator = _color_alternator * -1
        _real = len(' '.join(_entry_list)) - (5.5 * len(_entry_list))
        if _real <= get_terminal_size()[0]:
            _width = len(' '.join(_entry_list))
        else:
            _width = (len(' '.join(_entry_list)) / (_real / get_terminal_size()[0]) - 25)
        if len(_entry_list) > 0:
            print(fill(' '.join(_entry_list), width=_width) + '\n')
        elif _ran:
            print('\u001b[38;5;9m-empty directory-\u001b[0m\n')
        _ran = True


# displays the contents of an entry in a readable format
def entry_reader(_decrypted_entry):
    _entry_lines, _notes_flag = [_line.rstrip() for _line in open(_decrypted_entry, 'r').readlines()], 0
    if pass_show:
        _entry_password = f'\u001b[38;5;10m{_entry_lines[0]}\u001b[0m'
    else:
        _entry_password = f'\u001b[38;5;3mend command in "--show" or "-s" to view\u001b[0m'
    print()
    for _num in range(len(_entry_lines)):
        try:
            if _num == 0 and _entry_lines[1] != '':
                print(f"\u001b[38;5;15;48;5;238musername:\u001b[0m\n{_entry_lines[1]}\n")
            elif _num == 1 and _entry_lines[0] != '':
                print(f"\u001b[38;5;15;48;5;238mpassword:\u001b[0m\n{_entry_password}\n")
            elif _num == 2 and _entry_lines[2] != '':
                print(f"\u001b[38;5;15;48;5;238murl:\u001b[0m\n{_entry_lines[_num]}\n")
            elif _num >= 3 and _entry_lines[_num] != '' and _notes_flag != 1:
                _notes_flag = 1
                print('\u001b[38;5;15;48;5;238mnotes:\u001b[0m\n' + _entry_lines[_num])
            elif _num >= 3 and _notes_flag == 1:
                print(_entry_lines[_num])
            if _notes_flag == 1:
                try:
                    _line_test = _entry_lines[_num + 1]
                except IndexError:
                    print()
        except IndexError:
            if _num == 0:
                print(f"\u001b[38;5;15;48;5;238mpassword:\u001b[0m\n{_entry_password}\n")


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
            _length = int(input('password length: '))
        except ValueError:
            continue
        else:
            if _length < 1:
                continue
            else:
                break
    _complexity = str(input('password complexity - simple (for compatibility) or complex (for security)? (s/C) '))
    if _complexity not in ('s', 'S'):
        _complexity = 'c'
    _gen = string_gen(_complexity.lower(), _length)
    return _gen


# creates a temporary directory for entry editing
def shm_gen(_tmp_dir=f"{home}/.config/sshyp/tmp/"):
    _shm_folder_gen = string_gen('f', randint(12, 48))
    _shm_entry_gen = string_gen('f', randint(12, 48))
    Path(_tmp_dir + _shm_folder_gen).mkdir(mode=0o700)
    return _shm_folder_gen, _shm_entry_gen


# encrypts an entry and cleans up the temporary files
def encrypt(_entry_dir, _shm_folder, _shm_entry, _gpg_id, _tmp_dir=f"{home}/.config/sshyp/tmp/"):
    run(('gpg', '-qr', str(_gpg_id), '-e', f"{_tmp_dir}{_shm_folder}/{_shm_entry}"))
    move(f"{_tmp_dir}{_shm_folder}/{_shm_entry}.gpg", f"{_entry_dir}.gpg")
    rmtree(f"{_tmp_dir}{_shm_folder}")


# decrypts an entry to a temporary directory
def decrypt(_entry_dir, _shm_folder, _shm_entry, _quick_pass,
            _tmp_dir=f"{home}/.config/sshyp/tmp/"):
    if not isinstance(_quick_pass, bool):
        _unlock_method = ('gpg', '--pinentry-mode', 'loopback', '--passphrase', _quick_pass, '-qd', '--output')
    else:
        _unlock_method = ('gpg', '-qd', '--output')
    if _shm_folder is None and _shm_entry is None:
        _output_target = ('/dev/null', f"{home}/.config/sshyp/lock.gpg")
    else:
        _output_target = (f"{_tmp_dir}{_shm_folder}/{_shm_entry}", f"{_entry_dir}.gpg")
    try:
        run(_unlock_method + _output_target, stderr=DEVNULL, check=True)
    except CalledProcessError:
        if not isinstance(_quick_pass, bool):
            print('\n\u001b[38;5;9merror: quick-unlock failed as a result of an incorrect passphrase, an unreachable '
                  'sshyp server, or an invalid configuration\n\nfalling back to standard unlock\u001b[0m\n')
            try:
                run(('gpg', '-qd', '--output') + _output_target, stderr=DEVNULL, check=True)
            except CalledProcessError:
                print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
                s_exit(4)
        else:
            print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
            s_exit(4)


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


# call decrypt() based on quick-unlock status
def determine_decrypt(_entry_dir, _shm_folder, _shm_entry):
    if quick_unlock_enabled == 'true':
        decrypt(_entry_dir, _shm_folder, _shm_entry, whitelist_verify(port, username_ssh, ip, client_device_id))
    else:
        decrypt(_entry_dir, _shm_folder, _shm_entry, False)


# ensures an edited entry is optimized for best compatibility
def optimized_edit(_lines, _edit_data, _edit_line):
    while len(_lines) < _edit_line + 1:
        _lines.append('\n')
    if _edit_data is not None:
        _lines[_edit_line] = _edit_data.strip('\n').rstrip() + '\n'
    for _num in range(len(_lines)):
        if not _lines[_num].endswith('\n'):
            _lines[_num] += '\n'
    for _num in reversed(range(len(_lines))):
        if _lines[_num] == '\n':
            _lines = _lines[:-1]
        elif _lines[_num].endswith('\n'):
            _lines[_num] = _lines[_num].rstrip()
            break
        else:
            break
    return _lines


# edits the note attached to an entry
def edit_note(_shm_folder, _shm_entry, _lines):
    _reg_lines = _lines[0:3]
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'w').writelines(_lines[3:])
    run((editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"))
    _new_notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n").readlines()
    while len(_reg_lines) < 3:
        _reg_lines.append('\n')
    _noted_lines = _reg_lines + _new_notes
    return _noted_lines


# attempts to connect to the user's server via ssh to register the device for syncing
def copy_id_check(_port, _username_ssh, _ip, _client_device_id, _sshyp_data):
    from stweak import write_config
    if not _sshyp_data.has_section('CLIENT-ONLINE'):
        _sshyp_data.add_section('CLIENT-ONLINE')
    try:
        run(('ssh', '-o', 'ConnectTimeout=3', '-i', f"{home}/.ssh/sshyp", '-p', _port, f"{_username_ssh}@{_ip}",
             f'python3 -c \'from pathlib import Path; Path("/home/{_username_ssh}/.config/sshyp/devices/'
             f'{_client_device_id}").touch(mode=0o400, exist_ok=True)\''), stderr=DEVNULL, check=True)
    except CalledProcessError:
        print('\n\u001b[38;5;9mwarning: ssh connection could not be made - ensure the public key (~/.ssh/sshyp.pub) is '
              'registered on the remote server and that the entered ip, port, and username are correct\n\nsyncing '
              'functionality will be disabled until this is addressed\u001b[0m\n')
        _sshyp_data.set('CLIENT-ONLINE', 'ssh_error', '1')
        write_config(_sshyp_data)
        return True
    _sshyp_data.set('CLIENT-ONLINE', 'ssh_error', '0')
    write_config(_sshyp_data)
    return False


# ARGUMENT-SPECIFIC FUNCTIONS

# prints help text based on argument
def print_info():
    if arguments[0] in ('version', '-v'):
        _blank = '\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m' + 54*' ' + '\u001b[38;5;7;48;5;8m/\u001b[0m'
        _border = '\u001b[38;5;7;48;5;8m' + 28*'<>' + '\u001b[0m\n'
        print(f"""\nsshyp is a simple, self-hosted, sftp-synchronized\npassword manager for unix(-like) systems\n
{16*' '}..{7*' '}\u001b[38;5;9m♥♥ ♥♥\u001b[0m{7*' '}..
{9*' '}.''.''/()\\{5*' '}\u001b[38;5;13m♥♥♥♥♥♥♥\u001b[0m{5*' '}/()\\''.''.
{8*' '}*{7*' '}:{8*' '}\u001b[38;5;9m♥♥♥♥♥\u001b[0m{8*' '}:{7*' '}*
{9*' '}`..'..'{10*' '}\u001b[38;5;13m♥♥♥\u001b[0m{10*' '}`..'..'
{9*' '}//{3*' '}\\\\{11*' '}\u001b[38;5;9m♥\u001b[0m{11*' '}//{3*' '}\\\\""")
        print(f"{_border}{_blank}\n\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m{3*' '}\u001b[38;5;15;48;5;8m"
              f"sshyp ", f"copyright (c) 2021-2023 ", f"randall winkhart\u001b[38;5;15;48;5;15m{3*' '}"
              f"\u001b[38;5;7;48;5;8m/\u001b[0m\n{_blank}")
        print(f"\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m{20*' '}\u001b[38;5;15;48;5;8mversion 1.4.99"
              f"\u001b[38;5;15;48;5;15m{20*' '}\u001b[38;5;7;48;5;8m/\u001b[0m")
        print(f"\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m{9*' '}\u001b[38;5;15;48;5;8mthe argumentative "
              f"agronomist update\u001b[38;5;15;48;5;15m{10*' '}\u001b[38;5;7;48;5;8m/\u001b[0m")
        print(f"{_blank}\n{_border}\nsee https://github.com/rwinkhart/sshyp for more information\n")
    elif arguments[0] == 'license':
        print('\nThis program is free software: you can redistribute it and/or modify it under the terms\nof version 3 '
              '(only) of the GNU General Public License as published by the Free Software Foundation.\n\nThis program '
              'is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;\nwithout even the implied '
              'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\nSee the GNU General Public License for'
              ' more details.\n\nhttps://opensource.org/licenses/GPL-3.0\n')
    elif arguments[0] == 'add' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp </entry name> add <option>\u001b[0m\n
\u001b[1moptions:\u001b[0m
 add:
  password/-p{12*' '}add a password entry
  note/-n{16*' '}add a note entry
  folder/-f{14*' '}add a new folder for entries\n""")
    elif arguments[0] == 'edit' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp </entry name> edit <option>\u001b[0m\n
\u001b[1moptions:\u001b[0m
 edit:
  rename/relocate/-r{5*' '}rename or relocate an entry
  username/-u{12*' '}change the username of an entry
  password/-p{12*' '}change the password of an entry
  url/-l{17*' '}change the url attached to an entry
  note/-n{16*' '}change the note attached to an entry\n""")
    elif arguments[0] == 'copy' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp </entry name> copy <option>\u001b[0m\n
\u001b[1moptions:\u001b[0m
 copy:
  username/-u{12*' '}copy the username of an entry to your clipboard
  password/-p{12*' '}copy the password of an entry to your clipboard
  url/-l{17*' '}copy the url of an entry to your clipboard
  note/-n{16*' '}copy the note of an entry to your clipboard\n""")
    elif arguments[0] == 'gen' and device_type == 'client':
        print(f"""\n\u001b[1musage:\u001b[0m sshyp </entry name> gen [option]\u001b[0m\n
\u001b[1moptions:\u001b[0m
 gen:
  update/-u{14*' '}generate a password for an existing entry\n""")
    elif arguments[0] == 'whitelist':
        if device_type == 'server':
            if arg_count > 1 and arguments[1] in ('add', 'del'):
                print("\nwhen adding or deleting devices from the whitelist,\nthe device ID must be specified as an"
                      " argument\n\nexample: sshyp whitelist add 'this-is-a-quoted-device-id'")
            print(f"""\n\u001b[1musage:\u001b[0m sshyp whitelist <option> [device id]\u001b[0m\n
\u001b[1moptions:\u001b[0m
 whitelist:
  setup{18*' '}set up the quick-unlock whitelist
  list/-l{16*' '}view all registered device ids and their quick-unlock whitelist status
  add{20*' '}whitelist a device id for quick-unlock
  del{20*' '}remove a device id from the quick-unlock whitelist\n""")
        else:
            print('\n\u001b[38;5;9merror: argument (whitelist) only available on server\u001b[0m\n')
    else:
        print("\n\u001b[1msshyp ", "copyright (c) 2021-2023 ", """randall winkhart\u001b[0m
this is free software, and you are welcome to redistribute it under certain conditions;
this program comes with absolutely no warranty; type 'sshyp license' for details""")
        if device_type == 'client':
            print(f"""\n\u001b[1musage:\u001b[0m sshyp [</entry name> [argument] [option]] | [argument]\n
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
\n\u001b[1mtip 1:\u001b[0m you can quickly read an entry with 'sshyp </entry name>'
\u001b[1mtip 2:\u001b[0m type 'sshyp' to view a list of saved entries\n""")
        # PORT START HELP-SERVER
        else:
            print(f"""\n\u001b[1musage:\u001b[0m sshyp <argument> [option] [device id]\n
\u001b[1marguments:\u001b[0m
 help/-h{17*' '}bring up this menu
 version/-v{14*' '}display sshyp version info
 init{20*' '}set up sshyp
 tweak{19*' '}change configuration options/manage extensions and updates
 whitelist{15*' '}manage the quick-unlock whitelist
\n\u001b[1moptions:\u001b[0m
 whitelist:
  setup{18*' '}set up the quick-unlock whitelist
  list/-l{16*' '}view all registered device ids and their quick-unlock whitelist status
  add{20*' '}whitelist a device id for quick-unlock
  del{20*' '}remove a device id from the quick-unlock whitelist\n""")
        # PORT END HELP-SERVER


# shortcut to quickly read an entry
def read_shortcut():
    target_type_check(entry_name, True, True)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + entry_name, _shm_folder, _shm_entry)
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    rmtree(f"{tmp_dir}{_shm_folder}")


# calls sshync to sync changes to the user's server
def sync():
    print('\nsyncing entries with the server device...\n')
    # set permissions before uploading
    for _root, _dirs, _files in walk(f"{home}/.local/share/sshyp"):
        for _path in _root.splitlines():
            chmod(_path, 0o700)
        for _file in _files:
            chmod(_root + '/' + _file, 0o600)
    run_profile(f"{home}/.config/sshyp/sshyp.ini", silent_sync)


# PORT START WHITELIST-SERVER
# takes input from the user to set up quick-unlock password
def whitelist_setup():
    _gpg_password_temp = str(input('\nfull gpg passphrase: '))
    _half_length = int(len(_gpg_password_temp)/2)
    try:
        _short_password_length = int(input(f"\nquick unlock pin length (must be half the length of gpg password or "
                                           f"less) ({_half_length}): "))
        if _short_password_length > _half_length:
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
        'Name-Comment: gpg-sshyp-whitelist\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
    run(('gpg', '-q', '--pinentry-mode', 'loopback', '--batch', '--generate-key', '--passphrase',
         _quick_unlock_password, f"{home}/.config/sshyp/gpg-gen"))
    remove(f"{home}/.config/sshyp/gpg-gen")
    _gpg_id = run(('gpg', '-k'), stdout=PIPE, text=True).stdout.splitlines()[-3].strip()

    # encrypt excluded with the assembly key
    _shm_folder, _shm_entry = shm_gen()
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').write(_quick_unlock_password_excluded)
    encrypt(f"{home}/.config/sshyp/excluded", _shm_folder, _shm_entry, _gpg_id)
    print(f"\nyour quick-unlock passphrase: {_quick_unlock_password}")


# shows the quick-unlock whitelist status of device ids
def whitelist_list():
    _whitelisted_ids = listdir(f"{home}/.config/sshyp/whitelist")
    _device_ids = listdir(f"{home}/.config/sshyp/devices")
    print('\n\u001b[1mquick-unlock whitelisted device ids:\u001b[0m')
    for _id in _whitelisted_ids:
        print(_id)
    print('\n\u001b[1mother registered device ids:\u001b[0m')
    for _id in _device_ids:
        if _id not in _whitelisted_ids:
            print(_id)
    print()


# adds or removes quick-unlock whitelisted device ids
def whitelist_manage(_device_id):
    if arguments[1] == 'add':
        if _device_id in listdir(f"{home}/.config/sshyp/devices"):
            open(f"{home}/.config/sshyp/whitelist/{_device_id}", 'w').write('')
            whitelist_list()
        else:
            print(f"\n\u001b[38;5;9merror: device id ({_device_id}) is not registered\u001b[0m\n")
            s_exit(1)
    elif isfile(f"{home}/.config/sshyp/whitelist/{_device_id}"):
        remove(f"{home}/.config/sshyp/whitelist/{_device_id}")
        whitelist_list()
    else:
        print(f"\n\u001b[38;5;9merror: device id ({_device_id}) is not whitelisted\u001b[0m\n")
        s_exit(1)
# PORT END WHITELIST-SERVER


# checks the user's whitelist status and fetches the full gpg key password if possible
def whitelist_verify(_port, _username_ssh, _ip, _client_device_id):
    try:
        run(('gpg', '--pinentry-mode', 'cancel', '-qd', '--output', '/dev/null',
             f"{home}/.config/sshyp/lock.gpg"), stderr=DEVNULL, check=True)
        return False
    except CalledProcessError:
        _i, _full_password = 0, ''
        _server_whitelist = run(('ssh', '-i', f"{home}/.ssh/sshyp", '-p', _port, f"{_username_ssh}@{_ip}",
                                 f'python3 -c \'from os import listdir; print(*listdir("/home/{_username_ssh}'
                                 f'/.config/sshyp/whitelist"))\''), stdout=PIPE, text=True).stdout.rstrip().split()
        for _device_id in _server_whitelist:
            if _device_id == _client_device_id:
                from getpass import getpass
                _quick_unlock_password = getpass(prompt='\nquick-unlock passphrase: ')
                _quick_unlock_password_excluded = \
                    run(('ssh', '-i', f"{home}/.ssh/sshyp", '-p',  _port, f"{_username_ssh}@{_ip}",
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


# adds a new entry
def add_entry():
    # set to avoid PEP8 warnings
    _shm_folder, _shm_entry = None, None

    # make sure the add target does not already exist
    target_exists_check(entry_name, False)

    # note entry
    if arguments[2] in ('note', '-n'):
        _shm_folder, _shm_entry = shm_gen()
        run((editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"))
        _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(optimized_edit(['', '', '', _notes], None, -1))
    else:

        # password entry
        _username = str(input('username: '))
        _password = str(input('password: '))
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
        _shm_folder, _shm_entry = shm_gen()
        if _add_note.lower() == 'y':
            run((editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"))
            _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        else:
            _notes = ''
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w')\
            .writelines(optimized_edit([_password, _username, _url, _notes], None, -1))
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + entry_name, _shm_folder, _shm_entry, gpg_id)


# creates a new folder
def add_folder():
    Path(directory + entry_name).mkdir(mode=0o700, parents=True, exist_ok=True)
    if not ssh_error:
        run(('ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
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
            run(('ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
                 f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{entry_name}")'
                 f'.rename(Path("{directory_ssh}{_new_name}"))\''))                 
        else:
            move(f"{directory}{entry_name}", f"{directory}{_new_name}")
    if not ssh_error:
        run(('ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
             f'cd /lib/sshyp; python3 -c \'from sshync import delete; delete("{entry_name}", "remotely", True)\''))


# edits the contents of an entry
def edit():
    # set to avoid PEP8 warnings
    _shm_folder, _shm_entry, _detail, _edit_line = None, None, None, None
    
    # ensure the edit target is an entry
    target_type_check(entry_name, True, True)
    
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + entry_name, _shm_folder, _shm_entry)
    if arguments[2] in ('username', '-u'):
        _detail, _edit_line = str(input('username: ')), 1
    elif arguments[2] in ('password', '-p'):
        _detail, _edit_line = str(input('password: ')), 0
    elif arguments[2] in ('url', '-l'):
        _detail, _edit_line = str(input('url: ')), 2
    if arguments[2] in ('note', '-n'):
        _edit_line = 2
        _new_lines = optimized_edit(edit_note(_shm_folder, _shm_entry,
                                              open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines()), None, -1)
    else:
        _new_lines = optimized_edit(open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), _detail, _edit_line)
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_new_lines)
    remove(f"{directory}{entry_name}.gpg")
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + entry_name, _shm_folder, _shm_entry, gpg_id)


# generates a password for a new or an existing entry
def gen():
    # set to avoid PEP8 warnings
    _username, _url, _notes = None, None, None
    _shm_folder, _shm_entry = shm_gen()
    # gen update
    if arg_count == 3 and arguments[2] in ('update', '-u'):
        # ensure the gen update target is an entry        
        target_type_check(entry_name, True, True)
        determine_decrypt(directory + entry_name, _shm_folder, _shm_entry)
        _new_lines = optimized_edit(open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), pass_gen(), 0)
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_new_lines)
        remove(f"{directory}{entry_name}.gpg")
    # gen
    else:
        # make sure the gen target does not already exist
        target_exists_check(entry_name, False)
        _username = str(input('username: '))
        _password = pass_gen()
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
        if _add_note.lower() == 'y':
            run((editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"))
            _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        else:
            _notes = ''
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w')\
            .writelines(optimized_edit([_password, _username, _url, _notes], None, -1))
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + entry_name, _shm_folder, _shm_entry, gpg_id)


# copies a specified field of an entry to the clipboard
def copy_data():
    from subprocess import Popen
    # ensure the copy target is an entry
    target_type_check(entry_name, True, True)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + entry_name, _shm_folder, _shm_entry)
    _copy_line, _index = [_line.rstrip() for _line in open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines()], 0
    if arguments[2] in ('username', '-u'):
        _index = 1
    elif arguments[2] in ('password', '-p'):
        _index = 0
    elif arguments[2] in ('url', '-l'):
        _index = 2
    elif arguments[2] in ('note', '-n'):
        _index = 3
    _copy_subject = _copy_line[_index]
    # ensure field is not blank
    if _copy_subject == '':
        raise IndexError
    # PORT START CLIPBOARD
    # WSL clipboard detection
    if 'WSL_DISTRO_NAME' in environ:
        run(('powershell.exe', '-c', "Set-Clipboard '" + _copy_subject.replace("'", "''") + "'"))
        Popen("sleep 30; powershell.exe -c Set-Clipboard ''", shell=True, stdout=DEVNULL, stderr=DEVNULL)
    # Wayland clipboard detection
    elif 'WAYLAND_DISPLAY' in environ:
        run(('wl-copy', _copy_subject))
        Popen('sleep 30; wl-copy -c', shell=True)
    # Haiku clipboard detection
    elif uname()[0] == 'Haiku':
        run(('clipboard', '-c', _copy_subject))
        Popen('sleep 30; clipboard -r', shell=True)
    # MacOS clipboard detection
    elif uname()[0] == 'Darwin':
        run('pbcopy', stdin=Popen(('printf', _copy_subject.replace('\\', '\\\\').replace('%', '%%')), stdout=PIPE)
            .stdout)
        Popen("sleep 30; printf '' | pbcopy", shell=True)
    # Termux (Android) clipboard detection
    elif isdir("/data/data/com.termux"):
        run(('termux-clipboard-set', _copy_subject))
        Popen("sleep 30; termux-clipboard-set ''", shell=True)
    # X11 clipboard detection
    elif 'DISPLAY' in environ:
        run(('xclip', '-sel', 'c'), stdin=Popen(('printf', _copy_subject.replace('\\', '\\\\')
                                                .replace('%', '%%')), stdout=PIPE).stdout)
        Popen("sleep 30; printf '' | xclip -sel c", shell=True)
    else:
        print('\n\u001b[38;5;9merror: clipboard tool could not be determined\n\nnote that the clipboard does not '
              'function in a raw tty\u001b[0m\n')
    # PORT END CLIPBOARD
    rmtree(f"{tmp_dir}{_shm_folder}")


# deletes an entry from the server and flags it for local deletion on sync
def remove_data():
    determine_decrypt(f"{home}/.config/sshyp/lock.gpg", None, None)
    if not ssh_error:
        run(('ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
             f'cd /lib/sshyp; python3 -c \'from sshync import delete; delete("{entry_name}", "remotely", False)\''))
    else:
        offline_delete(entry_name, 'locally', silent_sync)


# checks extension config files for matches to argument, runs extensions
def extension_runner():
    _output_com, _extension_dir = None, realpath(__file__).rsplit('/', 1)[0] + '/extensions/'
    if isdir(_extension_dir):
        for _extension in listdir(_extension_dir):
            _extension_config = ConfigParser()
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
        arg_start, device_type = None, None
        
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
                    arguments.pop()
                    arg_count -= 1
                    pass_show = True
            else:
                arg_start = 0

            # import saved userdata
            tmp_dir = f"{home}/.config/sshyp/tmp/"
            try:
                sshyp_data = ConfigParser()
                sshyp_data.read(f"{home}/.config/sshyp/sshyp.ini")
                device_type = sshyp_data.get('GENERAL', 'device_type')
                if device_type == 'client':
                    directory = f"{home}/.local/share/sshyp/"
                    gpg_id = sshyp_data.get('CLIENT-GENERAL', 'gpg_id')
                    editor = sshyp_data.get('CLIENT-GENERAL', 'text_editor')
                    offline_mode_enabled = sshyp_data.get('CLIENT-GENERAL', 'offline_mode_enabled')
                    if offline_mode_enabled == 'true':
                        ssh_error = True
                        quick_unlock_enabled = 'false'
                    else:
                        quick_unlock_enabled = sshyp_data.get('CLIENT-ONLINE', 'quick_unlock_enabled')
                        username_ssh = sshyp_data.get('SSHYNC', 'user')
                        ip = sshyp_data.get('SSHYNC', 'ip')
                        port = sshyp_data.get('SSHYNC', 'port')
                        directory_ssh = sshyp_data.get('SSHYNC', 'remote_dir')
                        client_device_id = listdir(f"{home}/.config/sshyp/devices")[0]
                        ssh_error = int(sshyp_data.get('CLIENT-ONLINE', 'ssh_error'))
                        if ssh_error == 1:
                            ssh_error = copy_id_check(port, username_ssh, ip, client_device_id, sshyp_data)
            except (FileNotFoundError, NoSectionError):
                print(f"\n{73*'!'}")
                print("not all necessary configurations have been made - please run 'sshyp init'")
                print(f"{73*'!'}\n")
                s_exit(1)
        else:
            from stweak import initial_setup
            initial_setup()
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
                    success_flag, sync_flag = True, True
                    remove_data()

            elif arg_count == 1:
                if arg_start == 1:
                    success_flag = True
                    read_shortcut()
                elif arguments[0] == 'tweak':
                    success_flag = True
                    from stweak import menu_repeat
                    menu_repeat(False)

        # PORT START ARGS-SERVER
        # server arguments
        else:
            if arg_count < 1:
                arguments.append('help')
                print_info()
            elif arg_count == 2 and arguments[0] == 'whitelist':
                if arguments[1] in ('list', '-l'):
                    success_flag = True
                    whitelist_list()
                elif arguments[1] == 'setup':
                    success_flag = True
                    whitelist_setup()
            elif arg_count == 1 and arguments[0] == 'tweak':
                success_flag = True
                from stweak import global_menu
                global_menu(False)
            elif arg_count > 2 and arguments[1] in ('add', 'del'):
                success_flag = True
                whitelist_manage(arguments[2])
        # PORT END ARGS-SERVER

        if arg_count > 0 and success_flag == 0 and arguments[0] != 'sync':
            if device_type == 'client' and arguments[0] not in ('help', '-h', 'version', '-v', 'license'):
                extension_runner()
            else:
                print_info()
        elif (not ssh_error and sync_flag) or (arg_count > 0 and arguments[0] == 'sync'):
            sync()

    except KeyboardInterrupt:
        print('\n')
