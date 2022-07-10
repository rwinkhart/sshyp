#!/bin/python3

# external modules

from os import environ, listdir, path, remove, system, uname, walk
from pathlib import Path
from random import randint, SystemRandom
from shutil import get_terminal_size, move, rmtree
import sshync
import string
from subprocess import CalledProcessError, Popen, PIPE, run
from sys import argv, exit as s_exit
from textwrap import fill


# BELOW - utility functions

def entry_list_gen(_directory=path.expanduser('~/.local/share/sshyp/')):  # generates and prints full entry list
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
                print(f"\u001b[38;5;15;48;5;238mpassword:\u001b[0m\n{_entry_lines[0]}")


def replace_line(file_name, line_num, text):  # replaces text in a given line with different text
    _lines = open(file_name, 'r').readlines()
    _lines[line_num] = text
    open(file_name, 'w').writelines(_lines)


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


def shm_gen(_tmp_dir=path.expanduser('~/.config/sshyp/tmp/')):  # creates a temporary directory for entry editing
    _shm_folder_gen = ''.join(SystemRandom().choice(string.ascii_letters + string.digits)
                              for _ in range(randint(10, 30)))
    _shm_entry_gen = ''.join(SystemRandom().choice(string.ascii_letters + string.digits)
                             for _ in range(randint(10, 30)))
    Path(_tmp_dir + _shm_folder_gen).mkdir(0o700)
    return _shm_folder_gen, _shm_entry_gen


def pass_gen():  # generates and returns a random password based on user-specified options
    def _pass_gen_function(__complexity, __length):
        if __complexity.lower() == 's':
            __character_pool = string.ascii_letters + string.digits
        else:
            __character_pool = string.ascii_letters + string.digits + string.punctuation
        __gen = ''.join(SystemRandom().choice(__character_pool) for _ in range(__length))
        __min_special, __special = round(.2 * __length), 0
        for __character in __gen:
            if not __character.isalpha():
                __special += 1
        if __special < __min_special:
            __gen = _pass_gen_function(__complexity, __length)
        return __gen
    try:
        _length = int(input('password length: '))
    except ValueError:
        print(f"\n\u001b[38;5;9merror: a non-integer value was input for password length\u001b[0m\n")
        _gen = pass_gen()
        return _gen
    if _length > 840:
        _length = 840
        print('\n\u001b[38;5;9mpassword length has been limited to the maximum of 840 characters\u001b[0m\n')
    _complexity = str(input('password complexity - simple (for compatibility) or complex (for security)? (s/C) '))
    _gen = _pass_gen_function(_complexity, _length)
    return _gen


def encrypt(_shm_folder, _shm_entry, _location):  # encrypts an entry and cleans up the temporary files
    system(f"{gpg} -qr {str(gpg_id)} -e '{tmp_dir}{_shm_folder}/{_shm_entry}'")
    move(f"{tmp_dir}{_shm_folder}/{_shm_entry}.gpg", f"{directory}{_location}.gpg")
    rmtree(f"{tmp_dir}{_shm_folder}")


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


def edit_note(_shm_folder, _shm_entry):  # edits the note attached to an entry
    lines = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}").readlines()
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(lines[0:3])
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'w').writelines(lines[3:])
    system(f"{editor} {tmp_dir}{_shm_folder}/{_shm_entry}-n")
    edit_notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n").read()
    open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'a').write(edit_notes)


