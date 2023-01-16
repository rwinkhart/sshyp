#!/usr/bin/env python3
from os import chmod, environ, listdir, remove, uname, walk
from os.path import expanduser
from pathlib import Path
from random import randint
from shutil import get_terminal_size, move, rmtree
from sshync import delete as offline_delete, run_profile, make_profile, get_profile
from subprocess import CalledProcessError, DEVNULL, PIPE, run
from sys import argv, exit as s_exit


# UTILITY FUNCTIONS

def entry_list_gen(_directory=expanduser('~/.local/share/sshyp/')):  # generates and prints full entry list
    from textwrap import fill
    print('\n\u001b[38;5;0;48;5;15msshyp entries:\u001b[0m\n')
    _entry_list, _color_alternator = [], 1
    for _entry in sorted(listdir(_directory)):
        if Path(f"{_directory}{_entry}").is_file():
            if _color_alternator == 1:
                _entry_list.append(f"{_entry.replace('.gpg', '')}")
                _color_alternator = 2
            else:
                _entry_list.append(f"\u001b[38;5;8m{_entry.replace('.gpg', '')}\u001b[0m")
                _color_alternator = 1
    _real = len(' '.join(_entry_list)) - (5.5 * len(_entry_list))
    if _real <= get_terminal_size()[0]:
        _width = len(' '.join(_entry_list))
    else:
        _width = (len(' '.join(_entry_list)) / (_real / get_terminal_size()[0]) - 25)
    try:
        print(fill(' '.join(_entry_list), width=_width) + '\n')
    except ValueError:
        pass
    for _root, _dirs, _files in walk(_directory):
        for _dir in sorted(_dirs):
            _inner_dir = f"{_root.replace(_directory, '')}/{_dir}"
            print(f"\u001b[38;5;15;48;5;238m{_inner_dir}/\u001b[0m")
            _entry_list, _color_alternator = [], 1
            for _s_root, _s_directories, _s_files in walk(f"{_directory[:-1]}{_inner_dir}"):
                for _entry in sorted(_s_files):
                    if _color_alternator == 1:
                        _entry_list.append(f"{_entry.replace('.gpg', '')}")
                        _color_alternator = 2
                    else:
                        _entry_list.append(f"\u001b[38;5;8m{_entry.replace('.gpg', '')}\u001b[0m")
                        _color_alternator = 1
            _real = len(' '.join(_entry_list)) - (5.5 * len(_entry_list))
            if _real <= get_terminal_size()[0]:
                _width = len(' '.join(_entry_list))
            else:
                _width = (len(' '.join(_entry_list)) / (_real / get_terminal_size()[0]) - 25)
            try:
                print(fill(' '.join(_entry_list), width=_width) + '\n')
            except ValueError:
                print('\u001b[38;5;9m-empty directory-\u001b[0m\n')


def entry_reader(_decrypted_entry):  # displays the contents of an entry in a readable format
    _entry_lines, _notes_flag = open(_decrypted_entry, 'r').readlines(), 0
    print()
    for _num in range(len(_entry_lines)):
        try:
            if _num == 0 and _entry_lines[1] != '\n':
                print(f"\u001b[38;5;15;48;5;238musername:\u001b[0m\n{_entry_lines[1].strip()}\n")
            elif _num == 1 and _entry_lines[0] != '\n':
                print(f"\u001b[38;5;15;48;5;238mpassword:\u001b[0m\n{_entry_lines[0].strip()}\n")
            elif _num == 2 and _entry_lines[2] != '\n':
                print(f"\u001b[38;5;15;48;5;238murl:\u001b[0m\n{_entry_lines[_num].strip()}\n")
            elif _num >= 3 and _entry_lines[_num] != '\n' and _notes_flag != 1:
                _notes_flag = 1
                print(f"\u001b[38;5;15;48;5;238mnotes:\u001b[0m\n{_entry_lines[_num].strip()}")
            elif _num >= 3 and _notes_flag == 1:
                print(_entry_lines[_num].replace('\n', ''))
            if _notes_flag == 1:
                try:
                    _line_test = _entry_lines[_num + 1]
                except IndexError:
                    print()
        except IndexError:
            if _num == 0:
                print(f"\u001b[38;5;15;48;5;238mpassword:\u001b[0m\n{_entry_lines[0]}\n")


def entry_name_fetch(_entry_name_location):  # fetches and returns entry name from user input or from provided argument
    if type(_entry_name_location) == str:
        entry_list_gen()
        _entry_name = str(input(_entry_name_location))
    else:
        _entry_name_split = argument.split(' ')
        del _entry_name_split[:_entry_name_location]
        _entry_name = ' '.join(_entry_name_split)
    if _entry_name.startswith('/'):
        return _entry_name.replace('/', '', 1)
    else:
        return _entry_name.strip()


def string_gen(_complexity, _length):  # generates and returns a random string based on input
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


def pass_gen():  # prompts the user for necessary information to generate a password and passes it to string_gen
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
    if _complexity != 's' and _complexity != 'S':
        _complexity = 'c'
    _gen = string_gen(_complexity.lower(), _length)
    return _gen


