#!/usr/bin/env python3
from os import listdir, remove, walk
from os.path import expanduser
from shutil import rmtree


def delete(_file_path, _target_database):  # deletes an entry or folder, should be run remotely via ssh
    try:
        if _file_path.endswith('/'):
            rmtree(f"{expanduser('~/.local/share/sshyp/')}{_file_path}")
        else:
            remove(f"{expanduser('~/.local/share/sshyp/')}{_file_path}.gpg")
    except FileNotFoundError:
        print(f"location does not exist {_target_database}")
    for _device_name in listdir(expanduser('~/.config/sshyp/devices')):
        open(expanduser('~/.config/sshyp/deleted/') + _file_path.replace('/', '\x1e') + '\x1f' + _device_name, 'w')


def deletion_check(_client_device_name):  # creates a list of entries and folders to be deleted from a local machine
    open(expanduser('~/.config/sshyp/deletion_database'), 'w').write('')
    for _file in listdir(expanduser('~/.config/sshyp/deleted')):
        _file_path, _sep, _device = _file.partition('\x1f')
        _file_path = _file_path.replace('\x1e', '/')
        if _device == _client_device_name:
            try:
                remove(f"{expanduser('~/.config/sshyp/deleted/')}{_file}")
            except FileNotFoundError:
                pass
            open(expanduser('~/.config/sshyp/deletion_database'), 'a').write(_file_path + '\n')


def folder_check():  # creates a list of folders to be compared with those of a local machine
    open(expanduser('~/.config/sshyp/folder_database'), 'w').write('')
    for _root, _directories, _files in walk(expanduser('~/.local/share/sshyp')):
        for _dir in _directories:
            open(expanduser('~/.config/sshyp/folder_database'), 'a')\
                .write(f"{_root.replace(expanduser('~'), '')}/{_dir}\n")
