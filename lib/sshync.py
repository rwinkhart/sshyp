#!/usr/bin/env python3
from os import listdir, remove, walk
from os.path import expanduser, isdir, getmtime, join
from subprocess import CalledProcessError, PIPE, run
from sys import exit as s_exit
home = expanduser("~")


# PORT START SSHYNC-REMOTE
# REMOTE
# prints all necessary remote data to stdout
def remote_list_gen(_client_device_name, _remote_dir):
    # deletions
    for _file in listdir(f"{home}/.config/sshyp/deleted"):
        _file_path, _sep, _device = _file.partition('\x1f')
        _file_path = _file_path.replace('\x1e', '/')
        if _device == _client_device_name:
            print(_file_path)
            try:
                remove(f"{home}/.config/sshyp/deleted/{_file}")
            except FileNotFoundError:
                pass
    print('\x1d')
    # folders
    for _root, _directories, _files in walk(f"{home}/.local/share/sshyp"):
        for _dir in _directories:
            print(f"{_root.replace(home, '')}/{_dir}")
    print('\x1d')
    # titles and mod times
    get_local_data(_remote_dir, 'server')
# PORT END SSHYNC-REMOTE


# HYBRID
# deletes a file or folder and/or marks it for deletion upon syncing
def delete(_file_path, _target_database, _silent):
    from shutil import rmtree
    _directory = f"{home}/.local/share/sshyp/"
    try:
        if isdir(_directory + _file_path):
            rmtree(_directory + _file_path)
        else:
            remove(f"{_directory}{_file_path}.gpg")
    except FileNotFoundError:
        if not _silent:
            print(f"location does not exist {_target_database}")
    if _target_database == 'remotely':
        for _device_name in listdir(f"{home}/.config/sshyp/devices"):
            open(f"{home}/.config/sshyp/deleted/" + _file_path.replace('/', '\x1e') + '\x1f' + _device_name, 'w')


# retrieves and returns titles and mod times from the local device
def get_local_data(_directory, _device):
    _title_list, _mod_list = [], []
    for _root, _directories, _files in walk(_directory):
        for _filename in _files:
            _title_list.append(join(_root.replace(_directory, '', 1), _filename))
            _mod_list.append(int(getmtime(join(_root, _filename))))
    if _device == 'server':
        for _title in _title_list:
            print(_title.rstrip())
        for _time in _mod_list:
            print(_time)
    return _title_list, _mod_list