def copy_name_check(_port, _username_ssh, _ip, _client_device_name):
    # attempts to connect to the user's server via ssh to register the device for syncing
    _command = f"ssh -o ConnectTimeout=3 -i '{path.expanduser('~/.ssh/sshyp')}' -p {_port} {_username_ssh}@{_ip} " \
               f"\"touch '/home/{_username_ssh}/.config/sshyp/devices/{_client_device_name}'\""
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
    # storage/config directory creation
    Path(path.expanduser('~/.local/share/sshyp')).mkdir(0o700, parents=True, exist_ok=True)
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
        open(path.expanduser('~/.config/sshyp/sshyp-device'), 'w').write(_device_type)
        Path(path.expanduser('~/.config/sshyp/deleted')).mkdir(0o700, parents=True, exist_ok=True)
        print('\nmake sure the ssh service is running and properly configured\n\nconfiguration complete\n')
        s_exit(0)
    else:
        # device type configuration
        _device_type = 'c'  # ensure device type flag is properly set
        open(path.expanduser('~/.config/sshyp/sshyp-device'), 'w').write(_device_type)

        # gpg configuration
        _gpg_id = input('\nsshyp requires the use of a unique gpg key - use an (e)xisting key or (g)enerate a new one? '
                        '(E/g) ')
        if _gpg_id.lower() != 'g':
            system(f"{gpg} -k")
            _gpg_id = str(input('gpg key id: '))
        else:
            print('\na unique gpg key is being generated for you...')
            if not Path(path.expanduser('~/.config/sshyp/gpg-gen')).is_file():
                open(path.expanduser('~/.config/sshyp/gpg-gen'), 'w').write('Key-Type: 1\nKey-Length: 4096\nKey-Usage:\
                 sign encrypt\nName-Real: sshyp\nName-Comment: password manager encryption\nName-Email: \
                 https://github.com/rwinkhart/sshyp\nExpire-Date: 0')
            run(f"{gpg} --batch --generate-key '{path.expanduser('~/.config/sshyp/gpg-gen')}'", shell=True)
            _gpg_id = run(f"{gpg} -k", shell=True, stdout=PIPE, text=True).stdout.split('\n')[-4].strip()

        # lock file generation
        if Path(path.expanduser('~/.config/sshyp/lock.gpg')).is_file():
            remove(path.expanduser('~/.config/sshyp/lock.gpg'))
        open(path.expanduser('~/.config/sshyp/lock'), 'w')
        system(f"{gpg} -qr {str(_gpg_id)} -e {path.expanduser('~/.config/sshyp/lock')}")
        remove(path.expanduser('~/.config/sshyp/lock'))

        # ssh key configuration
        _ssh_gen = (input('\nmake sure the ssh service on the remote server is running and properly configured'
                          '\n\nsync support requires a unique ssh key - would you like to have this automatically '
                          'generated? (Y/n) '))
        if _ssh_gen.lower() != 'n':
            if uname()[0] == 'Haiku':
                Path(f"{path.expanduser('~')}/.ssh").mkdir(0o700, exist_ok=True)
            system('ssh-keygen -t ed25519 -f ~/.ssh/sshyp')
        else:
            print(f"\nensure that the key file you are using is located at {path.expanduser('~/.ssh/sshyp')}")

        # ssh ip+port configuration
        _ip_port = str(input('\nexample input: 10.10.10.10:9999\n\nip and ssh port of the remote server: '))
        _ip, _sep, _port = _ip_port.partition(':')

        # ssh user configuration
        _username_ssh = str(input('\nusername of the remote server: '))

        # sshyp-only data storage
        open(path.expanduser('~/.config/sshyp/sshyp-data'), 'w')\
            .write(_gpg_id + '\n' + input('\nexample input: vim\n\npreferred text editor: '))

        # sshync profile generation
        sshync.make_profile(path.expanduser('~/.config/sshyp/sshyp.sshync'),
                            path.expanduser('~/.local/share/sshyp/'), f"/home/{_username_ssh}/.local/share/sshyp/",
                            path.expanduser('~/.ssh/sshyp'), _ip, _port, _username_ssh)

        # device name configuration
        for _name in listdir(path.expanduser('~/.config/sshyp/devices')):  # remove existing device name
            remove(f"{path.expanduser('~/.config/sshyp/devices/')}{_name}")
        print('\n\u001b[4;1mimportant:\u001b[0m This name \u001b[4;1mmust\u001b[0m be unique amongst your client '
              'devices\n\nthis is used to keep track of which devices have up-to-date databases\n')
        _client_device_name = str(input('device name: '))
        open(f"{path.expanduser('~/.config/sshyp/devices/')}{_client_device_name}", 'w')
        copy_name_check(_port, _username_ssh, _ip, _client_device_name)

        print('\nconfiguration complete\n')


