#!/usr/bin/env python3

# external modules

from os import environ, listdir, path, remove, system, uname, walk
from pathlib import Path
from random import randint, SystemRandom
from shutil import get_terminal_size, move, rmtree
import sshync
from subprocess import CalledProcessError, Popen, PIPE, run
from sys import argv, exit as s_exit


# BELOW - utility functions

def entry_list_gen(_directory=path.expanduser('~/.local/share/sshyp/')):  # generates and prints full entry list
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
    for _root, _directories, _files in walk(_directory):
        for _dir in sorted(_directories):
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
        return _entry_name


def string_gen(_complexity, _length):  # generates and returns a random string based on input
    import string
    if _complexity == 's':
        _character_pool = string.ascii_letters + string.digits
    else:
        _character_pool = string.printable.replace('/', '').replace('\\', '')
    _gen = ''.join(SystemRandom().choice(_character_pool) for _ in range(_length))
    _min_special, _special = round(.2 * _length), 0
    for _character in _gen:
        if not _character.isalpha():
            _special += 1
    if _special < _min_special:
        _gen = string_gen(_complexity, _length)
    return _gen


def pass_gen():  # prompts the user for necessary information to generate a password and passes it to string_gen
    try:
        _length = int(input('password length: '))
    except ValueError:
        print(f"\n\u001b[38;5;9merror: a non-integer value was input for password length\u001b[0m\n")
        _gen = pass_gen()
        return _gen
    if _length > 800:
        _length = 800
        print('\n\u001b[38;5;9mpassword length has been limited to the maximum of 800 characters\u001b[0m\n')
    _complexity = str(input('password complexity - simple (for compatibility) or complex (for security)? (s/C) '))
    _gen = string_gen(_complexity.lower(), _length)
    return _gen


def shm_gen(_tmp_dir=path.expanduser('~/.config/sshyp/tmp/')):  # creates a temporary directory for entry editing
    _shm_folder_gen = string_gen('s', randint(12, 48))
    _shm_entry_gen = string_gen('s', randint(12, 48))
    Path(_tmp_dir + _shm_folder_gen).mkdir(0o700)
    return _shm_folder_gen, _shm_entry_gen


def encrypt(_entry_dir, _shm_folder, _shm_entry, _gpg_com, _gpg_id, _tmp_dir=path.expanduser('~/.config/sshyp/tmp/')):
    # encrypts an entry and cleans up the temporary files
    system(f"{_gpg_com} -qr {str(_gpg_id)} -e '{_tmp_dir}{_shm_folder}/{_shm_entry}'")
    move(f"{_tmp_dir}{_shm_folder}/{_shm_entry}.gpg", f"{_entry_dir}.gpg")
    rmtree(f"{_tmp_dir}{_shm_folder}")


def decrypt(_entry_dir, _shm_folder, _shm_entry, _gpg_command, _tmp_dir=path.expanduser('~/.config/sshyp/tmp/')):
    # decrypts an entry to a temporary directory
    if _shm_folder == 0 and _shm_entry == 0:
        _command = f"{_gpg_command} -qd --output /dev/null {path.expanduser('~/.config/sshyp/lock.gpg')}"
    else:
        _command = f"{_gpg_command} -qd --output {_tmp_dir}{_shm_folder}/{_shm_entry} {_entry_dir}.gpg"
    try:
        run(_command, shell=True, stderr=PIPE, check=True, close_fds=True)
    except CalledProcessError:
        print(f"\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n")
        s_exit(1)


def optimized_edit(_lines, _edit_data, _edit_line):  # ensures an edited entry is optimized for best compatibility
    while len(_lines) < _edit_line + 1:
        _lines += ['\n']
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
    system(f"{editor} {tmp_dir}{_shm_folder}/{_shm_entry}-n")
    _new_notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n").readlines()
    while len(_reg_lines) < 3:
        _reg_lines += ['\n']
    _noted_lines = _reg_lines + _new_notes
    return _noted_lines


