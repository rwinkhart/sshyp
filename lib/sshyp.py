#!/usr/bin/env python3
from os import chmod, environ, listdir, remove, uname, walk
from os.path import exists, expanduser, isdir, isfile, realpath
from pathlib import Path
from random import randint
from shutil import get_terminal_size, move, rmtree
from sshync import delete as offline_delete, run_profile, make_profile, get_profile
from subprocess import CalledProcessError, DEVNULL, PIPE, run
from sys import argv, exit as s_exit
home = expanduser("~")


# UTILITY FUNCTIONS

def entry_list_gen(_directory=f"{home}/.local/share/sshyp/"):  # generates and prints full entry list
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
        else:
            _ran = True


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
    if _complexity not in ('s', 'S'):
        _complexity = 'c'
    _gen = string_gen(_complexity.lower(), _length)
    return _gen


def shm_gen(_tmp_dir=f"{home}/.config/sshyp/tmp/"):  # creates a temporary directory for entry editing
    _shm_folder_gen = string_gen('f', randint(12, 48))
    _shm_entry_gen = string_gen('f', randint(12, 48))
    Path(_tmp_dir + _shm_folder_gen).mkdir(mode=0o700)
    return _shm_folder_gen, _shm_entry_gen


def encrypt(_entry_dir, _shm_folder, _shm_entry, _gpg_id, _tmp_dir=f"{home}/.config/sshyp/tmp/"):
    # encrypts an entry and cleans up the temporary files
    run(['gpg', '-qr', str(_gpg_id), '-e', f"{_tmp_dir}{_shm_folder}/{_shm_entry}"])
    move(f"{_tmp_dir}{_shm_folder}/{_shm_entry}.gpg", f"{_entry_dir}.gpg")
    rmtree(f"{_tmp_dir}{_shm_folder}")


def decrypt(_entry_dir, _shm_folder, _shm_entry, _quick_pass,
            _tmp_dir=f"{home}/.config/sshyp/tmp/"):  # decrypts an entry to a temporary directory
    if not isinstance(_quick_pass, bool):
        _unlock_method = ['gpg', '--pinentry-mode', 'loopback', '--passphrase', _quick_pass, '-qd', '--output']
    else:
        _unlock_method = ['gpg', '-qd', '--output']
    if _shm_folder is None and _shm_entry is None:
        _output_target = ['/dev/null', f"{home}/.config/sshyp/lock.gpg"]
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
                s_exit(4)
        else:
            print('\n\u001b[38;5;9merror: could not decrypt - ensure the correct gpg key is present\u001b[0m\n')
            s_exit(4)


def determine_decrypt(_entry_dir, _shm_folder, _shm_entry):  # call decrypt() based on quick-unlock status
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
        run(['ssh', '-o', 'ConnectTimeout=3', '-i', f"{home}/.ssh/sshyp", '-p', _port, f"{_username_ssh}@{_ip}",
             f'python3 -c \'from pathlib import Path; Path("/home/{_username_ssh}/.config/sshyp/devices/'
             f'{_client_device_id}").touch(mode=0o400, exist_ok=True)\''], stderr=DEVNULL, check=True)
    except CalledProcessError:
        print('\n\u001b[38;5;9mwarning: ssh connection could not be made - ensure the public key (~/.ssh/sshyp.pub) is '
              'registered on the remote server and that the entered ip, port, and username are correct\n\nsyncing '
              'functionality will be disabled until this is addressed\u001b[0m\n')
        open(f"{home}/.config/sshyp/ssh-error", 'w').write('1')
        return True
    open(f"{home}/.config/sshyp/ssh-error", 'w').write('0')
    return False


# ARGUMENT-SPECIFIC FUNCTIONS