def shm_gen(_tmp_dir=expanduser('~/.config/sshyp/tmp/')):  # creates a temporary directory for entry editing
    _shm_folder_gen = string_gen('f', randint(12, 48))
    _shm_entry_gen = string_gen('f', randint(12, 48))
    Path(_tmp_dir + _shm_folder_gen).mkdir(mode=0o700)
    return _shm_folder_gen, _shm_entry_gen


def encrypt(_entry_dir, _shm_folder, _shm_entry, _gpg_id, _tmp_dir=expanduser('~/.config/sshyp/tmp/')):
    # encrypts an entry and cleans up the temporary files
    run(['gpg', '-qr', str(_gpg_id), '-e', f"{_tmp_dir}{_shm_folder}/{_shm_entry}"])
    move(f"{_tmp_dir}{_shm_folder}/{_shm_entry}.gpg", f"{_entry_dir}.gpg")
    rmtree(f"{_tmp_dir}{_shm_folder}")


def decrypt(_entry_dir, _shm_folder, _shm_entry, _quick_pass,
            _tmp_dir=expanduser('~/.config/sshyp/tmp/')):  # decrypts an entry to a temporary directory
    if not isinstance(_quick_pass, bool):
        _unlock_method = ['gpg', '--pinentry-mode', 'loopback', '--passphrase', _quick_pass, '-qd', '--output']
    else:
        _unlock_method = ['gpg', '-qd', '--output']
    if _shm_folder == 0 and _shm_entry == 0:
        _output_target = ['/dev/null', expanduser('~/.config/sshyp/lock.gpg')]
    else:
        _output_target = [f"{_tmp_dir}{_shm_folder}/{_shm_entry}", f"{_entry_dir}.gpg"]
    try:
        run(_unlock_method + _output_target, stderr=DEVNULL, check=True)
    except CalledProcessError:
        if not isinstance(_quick_pass, bool):
            print('\n\u001b[38;5;9merror: quick-unlock failed as a result of an incorrect passphrase, an unreachable '
                  'sshyp server, or an invalid configuration\n\nfalling back to standard unlock\u001b[0m\n')
            try:
                run(['gpg', '-qd', '--output'] + _output_target, stderr=DEVNULL, check=True)
            except CalledProcessError:
                print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
                s_exit(5)
        else:
            print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
            s_exit(5)


def determine_decrypt(_entry_dir, _shm_folder, _shm_entry):
    if quick_unlock_enabled == 'y':
        decrypt(_entry_dir, _shm_folder, _shm_entry, whitelist_verify(port, username_ssh, ip, client_device_id))
    else:
        decrypt(_entry_dir, _shm_folder, _shm_entry, False)


def optimized_edit(_lines, _edit_data, _edit_line):  # ensures an edited entry is optimized for best compatibility
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