def print_info():  # prints help text based on argument
    if argument_list[0] == 'help' or argument_list[0] == '--help' or argument_list[0] == '-h':
        print('\n\u001b[1msshyp  copyright (c) 2021-2022  randall winkhart\u001b[0m\n')
        print("this is free software, and you are welcome to redistribute it under certain conditions;\nthis program "
              "comes with absolutely no warranty;\ntype `sshyp license' for details")
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
        print('sync/-s                  manually sync the entry directory via sshync\n')
        print('\u001b[1mflags:\u001b[0m')
        print('add:')
        print(' password/-p             add a password entry')
        print(' note/-n                 add a note entry')
        print(' folder/-f               add a new folder for entries')
        print('edit:')
        print(' rename/relocate/-r      rename or relocate an entry')
        print(' username/-u             change the username of an entry')
        print(' password/-p             change the password of an entry')
        print(' note/-n                 change the note attached to an entry')
        print(' url/-l                  change the url attached to an entry')
        print('copy:')
        print(' username/-u             copy the username of an entry to your clipboard')
        print(' password/-p             copy the password of an entry to your clipboard')
        print(' url/-l                  copy the url of an entry to your clipboard')
        print(' note/-n                 copy the note of an entry to your clipboard')
        print('gen:')
        print(' update/-u               generate a password for an existing entry\n')
        print("\u001b[1mtip:\u001b[0m you can quickly read an entry with 'sshyp /<entry name>'")
    elif argument_list[0] == 'version' or argument_list[0] == '-v':
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
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                    \u001b[38;5;15;48;5;8mversion 1.1.0'
              '\u001b[38;5;15;48;5;15m                     \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                 \u001b[38;5;15;48;5;8mthe sheecrets '
              'update\u001b[38;5;15;48;5;15m                 \u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m/\u001b[38;5;15;48;5;15m                                                      '
              '\u001b[38;5;7;48;5;8m/\u001b[0m')
        print('\u001b[38;5;7;48;5;8m<><><><><><><><><><><><><><><><><><><><><><><><><><><><>\u001b[0m\n')
        print('see https://github.com/rwinkhart/sshyp for more information\n')
    elif argument_list[0] == 'license':
        print('\nThis program is free software: you can redistribute it and/or modify it under the terms of the GNU '
              'General\nPublic License as published by the Free Software Foundation, either version 3 of the License,'
              '\nor (at your option) any later version.\n\nThis program is distributed in the hope that it will be '
              'useful, but WITHOUT ANY WARRANTY;\nwithout even the implied warranty of MERCHANTABILITY or FITNESS FOR A'
              ' PARTICULAR PURPOSE.\nSee the GNU General Public License for more details.'
              '\n\nhttps://opensource.org/licenses/GPL-3.0\n')
    elif argument_list[0] == 'add':
        print('\n\u001b[1musage:\u001b[0m sshyp add [flag [<entry name>]]\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('add:')
        print(' password/-p             add a password entry')
        print(' note/-n                 add a note entry')
        print(' folder/-f               add a new folder for entries\n')
    elif argument_list[0] == 'edit':
        print('\n\u001b[1musage:\u001b[0m sshyp edit [flag [<entry name>]]\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('edit:')
        print(' rename/relocate/-r      rename or relocate an entry')
        print(' username/-u             change the username of an entry')
        print(' password/-p             change the password of an entry')
        print(' url/-l                  change the url attached to an entry')
        print(' note/-n                 change the note attached to an entry\n')
    elif argument_list[0] == 'copy':
        print('\n\u001b[1musage:\u001b[0m sshyp copy [flag [<entry name>]]\u001b[0m\n')
        print('\u001b[1mflags:\u001b[0m')
        print('copy:')
        print(' username/-u             copy the username of an entry to your clipboard')
        print(' password/-p             copy the password of an entry to your clipboard')
        print(' url/-l                  copy the url of an entry to your clipboard')
        print(' note/-n                 copy the note of an entry to your clipboard\n')


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
           f"'import sshypRemote; sshypRemote.deletion_check(\"'\"{client_device_name}\"'\")'\"")
    system(f"scp -pqs -P {port} -i '{path.expanduser('~/.ssh/sshyp')}' {username_ssh}@{ip}:'/home/{username_ssh}"
           f"/.config/sshyp/deletion_database' {path.expanduser('~/.config/sshyp/')}")
    try:
        _deletion_database = open(path.expanduser('~/.config/sshyp/deletion_database')).readlines()
    except (FileNotFoundError, IndexError):
        print('\n\u001b[38;5;9merror: the deletion database does not exist or is corrupted\u001b[0m\n')
        _deletion_database = None
        s_exit(1)
    for _file in _deletion_database:
        if _file[:-1].endswith('/'):
            try:
                if silent_sync != 1:
                    print(f"\u001b[38;5;208m{_file[:-1]}\u001b[0m has been sheared, removing...")
                rmtree(f"{directory}{_file[:-1]}")
            except FileNotFoundError:
                if silent_sync != 1:
                    print('folder does not exist locally.')
        else:
            try:
                if silent_sync != 1:
                    print(f"\u001b[38;5;208m{_file[:-1]}\u001b[0m has been sheared, removing...")
                remove(f"{directory}{_file[:-1]}.gpg")
            except (FileNotFoundError, IsADirectoryError):
                if silent_sync != 1:
                    print('file does not exist locally.')
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


def add_entry():  # adds a new entry
    _shm_folder, _shm_entry = None, None  # sets base-line values to avoid errors
    if len(argument_list) < 3:
        _entry_name = entry_name_fetch('name of new entry: ')
    else:
        _entry_name = entry_name_fetch(2)
    if Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) already exists\u001b[0m\n")
        s_exit(1)
    if argument_list[1] == 'note' or argument_list[1] == '-n':
        _shm_folder, _shm_entry = shm_gen()
        system(f"{editor} {tmp_dir}{_shm_folder}/{_shm_entry}-n")
        _notes = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}-n", 'r').read()
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines('\n\n\n' + _notes)
    elif argument_list[1] == 'password' or argument_list[1] == '-p':
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
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_password + '\n' + _username + '\n' + _url +
                                                                     '\n' + _notes)
        print('\n\u001b[1mentry preview:\u001b[0m')
        entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(_shm_folder, _shm_entry, _entry_name)