def copy_id_check(_port, _username_ssh, _ip, _client_device_id):
    # attempts to connect to the user's server via ssh to register the device for syncing
    _command = f"ssh -o ConnectTimeout=3 -i '{path.expanduser('~/.ssh/sshyp')}' -p {_port} {_username_ssh}@{_ip} " \
               f"\"touch '/home/{_username_ssh}/.config/sshyp/devices/{_client_device_id}'\""
    try:
        run(_command, shell=True, stderr=PIPE, check=True, close_fds=True)
    except CalledProcessError:
        print('\n\u001b[38;5;9mwarning: ssh connection could not be made - ensure the public key (~/.ssh/sshyp.pub) is '
              'registered on the remote server and that the entered ip, port, and username are correct\n\nsyncing '
              'functionality will be disabled until this is addressed\u001b[0m\n')
        open(path.expanduser('~/.config/sshyp/ssh-error'), 'w').write('1')
        return 1
    open(path.expanduser('~/.config/sshyp/ssh-error'), 'w').write('0')
    return 0

# BELOW - argument-specific functions


def tweak():  # runs configuration wizard
    _divider = f"\n{'=' * (get_terminal_size()[0] - int((.5 * get_terminal_size()[0])))}\n\n"

    # config directory creation
    Path(path.expanduser('~/.config/sshyp/devices')).mkdir(0o700, parents=True, exist_ok=True)
    if not Path(f"{path.expanduser('~/.config/sshyp/tmp')}").exists():
        if uname()[0] == 'Haiku' or uname()[0] == 'FreeBSD':
            system(f"ln -s /tmp {path.expanduser('~/.config/sshyp/tmp')}")
        elif Path("/data/data/com.termux").exists():
            system(f"ln -s '/data/data/com.termux/files/usr/tmp' {path.expanduser('~/.config/sshyp/tmp')}")
        else:
            system(f"ln -s /dev/shm {path.expanduser('~/.config/sshyp/tmp')}")

    # device type configuration
    _device_type = input('\nclient or server installation? (C/s) ')
    if _device_type.lower() == 's':
        _sshyp_data = ['server']
        Path(path.expanduser('~/.config/sshyp/deleted')).mkdir(0o700, exist_ok=True)
        Path(path.expanduser('~/.config/sshyp/whitelist')).mkdir(0o700, exist_ok=True)
        print(f"\n\u001b[4;1mmake sure the ssh service is running and properly configured\u001b[0m")
    else:
        _sshyp_data = ['client']
        Path(path.expanduser('~/.local/share/sshyp')).mkdir(0o700, parents=True, exist_ok=True)

        # gpg configuration
        _gpg_gen = input(f"{_divider}sshyp requires the use of a unique gpg key - use an (e)xisting key or (g)enerate a"
                         f" new one? (E/g) ")
        if _gpg_gen.lower() != 'g':
            system(f"{gpg} -k")
            _sshyp_data += [str(input('gpg key id: '))]
        else:
            print('\na unique gpg key is being generated for you...')
            if not Path(path.expanduser('~/.config/sshyp/gpg-gen')).is_file():
                open(path.expanduser('~/.config/sshyp/gpg-gen'), 'w').writelines([
                    'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
                    'Name-Comment: gpg-sshyp\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
            if uname()[0] == 'Haiku':
                run(gpg + ' --batch --generate-key --passphrase ' + "'" +
                    input('\ngpg passphrase: ') + "'" + " '" +
                    path.expanduser('~/.config/sshyp/gpg-gen') + "'", shell=True)
            else:
                run(f"{gpg} --batch --generate-key '{path.expanduser('~/.config/sshyp/gpg-gen')}'", shell=True)
            remove(path.expanduser('~/.config/sshyp/gpg-gen'))
            _sshyp_data += [run(f"{gpg} -k", shell=True, stdout=PIPE, text=True).stdout.split('\n')[-4].strip()]

        # text editor configuration
        _sshyp_data += [input(f"{_divider}example input: vim\n\npreferred text editor: ")]

        # lock file generation
        if Path(path.expanduser('~/.config/sshyp/lock.gpg')).is_file():
            remove(path.expanduser('~/.config/sshyp/lock.gpg'))
        open(path.expanduser('~/.config/sshyp/lock'), 'w')
        system(f"{gpg} -qr {str(_sshyp_data[1])} -e {path.expanduser('~/.config/sshyp/lock')}")
        remove(path.expanduser('~/.config/sshyp/lock'))

        # ssh key configuration
        _offline_mode = False
        _ssh_gen = (input(f"{_divider}make sure the ssh service on the remote server is running and properly "
                          f"configured\n\nsync support requires a unique ssh key - would you like to have this "
                          f"automatically generated? (Y/n/o(ffline)) "))
        if _ssh_gen.lower() != 'n' and _ssh_gen.lower() != 'o' and _ssh_gen.lower() != 'offline':
            if uname()[0] == 'Haiku':
                Path(f"{path.expanduser('~')}/.ssh").mkdir(0o700, exist_ok=True)
            system('ssh-keygen -t ed25519 -f ~/.ssh/sshyp')
        elif _ssh_gen.lower() == 'n':
            print(f"\n\u001b[4;1mensure that the key file you are using is located at "
                  f"{path.expanduser('~/.ssh/sshyp')}\u001b[0m")
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
            sshync.make_profile(path.expanduser('~/.config/sshyp/sshyp.sshync'),
                                path.expanduser('~/.local/share/sshyp/'), f"/home/{_username_ssh}/.local/share/sshyp/",
                                path.expanduser('~/.ssh/sshyp'), _ip, _port, _username_ssh)

            # device id configuration
            for _id in listdir(path.expanduser('~/.config/sshyp/devices')):  # remove existing device id
                remove(f"{path.expanduser('~/.config/sshyp/devices/')}{_id}")
            print(f"{_divider}\u001b[4;1mimportant:\u001b[0m this id \u001b[4;1mmust\u001b[0m be unique amongst your "
                  f"client devices\n\nthis is used to keep track of database syncing and quick-unlock permissions\n")
            _device_id_prefix = str(input('device id: '))
            _device_id_suffix = string_gen('c', randint(12, 48))
            _device_id = _device_id_prefix + _device_id_suffix
            open(f"{path.expanduser('~/.config/sshyp/devices/')}{_device_id}", 'w')

            # quick-unlock configuration
            print(f"{_divider}\nthis allows you to use a shorter version of your gpg key password and\n"
                  f"requires a constant connection to your sshyp server to authenticate\n")
            _quick_unlock_enabled = input('enable quick-unlock? (y/N)')
            if _quick_unlock_enabled.lower() == 'y':
                _sshyp_data += ['quick']
                _sshyp_data += [int(input('this must be half the number of characters in your gpg key password or '
                                          'shorter\n\nquick-unlock key length: '))]
                print(f"\nquick-unlock has been enabled client-side - in order for this device to be able to read "
                      f"entries,\nyou must first login to the sshyp server and run:\n\nsshyp whitelist add "
                      f"{_device_id}")
            else:
                _sshyp_data += ['slow'], 0

            # test server connection and attempt to register device id
            copy_id_check(_port, _username_ssh, _ip, _device_id)

        elif Path(path.expanduser('~/.config/sshyp/sshyp.sshync')).is_file():
            remove(path.expanduser('~/.config/sshyp/sshyp.sshync'))

    # write main config file (sshyp-data)
    with open(path.expanduser('~/.config/sshyp/sshyp-data'), 'w') as _config_file:
        _lines = 0
        for _item in _sshyp_data:
            _lines += 1
            _config_file.write(_item + '\n')
        while _lines < 5:
            _lines += 1
            _config_file.write('offline\n')
    print(f"{_divider}configuration complete\n")


def print_info():  # prints help text based on argument
    if argument_list[1] == 'help' or argument_list[1] == '--help' or argument_list[1] == '-h':
        print('\n\u001b[1msshyp  copyright (c) 2021-2022  randall winkhart\u001b[0m\n')
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
            print(' list/-l             view all registered device ids and their quick-unlock whitelist status')
            print(' add                 whitelist a device id for quick-unlock')
            print(' delete/del          remove a device id from the quick-unlock whitelist\n')
    elif argument_list[1] == 'version' or argument_list[1] == '-v':
        print('\nsshyp is a simple, self-hosted, sftp-synchronized password manager\nfor unix(-like) systems (haiku/'
              'freebsd/linux/termux)\n\nsshyp is a viable alternative to (and compatible with) pass/password-store\n')
        print("                ..       \u001b[38;5;9m♥♥ ♥♥\u001b[0m       ..\n         .''.''/()\\     \u001b[38;5;13m"
              "♥♥♥♥♥♥♥\u001b[0m     /()\\''.''.\n        *       :        \u001b[38;5;9m♥♥♥♥♥\u001b[0m        :       *"
              "\n         `..'..'          \u001b[38;5;13m♥♥♥\u001b[0m          `..'..'\n         //   \\\\           "
              "\u001b[38;5;9m♥\u001b[0m           //   \\\\")
        print('\u001b[38;5;7;48;5;8m<><><><><><><><><><><><><><><><><><><><><><><><><><><><>\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                                                      '
              '\u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m   \u001b[38;5;15;48;5;8msshyp  copyright (c) 2021-2022  '
              'randall winkhart\u001b[38;5;15;48;5;15m   \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                                                      '
              '\u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                    \u001b[38;5;15;48;5;8mversion 1.1.2'
              '\u001b[38;5;15;48;5;15m                     \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                 \u001b[38;5;15;48;5;8mthe sheecrets '
              'update\u001b[38;5;15;48;5;15m                 \u001b[38;5;7;48;5;8m/\u001b[0m')
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
            print(' list/-l             view all registered device ids and their quick-unlock whitelist status')
            print(' add                 whitelist a device id for quick-unlock')
            print(' delete/del          remove a device id from the quick-unlock whitelist\n')
        else:
            print('\n\u001b[38;5;9merror: argument (whitelist) only available on server\u001b[0m\n')


def no_arg():  # displays a list of entries and gives an option to select one for viewing
    print("\nfor a list of usable commands, run 'sshyp help'")
    _entry_name = entry_name_fetch('entry to read: ')
    if not Path(f"{directory}{_entry_name}.gpg").exists():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(1)
    _shm_folder, _shm_entry = shm_gen()
    decrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg)
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    rmtree(f"{tmp_dir}{_shm_folder}")


def read_shortcut():  # shortcut to quickly read an entry
    if not Path(f"{directory}{argument.replace('/', '', 1)}.gpg").exists():
        print(f"\n\u001b[38;5;9merror: entry ({argument.replace('/', '', 1)}) does not exist\u001b[0m\n")
        s_exit(1)
    _shm_folder, _shm_entry = shm_gen()
    decrypt(directory + argument.replace('/', '', 1), _shm_folder, _shm_entry, gpg)
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    rmtree(f"{tmp_dir}{_shm_folder}")


def sync():  # calls sshync to sync changes to the user's server
    print('\nsyncing entries with the server device...\n')
    # check for deletions
    system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"cd /bin; python -c "
           f"'import sshypRemote; sshypRemote.deletion_check(\"'\"{client_device_id}\"'\")'\"")
    system(f"scp -pqs -P {port} -i '{path.expanduser('~/.ssh/sshyp')}' {username_ssh}@{ip}:'/home/{username_ssh}"
           f"/.config/sshyp/deletion_database' {path.expanduser('~/.config/sshyp/')}")
    try:
        _deletion_database = open(path.expanduser('~/.config/sshyp/deletion_database')).readlines()
    except (FileNotFoundError, IndexError):
        print('\n\u001b[38;5;9merror: the deletion database does not exist or is corrupted\u001b[0m\n')
        _deletion_database = None
        s_exit(1)
    for _file in _deletion_database:
        try:
            if silent_sync != 1:
                print(f"\u001b[38;5;208m{_file[:-1]}\u001b[0m has been sheared, removing...")
            if _file[:-1].endswith('/'):
                rmtree(f"{directory}{_file[:-1]}")
            else:
                remove(f"{directory}{_file[:-1]}.gpg")
        except FileNotFoundError:
            if silent_sync != 1:
                print('location does not exist locally')
    # check for new folders
    system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"cd /bin; python -c "
           f"'import sshypRemote; sshypRemote.folder_check()'\"")
    system(f"scp -pqs -P {port} -i '{path.expanduser('~/.ssh/sshyp')}' {username_ssh}@{ip}:'/home/{username_ssh}"
           f"/.config/sshyp/folder_database' {path.expanduser('~/.config/sshyp/')}")
    try:
        _folder_database = open(path.expanduser('~/.config/sshyp/folder_database')).readlines()
    except (FileNotFoundError, IndexError):
        print('\n\u001b[38;5;9merror: the folder database does not exist or is corrupted\u001b[0m\n')
        _folder_database = None
        s_exit(1)
    for _folder in _folder_database:
        if Path(f"{path.expanduser('~')}{_folder[:-1]}").is_dir():
            pass
        else:
            print(f"\u001b[38;5;2m{_folder.replace('/.local/share/sshyp/', '')[:-1]}/\u001b[0m does not exist locally, "
                  f"creating...")
            Path(f"{path.expanduser('~')}{_folder[:-1]}").mkdir(0o700, parents=True, exist_ok=True)
    # set permissions before uploading
    system('find ' + directory + ' -type d -exec chmod -R 700 {} +')
    system('find ' + directory + ' -type f -exec chmod -R 600 {} +')
    sshync.run_profile(path.expanduser('~/.config/sshyp/sshyp.sshync'))