def tweak():  # runs configuration wizard
    from os import symlink
    _divider = f"\n{'=' * (get_terminal_size()[0] - int((.5 * get_terminal_size()[0])))}\n\n"

    # config directory creation
    Path(f"{home}/.config/sshyp/devices").mkdir(mode=0o700, parents=True, exist_ok=True)
    if not exists(f"{home}/.config/sshyp/tmp"):
        if uname()[0] in ('Haiku', 'FreeBSD'):
            symlink('/tmp', f"{home}/.config/sshyp/tmp")
        elif exists('/data/data/com.termux'):
            symlink('/data/data/com.termux/files/usr/tmp', f"{home}/.config/sshyp/tmp")
        else:
            symlink('/dev/shm', f"{home}/.config/sshyp/tmp")

    # device type configuration
    _device_type = input('\nclient or server installation? (C/s) ')
    if _device_type.lower() == 's':
        _sshyp_data = ['server']
        Path(f"{home}/.config/sshyp/deleted").mkdir(mode=0o700, exist_ok=True)
        Path(f"{home}/.config/sshyp/whitelist").mkdir(mode=0o700, exist_ok=True)
        print(f"\n\u001b[4;1mmake sure the ssh service is running and properly configured\u001b[0m")
    else:
        _sshyp_data = ['client']
        Path(f"{home}/.local/share/sshyp").mkdir(mode=0o700, parents=True, exist_ok=True)

        # gpg configuration
        _gpg_gen = input(f"{_divider}sshyp requires the use of a unique gpg key - use an (e)xisting key or (g)enerate a"
                         f" new one? (E/g) ")
        if _gpg_gen.lower() != 'g':
            run(['gpg', '-k'])
            _sshyp_data.append(str(input('gpg key id: ')))
        else:
            print('\na unique gpg key is being generated for you...')
            if not isfile(f"{home}/.config/sshyp/gpg-gen"):
                open(f"{home}/.config/sshyp/gpg-gen", 'w').writelines([
                    'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
                    'Name-Comment: gpg-sshyp\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
            run(['gpg', '--batch', '--generate-key', f"{home}/.config/sshyp/gpg-gen"])
            remove(f"{home}/.config/sshyp/gpg-gen")
            _sshyp_data.append(run(['gpg', '-k'], stdout=PIPE, text=True).stdout.splitlines()[-3].strip())

        # text editor configuration
        _sshyp_data.append(input(f"{_divider}example input: vim\n\npreferred text editor: "))

        # lock file generation
        if isfile(f"{home}/.config/sshyp/lock.gpg"):
            remove(f"{home}/.config/sshyp/lock.gpg")
        open(f"{home}/.config/sshyp/lock", 'w')
        run(['gpg', '-qr', str(_sshyp_data[1]), '-e', f"{home}/.config/sshyp/lock"])
        remove(f"{home}/.config/sshyp/lock")

        # ssh key configuration
        _offline_mode = False
        _ssh_gen = (input(f"{_divider}make sure the ssh service on the remote server is running and properly "
                          f"configured\n\nsync support requires a unique ssh key - would you like to have this "
                          f"automatically generated? (Y/n/o(ffline)) "))
        if _ssh_gen.lower() not in ('n', 'o', 'offline'):
            Path(f"{home}/.ssh").mkdir(mode=0o700, exist_ok=True)
            run(['ssh-keygen', '-t', 'ed25519', '-f', f"{home}/.ssh/sshyp"])
        elif _ssh_gen.lower() == 'n':
            print(f"\n\u001b[4;1mensure that the key file you are using is located at {home}/.ssh/sshyp\u001b[0m")
        elif _ssh_gen.lower() in ('o', 'offline'):
            _offline_mode = True
            print('\nsshyp has been set to offline mode - to enable syncing, run "sshyp tweak" again')

        if not _offline_mode:
            # ssh ip+port configuration
            _iport = str(input(f"{_divider}example inputs:\n\n ipv4: 10.10.10.10:22\n ipv6: [2000:2000:2000:2000:"
                               f"2000:2000:2000:2000]:22\n domain: mydomain.com:22\n\nip and ssh port of sshyp server: "
                               )).lstrip('[').replace(']', '').rsplit(':', 1)

            # ssh user configuration
            _username_ssh = str(input('\nusername of the remote server: '))

            # sshync profile generation
            make_profile(f"{home}/.config/sshyp/sshyp.sshync",
                         f"{home}/.local/share/sshyp/", f"/home/{_username_ssh}/.local/share/sshyp/",
                         f"{home}/.ssh/sshyp", _iport[0], _iport[1], _username_ssh)

            # device id configuration
            for _id in listdir(f"{home}/.config/sshyp/devices"):  # remove existing device id
                remove(f"{home}/.config/sshyp/devices/{_id}")
            print(f"{_divider}\u001b[4;1mimportant:\u001b[0m this id \u001b[4;1mmust\u001b[0m be unique amongst your "
                  f"client devices\n\nthis is used to keep track of database syncing and quick-unlock permissions\n")
            _device_id_prefix = str(input('device id: ')) + '-'
            _device_id_suffix = string_gen('f', randint(24, 48))
            _device_id = _device_id_prefix + _device_id_suffix
            open(f"{home}/.config/sshyp/devices/{_device_id}", 'w')

            # quick-unlock configuration
            print(f"{_divider}this allows you to use a shorter version of your gpg key password and\n"
                  f"requires a constant connection to your sshyp server to authenticate")
            _sshyp_data.append(input('\nenable quick-unlock? (y/N) ').lower())
            if _sshyp_data[3] == 'y':
                print(f"\nquick-unlock has been enabled client-side - in order for this device to be able to read "
                      f"entries,\nyou must first login to the sshyp server and run:\n\nsshyp whitelist setup "
                      f"(if not already done)\nsshyp whitelist add '{_device_id}'")

            # test server connection and attempt to register device id
            copy_id_check(_iport[1], _username_ssh, _iport[0], _device_id)

        elif isfile(f"{home}/.config/sshyp/sshyp.sshync"):
            remove(f"{home}/.config/sshyp/sshyp.sshync")

    # write main config file (sshyp-data)
    with open(f"{home}/.config/sshyp/sshyp-data", 'w') as _config_file:
        _lines = 0
        for _item in _sshyp_data:
            _lines += 1
            _config_file.write(_item + '\n')
        while _lines < 4:
            _lines += 1
            _config_file.write('n')
    print(f"{_divider}configuration complete\n")


def print_info():  # prints help text based on argument
    if arguments[0] in ('version', '-v'):
        print('\nsshyp is a simple, self-hosted, sftp-synchronized password manager\nfor unix(-like) systems (haiku/'
              'freebsd/linux/termux)\n\nsshyp is a viable alternative to (and compatible with) pass/password-store\n')
        print("                ..       \u001b[38;5;9m♥♥ ♥♥\u001b[0m       ..\n         .''.''/()\\     \u001b[38;5;13m"
              "♥♥♥♥♥♥♥\u001b[0m     /()\\''.''.\n        *       :        \u001b[38;5;9m♥♥♥♥♥\u001b[0m        :       *"
              "\n         `..'..'          \u001b[38;5;13m♥♥♥\u001b[0m          `..'..'\n         //   \\\\           "
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
    elif arguments[0] == 'license':
        print('\nThis program is free software: you can redistribute it and/or modify it under the terms\nof version 3 '
              '(only) of the GNU General Public License as published by the Free Software Foundation.\n\nThis program '
              'is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;\nwithout even the implied '
              'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\nSee the GNU General Public License for'
              ' more details.\n\nhttps://opensource.org/licenses/GPL-3.0\n')
    elif arguments[0] == 'add' and device_type == 'client':
        print('\n\u001b[1musage:\u001b[0m sshyp </entry name> add <flag>\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('add:')
        print(' password/-p             add a password entry')
        print(' note/-n                 add a note entry')
        print(' folder/-f               add a new folder for entries\n')
    elif arguments[0] == 'edit' and device_type == 'client':
        print('\n\u001b[1musage:\u001b[0m sshyp </entry name> edit <flag>\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('edit:')
        print(' rename/relocate/-r      rename or relocate an entry')
        print(' username/-u             change the username of an entry')
        print(' password/-p             change the password of an entry')
        print(' url/-l                  change the url attached to an entry')
        print(' note/-n                 change the note attached to an entry\n')
    elif arguments[0] == 'copy' and device_type == 'client':
        print('\n\u001b[1musage:\u001b[0m sshyp </entry name> copy <flag>\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('copy:')
        print(' username/-u             copy the username of an entry to your clipboard')
        print(' password/-p             copy the password of an entry to your clipboard')
        print(' url/-l                  copy the url of an entry to your clipboard')
        print(' note/-n                 copy the note of an entry to your clipboard\n')
    elif arguments[0] == 'whitelist':
        if device_type == 'server':
            print('\n\u001b[1musage:\u001b[0m sshyp whitelist <flag> [device id]\u001b[0m\n')
            print('\u001b[1mflags:\u001b[0m')
            print('whitelist:')
            print(' setup                   set up the quick-unlock whitelist')
            print(' list/-l                 view all registered device ids and their quick-unlock whitelist status')
            print(' add                     whitelist a device id for quick-unlock')
            print(' delete/del              remove a device id from the quick-unlock whitelist\n')
        else:
            print('\n\u001b[38;5;9merror: argument (whitelist) only available on server\u001b[0m\n')
    else:
        print('\n\u001b[1msshyp  copyright (c) 2021-2023  randall winkhart\u001b[0m\n')
        print("this is free software, and you are welcome to redistribute it under certain conditions;\nthis program "
              "comes with absolutely no warranty;\ntype 'sshyp license' for details")
        if device_type == 'client':
            print('\n\u001b[1musage:\u001b[0m sshyp [</entry name> [option] [flag]] [option]\n')
            print('\u001b[1moptions:\u001b[0m')
            print('help/-h                  bring up this menu')
            print('version/-v               display sshyp version info')
            print('tweak                    configure sshyp')
            print('add                      add an entry')
            print('gen                      generate a new password')
            print('edit                     edit an existing entry')
            print('copy                     copy details of an entry to your clipboard')
            print('shear                    delete an existing entry')
            print('sync                     manually sync the entry directory via sshync')
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
            print("\n\u001b[1mtip 1:\u001b[0m you can quickly read an entry with 'sshyp </entry name>'")
            print("\u001b[1mtip 2:\u001b[0m type 'sshyp' to view a list of saved entries\n")
        else:
            print('\n\u001b[1musage:\u001b[0m sshyp <option> [flag] [<device id>]\n')
            print('\u001b[1moptions:\u001b[0m')
            print('help/-h                  bring up this menu')
            print('version/-v               display sshyp version info')
            print('tweak                    configure sshyp')
            print('whitelist                manage the quick-unlock whitelist')
            print('\n\u001b[1mflags:\u001b[0m')
            print('whitelist:')
            print(' setup                   set up the quick-unlock whitelist')
            print(' list/-l                 view all registered device ids and their quick-unlock whitelist status')
            print(' add                     whitelist a device id for quick-unlock')
            print(' del                     remove a device id from the quick-unlock whitelist\n')


def read_shortcut():  # shortcut to quickly read an entry
    if not exists(f"{directory}{arguments[0].replace('/', '', 1)}.gpg"):
        if not arguments[0].replace('/', '', 1):
            print(f"\n\u001b[38;5;9merror: missing entry name\u001b[0m\n")
        elif isdir(f"{directory}{arguments[0].replace('/', '', 1)}"):
            print(f"\n\u001b[38;5;9merror: entry ({arguments[0]}) is a directory\u001b[0m\n")
        else:
            print(f"\n\u001b[38;5;9merror: entry ({arguments[0]}) does not exist\u001b[0m\n")
        s_exit(2)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + arguments[0].replace('/', '', 1), _shm_folder, _shm_entry)
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    rmtree(f"{tmp_dir}{_shm_folder}")


def sync():  # calls sshync to sync changes to the user's server
    print('\nsyncing entries with the server device...\n')
    # set permissions before uploading
    for _root, _dirs, _files in walk(f"{home}/.local/share/sshyp"):
        for _path in _root.splitlines():
            chmod(_path, 0o700)
        for _file in _files:
            chmod(_root + '/' + _file, 0o600)
    run_profile(f"{home}/.config/sshyp/sshyp.sshync", silent_sync)


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
    open(f"{home}/.config/sshyp/gpg-gen", 'w').writelines([
        'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
        'Name-Comment: gpg-sshyp-whitelist\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n', 'Expire-Date: 0'])
    run(['gpg', '-q', '--pinentry-mode', 'loopback', '--batch', '--generate-key', '--passphrase',
         _quick_unlock_password, f"{home}/.config/sshyp/gpg-gen"])
    remove(f"{home}/.config/sshyp/gpg-gen")
    _gpg_id = run(['gpg', '-k'], stdout=PIPE, text=True).stdout.splitlines()[-3].strip()

    # encrypt excluded with the assembly key
    _shm_folder, _shm_entry = shm_gen()
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').write(_quick_unlock_password_excluded)
    encrypt(f"{home}/.config/sshyp/excluded", _shm_folder, _shm_entry, _gpg_id)
    print(f"\nyour quick-unlock passphrase: {_quick_unlock_password}")


def whitelist_verify(_port, _username_ssh, _ip, _client_device_id):
    # checks the user's whitelist status and fetches the full gpg key password if possible
    try:
        run(['gpg', '--pinentry-mode', 'cancel', '-qd', '--output', '/dev/null',
             f"{home}/.config/sshyp/lock.gpg"], stderr=DEVNULL, check=True)
        return False
    except CalledProcessError:
        _i, _full_password = 0, ''
        _server_whitelist = run(['ssh', '-i', f"{home}/.ssh/sshyp", '-p', _port, f"{_username_ssh}@{_ip}",
                                 f'python3 -c \'from os import listdir; print(*listdir("/home/{_username_ssh}'
                                 f'/.config/sshyp/whitelist"))\''], stdout=PIPE, text=True).stdout.rstrip().split()
        for _device_id in _server_whitelist:
            if _device_id == _client_device_id:
                from getpass import getpass
                _quick_unlock_password = getpass(prompt='\nquick-unlock passphrase: ')
                _quick_unlock_password_excluded = \
                    run(['ssh', '-i', f"{home}/.ssh/sshyp", '-p',  _port, f"{_username_ssh}@{_ip}",
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


def whitelist_manage():  # adds or removes quick-unlock whitelisted device ids
    if arg_count == 2:
        whitelist_list()
        _device_id = input('device id: ')
    else:
        _device_id = arguments[2]

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


def add_entry():  # adds a new entry
    _shm_folder, _shm_entry = None, None  # set to avoid PEP8 warnings
    _entry_name = arguments[0]
    if isfile(f"{directory}{_entry_name}.gpg"):
        print(f"\n\u001b[38;5;9merror: entry (/{_entry_name}) already exists\u001b[0m\n")
        s_exit(3)
    if arguments[2] in ('note', '-n'):  # note entry
        _shm_folder, _shm_entry = shm_gen()
        run([editor, f"{tmp_dir}{_shm_folder}/{_shm_entry}-n"])
        _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(optimized_edit(['', '', '', _notes], None, -1))
    else:  # password entry
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
    _entry_name = arguments[0]
    Path(directory + _entry_name).mkdir(mode=0o700, parents=True, exist_ok=True)
    if not ssh_error:
        run(['ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
             f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{_entry_name}")'
             f'.mkdir(mode=0o700, parents=True, exist_ok=True)\''])


def rename():  # renames an entry or folder
    from shutil import copy
    _entry_name = arguments[0]
    if not isfile(f"{directory}{_entry_name}.gpg") and not isdir(f"{directory}{_entry_name}"):
        print(f"\n\u001b[38;5;9merror: entry (/{_entry_name}) does not exist\u001b[0m\n")
        s_exit(2)
    _new_name = str(input('new name: '))
    if _new_name.startswith('/'):
        _new_name.replace('/', '', 1)
    if isfile(f"{directory}{_new_name}.gpg") or isdir(f"{directory}{_new_name}"):
        print(f"\n\u001b[38;5;9merror: (/{_new_name}) already exists\u001b[0m\n")
        s_exit(3)
    if _entry_name.endswith('/'):
        if not ssh_error:
            Path(f"{directory}{_new_name}").mkdir(mode=0o700, parents=True, exist_ok=True)
            run(['ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
                 f'python3 -c \'from pathlib import Path; Path("{directory_ssh}{_new_name}")'
                 f'.mkdir(mode=0o700, parents=True, exist_ok=True)\''])
        else:
            move(f"{directory}{_entry_name}", f"{directory}{_new_name}")
    else:
        if not ssh_error:
            copy(f"{directory}{_entry_name}.gpg", f"{directory}{_new_name}.gpg")
        else:
            move(f"{directory}{_entry_name}.gpg", f"{directory}{_new_name}.gpg")
    if not ssh_error:
        run(['ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
             f'cd /lib/sshyp; python3 -c \'from sshync import delete; delete("{_entry_name}", "remotely")\''])


def edit():  # edits the contents of an entry
    _shm_folder, _shm_entry, _detail, _edit_line = None, None, None, None  # set to avoid PEP8 warnings
    _entry_name = arguments[0]
    if not isfile(f"{directory}{_entry_name}.gpg"):
        print(f"\n\u001b[38;5;9merror: entry (/{_entry_name}) does not exist\u001b[0m\n")
        s_exit(2)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
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
    remove(f"{directory}{_entry_name}.gpg")
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg_id)


def gen():  # generates a password for a new or an existing entry
    _username, _url, _notes = None, None, None  # set to avoid PEP8 warnings
    _entry_name = arguments[0]
    _shm_folder, _shm_entry = shm_gen()
    if arg_count == 3 and arguments[2] in ('update', '-u'):  # gen update
        if not isfile(f"{directory}{_entry_name}.gpg"):
            print(f"\n\u001b[38;5;9merror: entry (/{_entry_name}) does not exist\u001b[0m\n")
            s_exit(2)
        determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
        _new_lines = optimized_edit(open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), pass_gen(), 0)
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_new_lines)
        remove(f"{directory}{_entry_name}.gpg")
    elif isfile(f"{directory}{_entry_name}.gpg"):  # gen
        print(f"\n\u001b[38;5;9merror: entry (/{_entry_name}) already exists\u001b[0m\n")
        s_exit(3)
    else:
        _username = str(input('username: '))
        _password = pass_gen()
        _url = str(input('url: '))
        _add_note = input('add a note to this entry? (y/N) ')
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


def copy_data():  # copies a specified field of an entry to the clipboard
    from subprocess import Popen
    _entry_name = arguments[0]
    if not isfile(f"{directory}{_entry_name}.gpg"):
        print(f"\n\u001b[38;5;9merror: entry (/{_entry_name}) does not exist\u001b[0m\n")
        s_exit(2)
    _shm_folder, _shm_entry = shm_gen()
    determine_decrypt(directory + _entry_name, _shm_folder, _shm_entry)
    _copy_line, _index = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines(), 0
    if arguments[2] in ('username', '-u'):
        _index = 1
    elif arguments[2] in ('password', '-p'):
        _index = 0
    elif arguments[2] in ('url', '-l'):
        _index = 2
    elif arguments[2] in ('note', '-n'):
        _index = 3
    if 'WAYLAND_DISPLAY' in environ:  # Wayland clipboard detection
        run(['wl-copy', _copy_line[_index].rstrip()])
        Popen('sleep 30; wl-copy -c', shell=True)
    elif uname()[0] == 'Haiku':  # Haiku clipboard detection
        run(['clipboard', '-c', _copy_line[_index].rstrip()])
        Popen('sleep 30; clipboard -r', shell=True)
    elif exists("/data/data/com.termux"):  # Termux (Android) clipboard detection
        run(['termux-clipboard-set', _copy_line[_index].rstrip()])
        Popen("sleep 30; termux-clipboard-set ''", shell=True)
    else:  # X11 clipboard detection
        run(['xclip', '-sel', 'c'], stdin=Popen(['echo', '-n', _copy_line[_index].rstrip()], stdout=PIPE).stdout)
        Popen("sleep 30; echo -n '' | xclip -sel c", shell=True)
    rmtree(f"{tmp_dir}{_shm_folder}")


def remove_data():  # deletes an entry from the server and flags it for local deletion on sync
    _entry_name = arguments[0]
    determine_decrypt(f"{home}/.config/sshyp/lock.gpg", None, None)
    if not ssh_error:
        run(['ssh', '-i', f"{home}/.ssh/sshyp", '-p', port, f"{username_ssh}@{ip}",
             f'cd /lib/sshyp; python3 -c \'from sshync import delete; delete("{_entry_name}", "remotely")\''])
    else:
        offline_delete(_entry_name, 'locally')


def extension_runner():  # checks extension config files for matches to argument, runs extensions
    from configparser import ConfigParser
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
        ssh_error, success_flag, sync_flag, silent_sync = False, False, False, False
        arg_start, device_type = None, None  # set to avoid PEP8 warnings
        # retrieve typed argument
        arguments = argv[1:]
        arg_count = len(arguments)

        if arg_count < 1 or (arg_count > 0 and arguments[0] != 'tweak'):
            if arg_count > 0 and arguments[0].startswith('/'):
                arg_start = 1
            else:
                arg_start = 0

            # import saved userdata
            tmp_dir = f"{home}/.config/sshyp/tmp/"
            try:
                sshyp_data = open(f"{home}/.config/sshyp/sshyp-data").readlines()
                device_type = sshyp_data[0].rstrip()
                if device_type == 'client':
                    directory = f"{home}/.local/share/sshyp/"
                    gpg_id = sshyp_data[1].rstrip()
                    editor = sshyp_data[2].rstrip()
                    quick_unlock_enabled = sshyp_data[3].rstrip()
                    if isfile(f"{home}/.config/sshyp/sshyp.sshync"):
                        ssh_info = get_profile(f"{home}/.config/sshyp/sshyp.sshync")
                        username_ssh = ssh_info[0].rstrip()
                        ip = ssh_info[1].rstrip()
                        port = ssh_info[2].rstrip()
                        directory_ssh = str(ssh_info[4].rstrip())
                        client_device_id = listdir(f"{home}/.config/sshyp/devices")[0].rstrip()
                        ssh_error = int(open(f"{home}/.config/sshyp/ssh-error").read().rstrip())
                        if ssh_error == 1:
                            ssh_error = copy_id_check(port, username_ssh, ip, client_device_id)
                        else:
                            ssh_error = False
                    else:
                        ssh_error = True
            except (FileNotFoundError, IndexError):
                print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print("not all necessary configuration files are present - please run 'sshyp tweak'")
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
                s_exit(1)
        else:
            tweak()
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
                            print(f"\n\u001b[38;5;9merror: field does not exist in entry\u001b[0m\n")
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

            elif arg_count == 1 and arg_start == 1:
                success_flag = True
                read_shortcut()

        else:  # server arguments
            if arg_count < 1:
                arguments.append('help')
                print_info()
            elif arg_count > 1 and arguments[0] == 'whitelist':
                if arguments[1] in ('list', '-l'):
                    success_flag = True
                    whitelist_list()
                elif arguments[1] in ('add', 'del'):
                    success_flag = True
                    whitelist_manage()
                elif arguments[1] == 'setup':
                    success_flag = True
                    whitelist_setup()

        if arg_count > 0 and success_flag == 0 and arguments[0] != 'sync':
            if device_type == 'client' and arguments[0] not in ('help', '-h', 'version', '-v', 'license'):
                extension_runner()
            else:
                print_info()
        elif (not ssh_error and sync_flag) or (arg_count > 0 and arguments[0] == 'sync'):
            sync()

    except KeyboardInterrupt:
        print('\n')