def add_folder():  # creates a new folder
    if len(argument_list) < 3:
        _entry_name = entry_name_fetch('name of new folder: ')
    else:
        _entry_name = entry_name_fetch(2)
    Path(directory + _entry_name).mkdir(0o700)
    system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"mkdir -p '{directory_ssh}"
           f"{_entry_name}'\"")


def rename():  # renames an entry or folder
    if argument == 'edit rename' or argument == 'edit relocate' or argument == 'edit -r':
        _entry_name = entry_name_fetch('entry/folder to rename/relocate: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file() and not Path(f"{directory}{_entry_name}").is_dir():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(1)
    _new_name = str(input('new name: '))
    print(f"{directory}{_new_name}")
    if Path(f"{directory}{_new_name}.gpg").is_file() or Path(f"{directory}{_new_name}").is_dir():
        print(f"\n\u001b[38;5;9merror: ({_new_name}) already exists\u001b[0m\n")
        s_exit(1)
    if _entry_name.endswith('/'):
        move(f"{directory}{_entry_name}", f"{directory}{_new_name}")
        system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"mkdir -p '{directory_ssh}"
               f"{_new_name}'\"")
    else:
        move(f"{directory}{_entry_name}.gpg", f"{directory}{_new_name}.gpg")
    system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"cd /bin; python -c "
           f"'import sshypRemote; sshypRemote.delete(\"'\"{_entry_name}\"'\")'\"")