def whitelist_list():  # shows the quick-unlock whitelist status of device ids
    _whitelisted_ids = listdir(path.expanduser('~/.config/sshyp/whitelist'))
    _device_ids = listdir(path.expanduser('~/.config/sshyp/devices'))
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
        if _device_id in listdir(path.expanduser('~/.config/sshyp/devices')):
            open(path.expanduser(f"~/.config/sshyp/whitelist/{_device_id}"), 'w').write('')
            whitelist_list()
        else:
            print(f"\n\u001b[38;5;9merror: device id ({_device_id}) is not registered\u001b[0m\n")
            s_exit(1)

    elif Path(path.expanduser(f"~/.config/sshyp/whitelist/{_device_id}")).is_file():
        remove(path.expanduser(f"~/.config/sshyp/whitelist/{_device_id}"))
        whitelist_list()


def add_entry():  # adds a new entry
    _shm_folder, _shm_entry = None, None  # sets base-line values to avoid errors
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('name of new entry: ')
    else:
        _entry_name = entry_name_fetch(2)
    if Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) already exists\u001b[0m\n")
        s_exit(1)
    if argument_list[2] == 'note' or argument_list[2] == '-n':
        _shm_folder, _shm_entry = shm_gen()
        system(f"{editor} {tmp_dir}{_shm_folder}/{_shm_entry}-n")
        _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(optimized_edit(['', '', '', _notes], None, -1))
    elif argument_list[2] == 'password' or argument_list[2] == '-p':
        _username = str(input('username: '))
        _password = str(input('password: '))
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
        _shm_folder, _shm_entry = shm_gen()
        if _add_note.lower() == 'y':
            system(f"{editor} {tmp_dir}{_shm_folder}/{_shm_entry}-n")
            _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        else:
            _notes = ''
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w')\
            .writelines(optimized_edit([_password, _username, _url, _notes], None, -1))
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg, gpg_id)


