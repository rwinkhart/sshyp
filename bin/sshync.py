#!/usr/bin/python3

# sshync 2022.01.16.unreleased11

# external modules

from os import mkdir, path, remove, system, walk
from os.path import getmtime, join, expanduser
from sys import exit as s_exit
from pathlib import Path


# utility functions

def get_titles_mods(_directory, _destination, _user_data):
    _title_list, _mod_list = [], []
    Path(path.expanduser('~/.config/sshync')).mkdir(0o700, parents=True, exist_ok=True)  # create config directory
    # local fetching
    if _destination == 'l':
        remove(expanduser('~/.config/sshync/database'))  # assumed to exist because remote runs first
        open(expanduser('~/.config/sshync/database'), 'w')  # create blank database file
        for _root, _directories, _files in walk(_directory):
            for _filename in _files:
                _title_list.append(join(_root.replace(_directory, '', 1), _filename))
                _mod_list.append(int(getmtime(join(_root, _filename))))
        for _title in _title_list:
            open(expanduser('~/.config/sshync/database'), 'a').write(str(_title) + '\n')
        open(expanduser('~/.config/sshync/database'), 'a').write('^&*\n')
        for _mod in _mod_list:
            open(expanduser('~/.config/sshync/database'), 'a').write(str(_mod) + '\n')
    # remote fetching
    if _destination == 'r':
        system(f"ssh -i '{_user_data[5]}' -p {_user_data[2]} {_user_data[0]}@{_user_data[1]} \"python -c 'import sshync"
               f"; sshync.get_titles_mods(\"'\"{_user_data[4]}\"'\", \"'\"l\"'\", \"'\"{_user_data}\"'\")'\"")
        system(f"sftp -P {_user_data[2]} {_user_data[0]}@{_user_data[1]}:"
               f"'{expanduser(f'/home/{_user_data[0]}/.config/sshync/database')}' "
               f"'{expanduser('~/.config/sshync/database')}'")
        _titles, _sep, _mods = ' '.join(open(expanduser('~/.config/sshync/database')).readlines()).replace('\n', '')\
            .partition('^&*')
        _title_list, _mod_list = _titles.split(' ')[:-1], _mods.split(' ')[1:]
    return _title_list, _mod_list


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


def make_profile(_profile_dir, _local_dir, _remote_dir, _identity, _ip, _port, _user):
    open(_profile_dir, 'w').write(_user + '\n' + _ip + '\n' + _port + '\n' + _local_dir + '\n' + _remote_dir + '\n' +
                                  _identity + '\n')


def get_profile(_profile_dir):
    try:
        _profile_data = open(_profile_dir).readlines()
    except (FileNotFoundError, IndexError):
        print('\nEither the profile does not exist, or it is corrupted.\n')
        _profile_data = None
        s_exit()
    # extract data from profile
    _user = _profile_data[0].replace('\n', '')
    _ip = _profile_data[1].replace('\n', '')
    _port = _profile_data[2].replace('\n', '')
    _local_dir = _profile_data[3].replace('\n', '')
    _remote_dir = _profile_data[4].replace('\n', '')
    _identity = _profile_data[5].replace('\n', '')
    return _user, _ip, _port, _local_dir, _remote_dir, _identity


def run_profile(_profile_dir):
    _user_data = get_profile(_profile_dir)
    _remote_titles_mods_saver = get_titles_mods(_user_data[4], 'r', _user_data)  # saved to prevent re-walking directory
    _index_l = sort_titles_mods(_remote_titles_mods_saver, get_titles_mods(_user_data[3], 'l', _user_data))
    _index_r = sort_titles_mods(_index_l, _remote_titles_mods_saver)
    _i = -1
    for _title in _index_l[0]:
        _i += 1
        if _title in _index_r[0]:
            # compare mod times and sync
            if int(_index_l[1][_i]) > int(_index_r[1][_i]):
                print(f"[{_title}] Local is newer, uploading...")
                system(f"sftp -p -q -i '{_user_data[5]}' -P {_user_data[2]} {_user_data[0]}@{_user_data[1]}:"
                       f"{_user_data[4]}{'/'.join(_title.split('/')[:-1]) + '/'} <<< $'put {_user_data[3]}{_title}'")
            elif int(_index_l[1][_i]) < int(_index_r[1][_i]):
                print(f"[{_title}] Remote is newer, downloading...")
                system(f"sftp -p -q -i '{_user_data[5]}' -P {_user_data[2]} {_user_data[0]}@{_user_data[1]}:"
                       f"'{_user_data[4]}'{_title} {_user_data[3]}{'/'.join(_title.split('/')[:-1]) + '/'}")
        else:
            print(f"[{_title}] Not on remote server, uploading...")
            system(f"sftp -p -q -i '{_user_data[5]}' -P {_user_data[2]} {_user_data[0]}@{_user_data[1]}:{_user_data[4]}"
                   f"{'/'.join(_title.split('/')[:-1]) + '/'} <<< $'put {_user_data[3]}{_title}'")
    for _title in _index_r[0]:
        if _title not in _index_l[0]:
            print(f"[{_title}] Not in local directory, downloading...")
            system(f"sftp -p -q -i '{_user_data[5]}' -P {_user_data[2]} {_user_data[0]}@{_user_data[1]}:"
                   f"'{_user_data[4]}{_title}' {_user_data[3]}{'/'.join(_title.split('/')[:-1]) + '/'}")