def edit():  # edits the contents of an entry
    _shm_folder, _shm_entry = None, None  # sets base-line values to avoid errors
    if len(argument_list) < 3:
        _entry_name = entry_name_fetch('entry to edit: ')
    else:
        _entry_name = entry_name_fetch(2)
    if not Path(f"{directory}{_entry_name}.gpg").is_file():
        print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
        s_exit(1)
    _shm_folder, _shm_entry = shm_gen()
    decrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg)

    # compatibility check for GNU pass entries (ensuring they have at least four lines)
    _lines = open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'r').readlines()
    if len(_lines) < 3:
        while len(_lines) < 3:
            _lines.append('\n')
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_lines)

    if argument_list[1] == 'username' or argument_list[1] == '-u':
        _detail = str(input('new username: '))
        replace_line(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 1, _detail + '\n')
    elif argument_list[1] == 'password' or argument_list[1] == '-p':
        _detail = str(input('new password: '))
        replace_line(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 0, _detail + '\n')
    elif argument_list[1] == 'url' or argument_list[1] == '-l':
        _detail = str(input('new url: '))
        replace_line(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 2, _detail + '\n')
    elif argument_list[1] == 'note' or argument_list[1] == '-n':
        edit_note(_shm_folder, _shm_entry)
    remove(f"{directory}{_entry_name}.gpg")
    print('\n\u001b[1mentry preview:\u001b[0m')
    entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
    encrypt(_shm_folder, _shm_entry, _entry_name)


def gen():  # generates a password for a new or an existing entry
    _username, _url, _notes = None, None, None  # sets base-line values to avoid errors
    if argument == 'gen update' or argument == 'gen -u' or argument == 'gen':
        _entry_name = entry_name_fetch('name of entry: ')
    elif argument_list[1] == 'update' or argument_list[1] == '-u':
        _entry_name = entry_name_fetch(2)
        if not Path(f"{directory}{_entry_name}.gpg").is_file():
            print(f"\n\u001b[38;5;9merror: entry ({_entry_name}) does not exist\u001b[0m\n")
            s_exit(1)
    else:
        _entry_name = entry_name_fetch(1)
    if len(argument_list) == 1 or (not argument_list[1] == 'update' and not argument_list[1] == '-u'):
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
        open(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 'w').writelines(_password + '\n' + _username + '\n' + _url + '\n'
                                                                     + _notes)
        print('\n\u001b[1mentry preview:\u001b[0m')
        entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
        encrypt(_shm_folder, _shm_entry, _entry_name)
    else:
        _password = pass_gen()
        _shm_folder, _shm_entry = shm_gen()
        decrypt(directory + _entry_name, _shm_folder, _shm_entry, gpg)
        replace_line(f"{tmp_dir}{_shm_folder}/{_shm_entry}", 0, _password + '\n')
        remove(f"{directory}{_entry_name}.gpg")
        print('\n\u001b[1mentry preview:\u001b[0m')
        entry_reader(f"{tmp_dir}{_shm_folder}/{_shm_entry}")
        encrypt(_shm_folder, _shm_entry, _entry_name)