def add_folder():  # creates a new folder
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('name of new folder: ')
    else:
        _entry_name = entry_name_fetch(2)
    Path(directory + _entry_name).mkdir(0o700)
    if ssh_error != 1:
        system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"mkdir -p "
               f"'{directory_ssh}{_entry_name}'\"")


def rename():  # renames an entry or folder
    if argument == 'edit rename' or argument == 'edit relocate' or argument == 'edit -r':
        _entry_name = entry_name_fetch('entry/folder to rename/relocate: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file() and not Path(f"{directory}{_entry_name}").is_dir():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(1)
    _new_name = entry_name_fetch('new name: ')
    if Path(f"{directory}{_new_name}.gpg").is_file() or Path(f"{directory}{_new_name}").is_dir():
        print(f"\n\u001b[38;5;9merror: ({_new_name}) already exists\u001b[0m\n")
        s_exit(1)
    if _entry_name.endswith('/'):
        move(f"{directory}{_entry_name}", f"{directory}{_new_name}")
        if ssh_error != 1:
            system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"mkdir -p "
                   f"'{directory_ssh}{_new_name}'\"")
    else:
        move(f"{directory}{_entry_name}.gpg", f"{directory}{_new_name}.gpg")
    if ssh_error != 1:
        system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"cd /bin; python -c "
               f"'import sshypRemote; sshypRemote.delete(\"'\"{_entry_name}\"'\", 'remotely')'\"")