# LOCAL
# captures and returns all necessary data from the remote server
def remote_list_fetch(_user_data):
    try:
        _remote_data = run(['ssh', '-i', _user_data[5], '-p', _user_data[2], f"{_user_data[0]}@{_user_data[1]}",
                            f'cd /lib/sshyp; python3 -c \'from sshync import remote_list_gen; remote_list_gen'
                            f'("{_user_data[6]}", "{_user_data[4]}")\''], stdout=PIPE, text=True, check=True
                           ).stdout.split('\x1d')
    except CalledProcessError:
        print('\n\u001b[38;5;9merror: failed to connect to the remote server\u001b[0m\n')
        _remote_data = ''
        s_exit(5)
    _deletion_database = _remote_data[0].strip().splitlines()
    _folder_database = _remote_data[1].strip().splitlines()
    _titles_mods = _remote_data[2].strip().splitlines()
    return _deletion_database, _folder_database, _titles_mods[:len(_titles_mods)//2], \
        _titles_mods[len(_titles_mods)//2:]


# checks for and acts upon files and folders marked for deletion
def deletion_sync(_deletion_database, _silent):
    for _file in _deletion_database:
        if _file != '':
            if not _silent:
                print(f"\u001b[38;5;208m{_file}\u001b[0m has been sheared, removing...")
            delete(_file, 'locally', False)


# creates matches of remote folders on the local client
def folder_sync(_folder_database):
    from pathlib import Path
    for _folder in _folder_database:
        if _folder != '' and not isdir(home + _folder):
            print(f"\u001b[38;5;2m{_folder.replace('/.local/share/sshyp/', '')}/\u001b[0m does not exist locally, "
                  f"creating...")
            Path(home + _folder).mkdir(mode=0o700, parents=True, exist_ok=True)


# creates and returns two lists (of titles and mod times) generated by sorting information from two provided 2D lists
def sort_titles_mods(_list_1, _list_2):
    _title_list_2_sorted, _mod_list_2_sorted = [], []
    # title sorting
    for _title in _list_1[0]:
        if _title in _list_2[0]:
            _title_list_2_sorted.append(_title)
    for _title in _list_2[0]:
        if _title not in _title_list_2_sorted:
            _title_list_2_sorted.append(_title)
    # mod time sorting
    for _title in _title_list_2_sorted:
        _mod_list_2_sorted.append(_list_2[1][_list_2[0].index(_title)])
    return _title_list_2_sorted, _mod_list_2_sorted


# creates a sshync job profile
def make_profile(_profile_dir, _local_dir, _remote_dir, _identity, _ip, _port, _user):
    open(_profile_dir, 'w').write(f"{_user}\n{_ip}\n{_port}\n{_local_dir}\n{_remote_dir}\n{_identity}\n")


# returns a list of data read from a sshync job profile
def get_profile(_profile_dir):
    try:
        _profile_data = open(_profile_dir).readlines()
    except (FileNotFoundError, IndexError):
        print('\n\u001b[38;5;9merror: the profile does not exist or is corrupted\u001b[0m\n')
        _profile_data = None
        s_exit(2)
    _user = _profile_data[0].rstrip()
    _ip = _profile_data[1].rstrip()
    _port = _profile_data[2].rstrip()
    _local_dir = _profile_data[3].rstrip()
    _remote_dir = _profile_data[4].rstrip()
    _identity = _profile_data[5].rstrip()
    _client_device_id = listdir(f"{home}/.config/sshyp/devices")[0].rstrip()
    return _user, _ip, _port, _local_dir, _remote_dir, _identity, _client_device_id


# runs a sshync job profile
def run_profile(_profile_dir, _silent):
    # import profile data
    _user_data = get_profile(_profile_dir)
    # fetch remote lists
    _deletion_database, _folder_database, _remote_titles, _remote_mods = remote_list_fetch(_user_data)
    _remote_titles_mods = (_remote_titles, _remote_mods)
    # sync deletions and folders
    deletion_sync(_deletion_database, _silent)
    folder_sync(_folder_database)
    # sort titles and mods
    _index_local = sort_titles_mods(_remote_titles_mods, get_local_data(_user_data[3], 'client'))
    _index_remote = sort_titles_mods(_index_local, _remote_titles_mods)
    # sync new and updated files
    _i = -1
    for _title in _index_local[0]:
        _i += 1
        if _title in _index_remote[0]:
            # compare mod times and sync
            if int(_index_local[1][_i]) > int(_index_remote[1][_i]):
                print(f"\u001b[38;5;4m{_title[:-4]}\u001b[0m is newer locally, uploading...")
                run(['scp', '-pqs', '-P', _user_data[2], '-i', _user_data[5], _user_data[3] + _title,
                     f"{_user_data[0]}@{_user_data[1]}:{_user_data[4]}{'/'.join(_title.split('/')[:-1]) + '/'}"])
            elif int(_index_local[1][_i]) < int(_index_remote[1][_i]):
                print(f"\u001b[38;5;2m{_title[:-4]}\u001b[0m is newer remotely, downloading...")
                run(['scp', '-pqs', '-P', _user_data[2], '-i', _user_data[5],
                     f"{_user_data[0]}@{_user_data[1]}:{_user_data[4]}{_title}",
                     f"{_user_data[3]}{'/'.join(_title.split('/')[:-1]) + '/'}"])
        else:
            print(f"\u001b[38;5;4m{_title[:-4]}\u001b[0m is not on remote server, uploading...")
            run(['scp', '-pqs', '-P', _user_data[2], '-i', _user_data[5], _user_data[3] + _title,
                 f"{_user_data[0]}@{_user_data[1]}:{_user_data[4]}{'/'.join(_title.split('/')[:-1]) + '/'}"])
    for _title in _index_remote[0]:
        if _title not in _index_local[0]:
            print(f"\u001b[38;5;2m{_title[:-4]}\u001b[0m is not in local directory, downloading...")
            run(['scp', '-pqs', '-P', _user_data[2], '-i', _user_data[5],
                 f"{_user_data[0]}@{_user_data[1]}:{_user_data[4]}{_title}",
                 f"{_user_data[3]}{'/'.join(_title.split('/')[:-1]) + '/'}"])