def copy_data():  # copies a specified field of an entry to the clipboard
    if len(argument_list) < 3:
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
        if argument_list[1] == 'username' or argument_list[1] == '-u':
            system('clipboard -c ' + "'" + _copy_line[1].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'password' or argument_list[1] == '-p':
            system('clipboard -c ' + "'" + _copy_line[0].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'url' or argument_list[1] == '-l':
            system('clipboard -c ' + "'" + _copy_line[2].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'note' or argument_list[1] == '-n':
            system('clipboard -c ' + "'" + _copy_line[3].replace('\n', '').replace("'", "'\\''") + "'")
        Popen('sleep 30; clipboard -r', shell=True, close_fds=True)
    elif Path("/data/data/com.termux").exists():  # Termux (Android) clipboard detection
        if argument_list[1] == 'username' or argument_list[1] == '-u':
            system('termux-clipboard-set ' + "'" + _copy_line[1].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'password' or argument_list[1] == '-p':
            system('termux-clipboard-set ' + "'" + _copy_line[0].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'url' or argument_list[1] == '-l':
            system('termux-clipboard-set ' + "'" + _copy_line[2].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'note' or argument_list[1] == '-n':
            system('termux-clipboard-set ' + "'" + _copy_line[3].replace('\n', '').replace("'", "'\\''") + "'")
        Popen("sleep 30; termux-clipboard-set ''", shell=True, close_fds=True)
    elif environ.get('WAYLAND_DISPLAY') == 'wayland-0':  # Wayland clipboard detection
        if argument_list[1] == 'username' or argument_list[1] == '-u':
            system('wl-copy ' + "'" + _copy_line[1].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'password' or argument_list[1] == '-p':
            system('wl-copy ' + "'" + _copy_line[0].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'url' or argument_list[1] == '-l':
            system('wl-copy ' + "'" + _copy_line[2].replace('\n', '').replace("'", "'\\''") + "'")
        elif argument_list[1] == 'note' or argument_list[1] == '-n':
            system('wl-copy ' + "'" + _copy_line[3].replace('\n', '').replace("'", "'\\''") + "'")
        Popen('sleep 30; wl-copy -c', shell=True, close_fds=True)
    else:  # X11 clipboard detection
        if argument_list[1] == 'username' or argument_list[1] == '-u':
            system('echo -n ' + "'" + _copy_line[1].replace('\n', '').replace("'", "'\\''") + "'" + ' | xclip -sel c')
        elif argument_list[1] == 'password' or argument_list[1] == '-p':
            system('echo -n ' + "'" + _copy_line[0].replace('\n', '').replace("'", "'\\''") + "'" + ' | xclip -sel c')
        elif argument_list[1] == 'url' or argument_list[1] == '-l':
            system('echo -n ' + "'" + _copy_line[2].replace('\n', '').replace("'", "'\\''") + "'" + ' | xclip -sel c')
        elif argument_list[1] == 'note' or argument_list[1] == '-n':
            system('echo -n ' + "'" + _copy_line[3].replace('\n', '').replace("'", "'\\''") + "'" + ' | xclip -sel c')
        Popen("sleep 30; echo -n '' | xclip -sel c", shell=True, close_fds=True)
    rmtree(f"{tmp_dir}{_shm_folder}")


def remove_data():  # deletes an entry from the server and flags it for local deletion on sync
    if argument == 'shear' or argument == '-rm':
        _entry_name = entry_name_fetch('entry/folder to shear: ')
    else:
        _entry_name = entry_name_fetch(1)
    decrypt(path.expanduser('~/.config/sshyp/lock.gpg'), 0, 0, gpg)
    system(f"ssh -i '{path.expanduser('~/.ssh/sshyp')}' -p {port} {username_ssh}@{ip} \"cd /bin; python -c "
           f"'import sshypRemote; sshypRemote.delete(\"'\"{_entry_name}\"'\")'\"")


if __name__ == "__main__":
    try:
        silent_sync, ssh_error = 0, 0
        # retrieve typed argument
        argument_list, argument = argv, ''
        del argument_list[0]
        for _argument in argument_list:
            argument += _argument + ' '
        argument = argument[:-1]
        if uname()[0] == 'Haiku':  # set proper gpg command for OS
            gpg = 'gpg --pinentry-mode loopback'
        else:
            gpg = 'gpg'

        # import saved userdata
        if argument != 'tweak':
            device_type = ''
            tmp_dir = path.expanduser('~/.config/sshyp/tmp/')
            try:
                device_type = open(path.expanduser('~/.config/sshyp/sshyp-device')).read().strip()
                if device_type == 'c':
                    ssh_info = sshync.get_profile(path.expanduser('~/.config/sshyp/sshyp.sshync'))
                    username_ssh = ssh_info[0].replace('\n', '')
                    ip = ssh_info[1].replace('\n', '')
                    port = ssh_info[2].replace('\n', '')
                    directory = str(ssh_info[3].replace('\n', ''))
                    directory_ssh = str(ssh_info[4].replace('\n', ''))
                    client_device_name = listdir(path.expanduser('~/.config/sshyp/devices'))[0]
                    sshyp_data = open(path.expanduser('~/.config/sshyp/sshyp-data')).readlines()
                    gpg_id = sshyp_data[0].replace('\n', '')
                    editor = sshyp_data[1].replace('\n', '')
                    ssh_error = int(open(path.expanduser('~/.config/sshyp/ssh-error')).read().strip())
                    if ssh_error != 0:
                        ssh_error = copy_name_check(port, username_ssh, ip, client_device_name)
                else:
                    print('running as server, option disabled')
                    s_exit(0)
            except (FileNotFoundError, IndexError):
                if device_type.lower() != 's':
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
        elif argument_list[0] == 'add':
            if len(argument_list) == 1:
                print_info()
            elif argument_list[1] == 'note' or argument_list[1] == '-n' or argument_list[1] == 'password' or \
                    argument_list[1] == '-p':
                add_entry()
            elif argument_list[1] == 'folder' or argument_list[1] == '-f':
                add_folder()
            else:
                print_info()
                s_exit(0)
        elif argument_list[0] == 'edit':
            if len(argument_list) == 1:
                print_info()
            elif argument_list[1] == 'rename' or argument_list[1] == 'relocate' or argument_list[1] == '-r':
                silent_sync = 1
                rename()
            elif argument_list[1] == 'username' or argument_list[1] == '-u' or argument_list[1] == 'password' or \
                    argument_list[1] == '-p' or argument_list[1] == 'url' or argument_list[1] == '-l' or \
                    argument_list[1] == 'note' or argument_list[1] == '-n':
                edit()
            else:
                print_info()
                s_exit(0)
        elif argument_list[0] == 'gen':
            gen()
        elif argument_list[0] == 'copy':
            if len(argument_list) == 1:
                print_info()
            elif argument_list[1] == 'username' or argument_list[1] == '-u' or argument_list[1] == 'password' or \
                    argument_list[1] == '-p' or argument_list[1] == 'url' or argument_list[1] == '-l' or \
                    argument_list[1] == 'note' or argument_list[1] == '-n':
                copy_data()
            else:
                print_info()
        elif argument_list[0] == 'shear' or argument_list[0] == '-rm':
            remove_data()
        elif argument_list[0] != 'sync' and argument_list[0] != '-s':
            print(f"\n\u001b[38;5;9merror: invalid argument - run 'sshyp help' to list usable commands\u001b[0m\n")
            s_exit(1)

        # sync if any changes were made
        if len(argument_list) > 0 and ssh_error == 0 and \
                ((argument_list[0] == 'sync' or argument_list[0] == '-s' or argument_list[0] == 'gen' or
                  argument_list[0] == 'shear' or argument_list[0] == '-rm') or ((argument_list[0] == 'add'
                                                                                 or argument_list[0] == 'edit')
                                                                                and len(argument_list) > 1)):
            sync()

        s_exit(0)

    except KeyboardInterrupt:
        print('\n')
        s_exit(0)