def edit():  # edits the contents of an entry
    _shm_folder, _shm_entry, _detail, _edit_line = None, None, None, None  # sets values to avoid PEP8 warnings
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('entry to edit: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(1)
    _shm_folder, _shm_entry = shm_gen()
    decrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg)
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
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg, gpg_id)


def gen():  # generates a password for a new or an existing entry
    _username, _url, _notes = None, None, None  # sets base-line values to avoid errors
    if argument == 'gen update' or argument == 'gen -u' or argument == 'gen':
        _entry_name = entry_name_fetch('name of entry: ')
    elif argument_list[2] == 'update' or argument_list[2] == '-u':
        _entry_name = entry_name_fetch(2)
        if not Path(f"{directory}{_entry_name}.gpg").is_file():
            print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
            s_exit(1)
    else:
        _entry_name = entry_name_fetch(1)
    if len(argument_list) == 2 or (not argument_list[2] == 'update' and not argument_list[2] == '-u'):
        if Path(f"{directory}{_entry_name}.gpg").is_file():
            print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) already exists\u001b[0m\n")
            s_exit(1)
        _username = str(input('username: '))
        _password = pass_gen()
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
        _shm_folder, _shm_entry = shm_gen()
        if _add_note.lower() == 'y':
            system(f"{editor} {tmp_dir}{_shm_folder}/{_shm_entry}-n")
            _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        else:
            _notes = ''
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w')\
            .writelines(optimized_edit([_password, _username, _url, _notes], None, -1))
    else:
        _shm_folder, _shm_entry = shm_gen()
        decrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg)
        _new_lines = optimized_edit(open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), pass_gen(), 0)
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_new_lines)
        remove(f"{directory}{_entry_name}.gpg")
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg, gpg_id)