def edit_note(_shm_folder, _shm_entry, _lines):  # edits the note attached to an entry
    _reg_lines = _lines[0:3]
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'w').writelines(_lines[3:])
    run([editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"])
    _new_notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n").readlines()
    while len(_reg_lines) < 3:
        _reg_lines.append('\n')
    _noted_lines = _reg_lines + _new_notes
    return _noted_lines


def copy_id_check(_port, _username_ssh, _ip, _client_device_id):
    # attempts to connect to the user's server via ssh to register the device for syncing
    try:
        run(['ssh', '-o', 'ConnectTimeout=3', '-i', expanduser('~/.ssh/sshyp'), '-p', _port, f"{_username_ssh}@{_ip}",
             f'python3 -c \'from pathlib import Path; Path("/home/{_username_ssh}/.config/sshyp/devices/'
             f'{_client_device_id}").touch(mode=0o400, exist_ok=True)\''], stderr=DEVNULL, check=True)
    except CalledProcessError:
        print('\n\u001b[38;5;9mwarning: ssh connection could not be made - ensure the public key (~/.ssh/sshyp.pub) is '
              'registered on the remote server and that the entered ip, port, and username are correct\n\nsyncing '
              'functionality will be disabled until this is addressed\u001b[0m\n')
        open(expanduser('~/.config/sshyp/ssh-error'), 'w').write('1')
        return 1
    open(expanduser('~/.config/sshyp/ssh-error'), 'w').write('0')
    return 0


# ARGUMENT-SPECIFIC FUNCTIONS

def tweak():  # runs configuration wizard
    from os import symlink
    _divider = f"\n{'=' * (get_terminal_size()[0] - int((.5 * get_terminal_size()[0])))}\n\n"

    # config directory creation
    Path(expanduser('~/.config/sshyp/devices')).mkdir(mode=0o700, parents=True, exist_ok=True)
    if not Path(f"{expanduser('~/.config/sshyp/tmp')}").exists():
        if uname()[0] == 'Haiku' or uname()[0] == 'FreeBSD':
            symlink('/tmp', expanduser('~/.config/sshyp/tmp'))
        elif Path("/data/data/com.termux").exists():
            symlink('/data/data/com.termux/files/usr/tmp', expanduser('~/.config/sshyp/tmp'))
        else:
            symlink('/dev/shm', expanduser('~/.config/sshyp/tmp'))

    # device type configuration
    _device_type = input('\nclient or server installation? (C/s) ')
    if _device_type.lower() == 's':
        _sshyp_data = ['server']
        Path(expanduser('~/.config/sshyp/deleted')).mkdir(mode=0o700, exist_ok=True)
        Path(expanduser('~/.config/sshyp/whitelist')).mkdir(mode=0o700, exist_ok=True)
        print(f"\n\u001b[4;1mmake sure the ssh service is running and properly configured\u001b[0m")
    else:
        _sshyp_data = ['client']
        Path(expanduser('~/.local/share/sshyp')).mkdir(mode=0o700, parents=True, exist_ok=True)

        # gpg configuration
        _gpg_gen = input(f"{_divider}sshyp requires the use of a unique gpg key - use an (e)xisting key or (g)enerate a"
                         f" new one? (E/g) ")
        if _gpg_gen.lower() != 'g':
            run(['gpg', '-k'])
            _sshyp_data.append(str(input('gpg key id: ')))
        else:
            print('\na unique gpg key is being generated for you...')
            if not Path(expanduser('~/.config/sshyp/gpg-gen')).is_file():
                open(expanduser('~/.config/sshyp/gpg-gen'), 'w').writelines([
                    'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
                    'Name-Comment: gpg-sshyp\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
            run(['gpg', '--batch', '--generate-key', expanduser('~/.config/sshyp/gpg-gen')])
            remove(expanduser('~/.config/sshyp/gpg-gen'))
            _sshyp_data.append(run(['gpg', '-k'], stdout=PIPE, text=True).stdout.split('\n')[-4].strip())

        # text editor configuration
        _sshyp_data.append(input(f"{_divider}example input: vim\n\npreferred text editor: "))

        # lock file generation
        if Path(expanduser('~/.config/sshyp/lock.gpg')).is_file():
            remove(expanduser('~/.config/sshyp/lock.gpg'))
        open(expanduser('~/.config/sshyp/lock'), 'w')
        run(['gpg', '-qr', str(_sshyp_data[1]), '-e', expanduser('~/.config/sshyp/lock')])
        remove(expanduser('~/.config/sshyp/lock'))

        # ssh key configuration
        _offline_mode = False
        _ssh_gen = (input(f"{_divider}make sure the ssh service on the remote server is running and properly "
                          f"configured\n\nsync support requires a unique ssh key - would you like to have this "
                          f"automatically generated? (Y/n/o(ffline)) "))
        if _ssh_gen.lower() != 'n' and _ssh_gen.lower() != 'o' and _ssh_gen.lower() != 'offline':
            Path(f"{expanduser('~')}/.ssh").mkdir(mode=0o700, exist_ok=True)
            run(['ssh-keygen', '-t', 'ed25519', '-f', expanduser('~/.ssh/sshyp')])
        elif _ssh_gen.lower() == 'n':
            print(f"\n\u001b[4;1mensure that the key file you are using is located at "
                  f"{expanduser('~/.ssh/sshyp')}\u001b[0m")
        elif _ssh_gen.lower() == 'o' or _ssh_gen.lower() == 'offline':
            _offline_mode = True
            print('\nsshyp has been set to offline mode - to enable syncing, run "sshyp tweak" again')

        if not _offline_mode:
            # ssh ip+port configuration
            _ip_port = str(input(f"{_divider}example input: 10.10.10.10:9999\n\nip and ssh port of sshyp server: "))
            _ip, _sep, _port = _ip_port.partition(':')

            # ssh user configuration
            _username_ssh = str(input('\nusername of the remote server: '))

            # sshync profile generation
            make_profile(expanduser('~/.config/sshyp/sshyp.sshync'),
                         expanduser('~/.local/share/sshyp/'), f"/home/{_username_ssh}/.local/share/sshyp/",
                         expanduser('~/.ssh/sshyp'), _ip, _port, _username_ssh)

            # device id configuration
            for _id in listdir(expanduser('~/.config/sshyp/devices')):  # remove existing device id
                remove(f"{expanduser('~/.config/sshyp/devices/')}{_id}")
            print(f"{_divider}\u001b[4;1mimportant:\u001b[0m this id \u001b[4;1mmust\u001b[0m be unique amongst your "
                  f"client devices\n\nthis is used to keep track of database syncing and quick-unlock permissions\n")
            _device_id_prefix = str(input('device id: ')) + '-'
            _device_id_suffix = string_gen('f', randint(24, 48))
            _device_id = _device_id_prefix + _device_id_suffix
            open(f"{expanduser('~/.config/sshyp/devices/')}{_device_id}", 'w')

            # quick-unlock configuration
            print(f"{_divider}this allows you to use a shorter version of your gpg key password and\n"
                  f"requires a constant connection to your sshyp server to authenticate")
            _sshyp_data.append(input('\nenable quick-unlock? (y/N) ').lower())
            if _sshyp_data[3] == 'y':
                print(f"\nquick-unlock has been enabled client-side - in order for this device to be able to read "
                      f"entries,\nyou must first login to the sshyp server and run:\n\nsshyp whitelist setup "
                      f"(if not already done)\nsshyp whitelist add '{_device_id}'")

            # test server connection and attempt to register device id
            copy_id_check(_port, _username_ssh, _ip, _device_id)

        elif Path(expanduser('~/.config/sshyp/sshyp.sshync')).is_file():
            remove(expanduser('~/.config/sshyp/sshyp.sshync'))

    # write main config file (sshyp-data)
    with open(expanduser('~/.config/sshyp/sshyp-data'), 'w') as _config_file:
        _lines = 0
        for _item in _sshyp_data:
            _lines += 1
            _config_file.write(_item + '\n')
        while _lines < 4:
            _lines += 1
            _config_file.write('n')
    print(f"{_divider}configuration complete\n")


def print_info():  # prints help text based on argument
    if argument_list[1] == 'help' or argument_list[1] == '--help' or argument_list[1] == '-h':
        print('\n\u001b[1msshyp  copyright (c) 2021-2023  randall winkhart\u001b[0m\n')
        print("this is free software, and you are welcome to redistribute it under certain conditions;\nthis program "
              "comes with absolutely no warranty;\ntype 'sshyp license' for details")
        if device_type == 'client':
            print('\n\u001b[1musage:\u001b[0m sshyp [option [flag] [<entry name>]] | [/<entry name>]\n')
            print('\u001b[1moptions:\u001b[0m')
            print('help/--help/-h           bring up this menu')
            print('version/-v               display sshyp version info')
            print('tweak                    configure sshyp')
            print('add                      add an entry')
            print('gen                      generate a new password')
            print('edit                     edit an existing entry')
            print('copy                     copy details of an entry to your clipboard')
            print('shear/-rm                delete an existing entry')
            print('sync/-s                  manually sync the entry directory via sshync')
            print('\n\u001b[1mflags:\u001b[0m')
            print('add:')
            print(' password/-p             add a password entry')
            print(' note/-n                 add a note entry')
            print(' folder/-f               add a new folder for entries')
            print('edit:')
            print(' rename/relocate/-r      rename or relocate an entry')
            print(' username/-u             change the username of an entry')
            print(' password/-p             change the password of an entry')
            print(' url/-l                  change the url attached to an entry')
            print(' note/-n                 change the note attached to an entry')
            print('copy:')
            print(' username/-u             copy the username of an entry to your clipboard')
            print(' password/-p             copy the password of an entry to your clipboard')
            print(' url/-l                  copy the url of an entry to your clipboard')
            print(' note/-n                 copy the note of an entry to your clipboard')
            print('gen:')
            print(' update/-u               generate a password for an existing entry')
            print("\n\u001b[1mtip:\u001b[0m you can quickly read an entry with 'sshyp /<entry name>'\n")
        else:
            print('\n\u001b[1musage:\u001b[0m sshyp [option [flag] [<device id>]]\n')
            print('\u001b[1moptions:\u001b[0m')
            print('help/--help/-h           bring up this menu')
            print('version/-v               display sshyp version info')
            print('tweak                    configure sshyp')
            print('whitelist                manage the quick-unlock whitelist')
            print('\n\u001b[1mflags:\u001b[0m')
            print('whitelist:')
            print(' setup                   set up the quick-unlock whitelist')
            print(' list/-l                 view all registered device ids and their quick-unlock whitelist status')
            print(' add                     whitelist a device id for quick-unlock')
            print(' delete/del              remove a device id from the quick-unlock whitelist\n')
    elif argument_list[1] == 'version' or argument_list[1] == '-v':
        print('\nsshyp is a simple, self-hosted, sftp-synchronized password manager\nfor unix(-like) systems (haiku/'
              'freebsd/linux/termux)\n\nsshyp is a viable alternative to (and compatible with) pass/password-store\n')
        print("                ..       \u001b[38;5;9m♥♥ ♥♥\u001b[0m       ..\n         .''.''/()\\     \u001b[38;5;10m"
              "♥♥♥♥♥♥♥\u001b[0m     /()\\''.''.\n        *       :        \u001b[38;5;9m♥♥♥♥♥\u001b[0m        :       *"
              "\n         `..'..'          \u001b[38;5;10m♥♥♥\u001b[0m          `..'..'\n         //   \\\\           "
              "\u001b[38;5;9m♥\u001b[0m           //   \\\\")
        print('\u001b[38;5;7;48;5;8m<><><><><><><><><><><><><><><><><><><><><><><><><><><><>\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                                                      '
              '\u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m   \u001b[38;5;15;48;5;8msshyp  copyright (c) 2021-2023  '
              'randall winkhart\u001b[38;5;15;48;5;15m   \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                                                      '
              '\u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                    \u001b[38;5;15;48;5;8mversion 1.3.0'
              '\u001b[38;5;15;48;5;15m                     \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m             \u001b[38;5;15;48;5;8mthe serious shepherd '
              'update\u001b[38;5;15;48;5;15m              \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                                                      '
              '\u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m<><><><><><><><><><><><><><><><><><><><><><><><><><><><>\u001b[0m\n')
        print('see https://github.com/rwinkhart/sshyp for more information\n')
    elif argument_list[1] == 'license':
        print('\nThis program is free software: you can redistribute it and/or modify it under the terms\nof version 3 '
              '(only) of the GNU General Public License as published by the Free Software Foundation.\n\nThis program '
              'is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;\nwithout even the implied '
              'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\nSee the GNU General Public License for'
              ' more details.\n\nhttps://opensource.org/licenses/GPL-3.0\n')
    elif argument_list[1] == 'add':
        print('\n\u001b[1musage:\u001b[0m sshyp add [flag [<entry name>]]\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('add:')
        print(' password/-p             add a password entry')
        print(' note/-n                 add a note entry')
        print(' folder/-f               add a new folder for entries\n')
    elif argument_list[1] == 'edit':
        print('\n\u001b[1musage:\u001b[0m sshyp edit [flag [<entry name>]]\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('edit:')
        print(' rename/relocate/-r      rename or relocate an entry')
        print(' username/-u             change the username of an entry')
        print(' password/-p             change the password of an entry')
        print(' url/-l                  change the url attached to an entry')
        print(' note/-n                 change the note attached to an entry\n')
    elif argument_list[1] == 'copy':
        print('\n\u001b[1musage:\u001b[0m sshyp copy [flag [<entry name>]]\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('copy:')
        print(' username/-u             copy the username of an entry to your clipboard')
        print(' password/-p             copy the password of an entry to your clipboard')
        print(' url/-l                  copy the url of an entry to your clipboard')
        print(' note/-n                 copy the note of an entry to your clipboard\n')
    elif argument_list[1] == 'whitelist':
        if device_type == 'server':
            print('\n\u001b[1musage:\u001b[0m sshyp whitelist [flag [<device id>]]\u001b[0m\n')
            print('\u001b[1mflags:\u001b[0m')
            print('whitelist:')
            print(' setup                   set up the quick-unlock whitelist')
            print(' list/-l                 view all registered device ids and their quick-unlock whitelist status')
            print(' add                     whitelist a device id for quick-unlock')
            print(' delete/del              remove a device id from the quick-unlock whitelist\n')
        else:
            print('\n\u001b[38;5;9merror: argument (whitelist) only available on server\u001b[0m\n')
    s_exit(0)


def no_arg():  # displays a list of entries and gives an option to select one for viewing
    print("\nfor a list of usable commands, run 'sshyp help'")
    _entry_name = entry_name_fetch('entry to read: ')
    if not Path(f"{directory}{_entry_name}.gpg").exists():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(3)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    rmtree(f"{tmp_dir}{_shm_folder}")


def read_shortcut():  # shortcut to quickly read an entry
    if not Path(f"{directory}{argument.replace('/', '', 1)}.gpg").exists():
        print(f"\n\u001b[38;5;9merror: entry ({argument.replace('/', '', 1)}) does not exist\u001b[0m\n")
        s_exit(3)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + argument.replace('/', '', 1), _shm_folder, _shm_entry)
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    rmtree(f"{tmp_dir}{_shm_folder}")


def sync():  # calls sshync to sync changes to the user's server
    print('\nsyncing entries with the server device...\n')
    # set permissions before uploading
    for _root, _dirs, _files in walk(expanduser('~/.local/share/sshyp')):
        for _path in _root.split('\n'):
            chmod(_path, 0o700)
        for _file in _files:
            chmod(_root + '/' + _file, 0o600)
    run_profile(expanduser('~/.config/sshyp/sshyp.sshync'), silent_sync)


def whitelist_setup():  # takes input from the user to set up quick-unlock password
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
    open(expanduser('~/.config/sshyp/gpg-gen'), 'w').writelines([
        'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
        'Name-Comment: gpg-sshyp-whitelist\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
    run(['gpg', '-q', '--pinentry-mode', 'loopback', '--batch', '--generate-key', '--passphrase',
         _quick_unlock_password, expanduser('~/.config/sshyp/gpg-gen')])
    remove(expanduser('~/.config/sshyp/gpg-gen'))
    _gpg_id = run(['gpg', '-k'], stdout=PIPE, text=True).stdout.split('\n')[-4].strip()

    # encrypt excluded with the assembly key
    _shm_folder, _shm_entry = shm_gen()
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').write(_quick_unlock_password_excluded)
    encrypt(expanduser('~/.config/sshyp/excluded'), _shm_folder, _shm_entry, _gpg_id)
    print(f"\nyour quick-unlock passphrase: {_quick_unlock_password}")


def whitelist_verify(_port, _username_ssh, _ip, _client_device_id):
    # checks the user's whitelist status and fetches the full gpg key password if possible
    try:
        run(['gpg', '--pinentry-mode', 'cancel', '-qd', '--output', '/dev/null',
             expanduser('~/.config/sshyp/lock.gpg')], stderr=DEVNULL, check=True)
        return False
    except CalledProcessError:
        _i, _full_password = 0, ''
        _server_whitelist = run(['ssh', '-i', expanduser('~/.ssh/sshyp'), '-p', _port, f"{_username_ssh}@{_ip}",
                                 f'python3 -c \'from os import listdir; print(*listdir("/home/{_username_ssh}'
                                 f'/.config/sshyp/whitelist"))\''], stdout=PIPE, text=True).stdout.rstrip().split(' ')
        for _device_id in _server_whitelist:
            if _device_id == _client_device_id:
                from getpass import getpass
                _quick_unlock_password = getpass(prompt='\nquick-unlock passphrase: ')
                _quick_unlock_password_excluded = \
                    run(['ssh', '-i', expanduser('~/.ssh/sshyp'), '-p',  _port, f"{_username_ssh}@{_ip}",
                         f"gpg --pinentry-mode loopback --passphrase '{_quick_unlock_password}' "
                         f"-qd ~/.config/sshyp/excluded.gpg"], stdout=PIPE, text=True).stdout.rstrip()
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


def whitelist_list():  # shows the quick-unlock whitelist status of device ids
    _whitelisted_ids = listdir(expanduser('~/.config/sshyp/whitelist'))
    _device_ids = listdir(expanduser('~/.config/sshyp/devices'))
    print('\n\u001b[1mquick-unlock whitelisted device ids:\u001b[0m')
    for _id in _whitelisted_ids:
        print(_id)
    print('\n\u001b[1mother registered device ids:\u001b[0m')
    for _id in _device_ids:
        if _id not in _whitelisted_ids:
            print(_id)
    print()


def whitelist_manage():  # adds or removes quick-unlock whitelisted device ids
    if len(argument_list) == 3:
        whitelist_list()
        _device_id = input('device id: ')
    else:
        _argument_split = argument.split(' ')
        del _argument_split[:2]
        _device_id = ' '.join(_argument_split)

    if argument_list[2] == 'add':
        if _device_id in listdir(expanduser('~/.config/sshyp/devices')):
            open(expanduser(f"~/.config/sshyp/whitelist/{_device_id}"), 'w').write('')
            whitelist_list()
        else:
            print(f"\n\u001b[38;5;9merror: device id ({_device_id}) is not registered\u001b[0m\n")
            s_exit(2)

    elif Path(expanduser(f"~/.config/sshyp/whitelist/{_device_id}")).is_file():
        remove(expanduser(f"~/.config/sshyp/whitelist/{_device_id}"))
        whitelist_list()


def add_entry():  # adds a new entry
    _shm_folder, _shm_entry = None, None  # sets base-line values to avoid errors
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('name of new entry: ')
    else:
        _entry_name = entry_name_fetch(2)
    if Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) already exists\u001b[0m\n")
        s_exit(4)
    if argument_list[2] == 'note' or argument_list[2] == '-n':
        _shm_folder, _shm_entry = shm_gen()
        run([editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"])
        _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(optimized_edit(['', '', '', _notes], None, -1))
    elif argument_list[2] == 'password' or argument_list[2] == '-p':
        _username = str(input('username: '))
        _password = str(input('password: '))
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
        _shm_folder, _shm_entry = shm_gen()
        if _add_note.lower() == 'y':
            run([editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"])
            _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        else:
            _notes = ''
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w')\
            .writelines(optimized_edit([_password, _username, _url, _notes], None, -1))
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg_id)


def add_folder():  # creates a new folder
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('name of new folder: ')
    else:
        _entry_name = entry_name_fetch(2)
    Path(directory + _entry_name).mkdir(mode=0o700, parents=True, exist_ok=True)
    if ssh_error != 1:
        run(['ssh', '-i', expanduser('~/.ssh/sshyp'), '-p', port, f"{username_ssh}@{ip}",
             f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{_entry_name}")'
             f'.mkdir(mode=0o700, parents=True, exist_ok=True)\''])


def rename():  # renames an entry or folder
    from shutil import copy
    if argument == 'edit rename' or argument == 'edit relocate' or argument == 'edit -r':
        _entry_name = entry_name_fetch('entry/folder to rename/relocate: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file() and not Path(f"{directory}{_entry_name}").is_dir():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(3)
    _new_name = entry_name_fetch('new name: ')
    if Path(f"{directory}{_new_name}.gpg").is_file() or Path(f"{directory}{_new_name}").is_dir():
        print(f"\n\u001b[38;5;9merror: ({_new_name}) already exists\u001b[0m\n")
        s_exit(4)
    if _entry_name.endswith('/'):
        if ssh_error != 1:
            Path(f"{directory}{_new_name}").mkdir(mode=0o700, parents=True, exist_ok=True)
            run(['ssh', '-i', expanduser('~/.ssh/sshyp'), '-p', port, f"{username_ssh}@{ip}",
                 f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{_new_name}")'
                 f'.mkdir(mode=0o700, parents=True, exist_ok=True)\''])
        else:
            move(f"{directory}{_entry_name}", f"{directory}{_new_name}")
    else:
        if ssh_error != 1:
            copy(f"{directory}{_entry_name}.gpg", f"{directory}{_new_name}.gpg")
        else:
            move(f"{directory}{_entry_name}.gpg", f"{directory}{_new_name}.gpg")
    if ssh_error != 1:
        run(['ssh', '-i', expanduser('~/.ssh/sshyp'), '-p', port, f"{username_ssh}@{ip}",
             f'cd /lib/sshyp; python3 -c \'from sshync import delete; delete("{_entry_name}", "remotely")\''])


def edit():  # edits the contents of an entry
    _shm_folder, _shm_entry, _detail, _edit_line = None, None, None, None  # sets values to avoid PEP8 warnings
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('entry to edit: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(3)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
    if argument_list[2] == 'username' or argument_list[2] == '-u':
        _detail, _edit_line = str(input('username: ')), 1
    elif argument_list[2] == 'password' or argument_list[2] == '-p':
        _detail, _edit_line = str(input('password: ')), 0
    elif argument_list[2] == 'url' or argument_list[2] == '-l':
        _detail, _edit_line = str(input('url: ')), 2
    if argument_list[2] == 'note' or argument_list[2] == '-n':
        _edit_line = 2
        _new_lines = optimized_edit(edit_note(_shm_folder, _shm_entry,
                                              open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines()), None, -1)
    else:
        _new_lines = optimized_edit(open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), _detail, _edit_line)
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_new_lines)
    remove(f"{directory}{_entry_name}.gpg")
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg_id)


def gen():  # generates a password for a new or an existing entry
    _username, _url, _notes = None, None, None  # sets base-line values to avoid errors
    if argument == 'gen update' or argument == 'gen -u' or argument == 'gen':
        _entry_name = entry_name_fetch('name of entry: ')
    elif argument_list[2] == 'update' or argument_list[2] == '-u':
        _entry_name = entry_name_fetch(2)
        if not Path(f"{directory}{_entry_name}.gpg").is_file():
            print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
            s_exit(3)
    else:
        _entry_name = entry_name_fetch(1)
    if len(argument_list) == 2 or (not argument_list[2] == 'update' and not argument_list[2] == '-u'):
        if Path(f"{directory}{_entry_name}.gpg").is_file():
            print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) already exists\u001b[0m\n")
            s_exit(4)
        _username = str(input('username: '))
        _password = pass_gen()
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
        _shm_folder, _shm_entry = shm_gen()
        if _add_note.lower() == 'y':
            run([editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"])
            _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        else:
            _notes = ''
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w')\
            .writelines(optimized_edit([_password, _username, _url, _notes], None, -1))
    else:
        _shm_folder, _shm_entry = shm_gen()
        determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
        _new_lines = optimized_edit(open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), pass_gen(), 0)
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_new_lines)
        remove(f"{directory}{_entry_name}.gpg")
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg_id)


def copy_data():  # copies a specified field of an entry to the clipboard
    from subprocess import Popen
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('entry to copy: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(3)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
    _copy_line, _index = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), 0
    if argument_list[2] == 'username' or argument_list[2] == '-u':
        _index = 1
    elif argument_list[2] == 'password' or argument_list[2] == '-p':
        _index = 0
    elif argument_list[2] == 'url' or argument_list[2] == '-l':
        _index = 2
    elif argument_list[2] == 'note' or argument_list[2] == '-n':
        _index = 3
    if 'WAYLAND_DISPLAY' in environ:  # Wayland clipboard detection
        run(['wl-copy', _copy_line[_index].rstrip()])
        Popen('sleep 30; wl-copy -c', shell=True)
    elif uname()[0] == 'Haiku':  # Haiku clipboard detection
        run(['clipboard', '-c', _copy_line[_index].rstrip()])
        Popen('sleep 30; clipboard -r', shell=True)
    elif Path("/data/data/com.termux").exists():  # Termux (Android) clipboard detection
        run(['termux-clipboard-set', _copy_line[_index].rstrip()])
        Popen("sleep 30; termux-clipboard-set ''", shell=True)
    else:  # X11 clipboard detection
        run(['xclip', '-sel', 'c'], stdin=Popen(['echo', '-n', _copy_line[_index].rstrip()], stdout=PIPE).stdout)
        Popen("sleep 30; echo -n '' | xclip -sel c", shell=True)
    rmtree(f"{tmp_dir}{_shm_folder}")


def remove_data():  # deletes an entry from the server and flags it for local deletion on sync
    if argument == 'shear' or argument == '-rm':
        _entry_name = entry_name_fetch('entry/folder to shear: ')
    else:
        _entry_name = entry_name_fetch(1)
    determine_decrypt(expanduser('~/.config/sshyp/lock.gpg'), 0, 0)
    if ssh_error != 1:
        run(['ssh', '-i', expanduser('~/.ssh/sshyp'), '-p', port, f"{username_ssh}@{ip}",
             f'cd /lib/sshyp; python3 -c \'from sshync import delete; delete("{_entry_name}", "remotely")\''])
    else:
        offline_delete(_entry_name, 'locally')


if __name__ == "__main__":
    try:
        silent_sync, ssh_error = 0, 0
        # retrieve typed argument
        argument_list = argv
        argument = ' '.join(argument_list[1:])

        # import saved userdata
        device_type = ''
        if argument != 'tweak':
            tmp_dir = expanduser('~/.config/sshyp/tmp/')
            try:
                sshyp_data = open(expanduser('~/.config/sshyp/sshyp-data')).readlines()
                device_type = sshyp_data[0].rstrip()
                if device_type == 'client':
                    directory = expanduser('~/.local/share/sshyp/')
                    gpg_id = sshyp_data[1].rstrip()
                    editor = sshyp_data[2].rstrip()
                    quick_unlock_enabled = sshyp_data[3].rstrip()
                    if Path(expanduser('~/.config/sshyp/sshyp.sshync')).is_file():
                        ssh_info = get_profile(expanduser('~/.config/sshyp/sshyp.sshync'))
                        username_ssh = ssh_info[0].rstrip()
                        ip = ssh_info[1].rstrip()
                        port = ssh_info[2].rstrip()
                        directory_ssh = str(ssh_info[4].rstrip())
                        client_device_id = listdir(expanduser('~/.config/sshyp/devices'))[0].rstrip()
                        ssh_error = int(open(expanduser('~/.config/sshyp/ssh-error')).read().rstrip())
                        if ssh_error != 0:
                            ssh_error = copy_id_check(port, username_ssh, ip, client_device_id)
                    else:
                        ssh_error = 1
                elif len(argument_list) <= 1 or (argument_list[1] != "help" and argument_list[1] != "--help" and
                                                 argument_list[1] != "-h" and argument_list[1] != "license" and
                                                 argument_list[1] != "version" and argument_list[1] != "-v" and
                                                 argument_list[1] != "whitelist"):
                    print(f"\n\u001b[38;5;9merror: invalid server argument - run 'sshyp help' to "
                          f"list usable commands\u001b[0m\n")
                    s_exit(1)
            except (FileNotFoundError, IndexError):
                print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print("not all necessary configuration files are present - please run 'sshyp tweak'")
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
                s_exit(2)
        else:
            tweak()
            s_exit(0)

        # run function based on arguments
        if argument.startswith('/'):
            read_shortcut()
        elif argument == '':
            no_arg()
        elif argument == 'help' or argument == '--help' or argument == '-h' or argument == 'license' or argument \
                == 'version' or argument == '-v':
            print_info()
        elif argument_list[1] == 'whitelist':
            if device_type == 'server':
                if len(argument_list) == 2:
                    print_info()
                elif argument_list[2] == 'list' or argument_list[2] == '-l':
                    whitelist_list()
                elif argument_list[2] == 'add' or argument_list[2] == 'delete' or argument_list[2] == 'del':
                    whitelist_manage()
                elif argument_list[2] == 'setup':
                    whitelist_setup()
                else:
                    print_info()
            else:
                print_info()
        elif argument_list[1] == 'add':
            if len(argument_list) == 2:
                print_info()
            elif argument_list[2] == 'note' or argument_list[2] == '-n' or argument_list[2] == 'password' or \
                    argument_list[2] == '-p':
                add_entry()
            elif argument_list[2] == 'folder' or argument_list[2] == '-f':
                add_folder()
            else:
                print_info()
        elif argument_list[1] == 'edit':
            if len(argument_list) == 2:
                print_info()
            elif argument_list[2] == 'rename' or argument_list[2] == 'relocate' or argument_list[2] == '-r':
                silent_sync = 1
                rename()
            elif argument_list[2] == 'username' or argument_list[2] == '-u' or argument_list[2] == 'password' or \
                    argument_list[2] == '-p' or argument_list[2] == 'url' or argument_list[2] == '-l' or \
                    argument_list[2] == 'note' or argument_list[2] == '-n':
                edit()
            else:
                print_info()
        elif argument_list[1] == 'gen':
            gen()
        elif argument_list[1] == 'copy':
            if len(argument_list) == 2:
                print_info()
            elif argument_list[2] == 'username' or argument_list[2] == '-u' or argument_list[2] == 'password' or \
                    argument_list[2] == '-p' or argument_list[2] == 'url' or argument_list[2] == '-l' or \
                    argument_list[2] == 'note' or argument_list[2] == '-n':
                try:
                    copy_data()
                except IndexError:
                    print(f"\n\u001b[38;5;9merror: field does not exist in entry\u001b[0m\n")
                    s_exit(3)
            else:
                print_info()
        elif argument_list[1] == 'shear' or argument_list[1] == '-rm':
            remove_data()
        elif argument_list[1] != 'sync' and argument_list[1] != '-s':
            print(f"\n\u001b[38;5;9merror: invalid argument - run 'sshyp help' to list usable commands\u001b[0m\n")
            s_exit(1)

        # sync if any changes were made
        if len(argument_list) > 1 and ssh_error == 0 \
                and ((argument_list[1] == 'sync' or argument_list[1] == '-s' or argument_list[1] == 'gen' or
                      argument_list[1] == 'shear' or argument_list[1] == '-rm') or
                     ((argument_list[1] == 'add' or argument_list[1] == 'edit') and len(argument_list) > 2)):
            sync()

    except KeyboardInterrupt:
        print('\n')