def copy_data():  # copies a specified field of an entry to the clipboard
    if len(argument_list) < 4:
        _entry_name = entry_name_fetch('entry to copy: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(1)
    _shm_folder, _shm_entry = shm_gen()
    decrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg)
    _copy_line = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines()
    if uname()[0] == 'Haiku':  # Haiku clipboard detection
        if argument_list[2] == 'username' or argument_list[2] == '-u':
            system('clipboard -c ' + "'" + _copy_line[1].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'password' or argument_list[2] == '-p':
            system('clipboard -c ' + "'" + _copy_line[0].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'url' or argument_list[2] == '-l':
            system('clipboard -c ' + "'" + _copy_line[2].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'note' or argument_list[2] == '-n':
            system('clipboard -c ' + "'" + _copy_line[3].rstrip().replace("'", "'\\''") + "'")
        Popen('sleep 30; clipboard -r', shell=True, close_fds=True)
    elif Path("/data/data/com.termux").exists():  # Termux (Android) clipboard detection
        if argument_list[2] == 'username' or argument_list[2] == '-u':
            system('termux-clipboard-set ' + "'" + _copy_line[1].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'password' or argument_list[2] == '-p':
            system('termux-clipboard-set ' + "'" + _copy_line[0].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'url' or argument_list[2] == '-l':
            system('termux-clipboard-set ' + "'" + _copy_line[2].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'note' or argument_list[2] == '-n':
            system('termux-clipboard-set ' + "'" + _copy_line[3].rstrip().replace("'", "'\\''") + "'")
        Popen("sleep 30; termux-clipboard-set ''", shell=True, close_fds=True)
    elif environ.get('WAYLAND_DISPLAY') == 'wayland-0':  # Wayland clipboard detection
        if argument_list[2] == 'username' or argument_list[2] == '-u':
            system('wl-copy ' + "'" + _copy_line[1].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'password' or argument_list[2] == '-p':
            system('wl-copy ' + "'" + _copy_line[0].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'url' or argument_list[2] == '-l':
            system('wl-copy ' + "'" + _copy_line[2].rstrip().replace("'", "'\\''") + "'")
        elif argument_list[2] == 'note' or argument_list[2] == '-n':
            system('wl-copy ' + "'" + _copy_line[3].rstrip().replace("'", "'\\''") + "'")
        Popen('sleep 30; wl-copy -c', shell=True, close_fds=True)
    else:  # X11 clipboard detection
        if argument_list[2] == 'username' or argument_list[2] == '-u':
            system('echo -n ' + "'" + _copy_line[1].rstrip().replace("'", "'\\''") + "'" + ' | xclip -sel c')
        elif argument_list[2] == 'password' or argument_list[2] == '-p':
            system('echo -n ' + "'" + _copy_line[0].rstrip().replace("'", "'\\''") + "'" + ' | xclip -sel c')
        elif argument_list[2] == 'url' or argument_list[2] == '-l':
            system('echo -n ' + "'" + _copy_line[2].rstrip().replace("'", "'\\''") + "'" + ' | xclip -sel c')
        elif argument_list[2] == 'note' or argument_list[2] == '-n':
            system('echo -n ' + "'" + _copy_line[3].rstrip().replace("'", "'\\''") + "'" + ' | xclip -sel c')
        Popen("sleep 30; echo -n '' | xclip -sel c", shell=True, close_fds=True)
    rmtree(f"{tmp_dir}{_shm_folder}")


def remove_data():  # deletes an entry from the server and flags it for local deletion on sync
    if argument == 'shear' or argument == '-rm':
        _entry_name = entry_name_fetch('entry/folder to shear: ')
    else:
        _entry_name = entry_name_fetch(1)
    decrypt(path.expanduser('~/.config/sshyp/lock.gpg'), 0, 0, gpg)
    if ssh_error != 1:
        system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"cd /bin; python -c "
               f"'import sshypRemote; sshypRemote.delete(\"'\"{_entry_name}\"'\", 'remotely')'\"")
    else:
        from sshypRemote import delete as offline_delete
        offline_delete(_entry_name, '')


if __name__ == "__main__":
    try:
        silent_sync, ssh_error = 0, 0
        # retrieve typed argument
        argument_list = argv
        argument = ' '.join(argument_list[1:])
        if uname()[0] == 'Haiku':  # set proper gpg command for OS
            gpg = 'gpg --pinentry-mode loopback'
        else:
            gpg = 'gpg'

        # import saved userdata
        device_type = ''
        if argument != 'tweak':
            tmp_dir = path.expanduser('~/.config/sshyp/tmp/')
            try:
                sshyp_data = open(path.expanduser('~/.config/sshyp/sshyp-data')).readlines()
                device_type = sshyp_data[0].rstrip()
                if device_type == 'client':
                    directory = path.expanduser('~/.local/share/sshyp/')
                    gpg_id = sshyp_data[1].rstrip()
                    editor = sshyp_data[2].rstrip()
                    quick_unlock_status = sshyp_data[3].rstrip()
                    if quick_unlock_status == 'quick':
                        quick_unlock_length = sshyp_data[4].rstrip()
                    if Path(path.expanduser('~/.config/sshyp/sshyp.sshync')).is_file():
                        ssh_info = sshync.get_profile(path.expanduser('~/.config/sshyp/sshyp.sshync'))
                        username_ssh = ssh_info[0].rstrip()
                        ip = ssh_info[1].rstrip()
                        port = ssh_info[2].rstrip()
                        directory_ssh = str(ssh_info[4].rstrip())
                        client_device_id = listdir(path.expanduser('~/.config/sshyp/devices'))[0]
                        ssh_error = int(open(path.expanduser('~/.config/sshyp/ssh-error')).read().rstrip())
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
                    s_exit(0)
            except (FileNotFoundError, IndexError):
                print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print("not all necessary configuration files are present - please run 'sshyp tweak'")
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
                s_exit(1)
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
                s_exit(0)
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
                s_exit(0)
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
                    s_exit(1)
            else:
                print_info()
        elif argument_list[1] == 'shear' or argument_list[1] == '-rm':
            remove_data()
        elif argument_list[1] != 'sync' and argument_list[1] != '-s':
            print(f"\n\u001b[38;5;9merror: invalid argument - run 'sshyp help' to list usable commands\u001b[0m\n")
            s_exit(1)

        # sync if any changes were made
        if len(argument_list) > 1 and ssh_error == 0 and \
                ((argument_list[1] == 'sync' or argument_list[1] == '-s' or argument_list[1] == 'gen' or
                  argument_list[1] == 'shear' or argument_list[1] == '-rm') or ((argument_list[1] == 'add'
                                                                                 or argument_list[1] == 'edit')
                                                                                and len(argument_list) > 2)):
            sync()

        s_exit(0)

    except KeyboardInterrupt:
        print('\n')
        s_exit(0)
