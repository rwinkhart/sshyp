#!/usr/bin/python3

# external modules

from os import remove, listdir
from os.path import expanduser
from shutil import rmtree


# utility functions

def delete(_file_path):
    if _file_path.endswith('/'):
        try:
            rmtree(f"{expanduser('~/.password-pasture/')}{_file_path}")
        except FileNotFoundError:
            print('\nFolder does not exist remotely.')
    else:
        try:
            remove(f"{expanduser('~/.password-pasture/')}{_file_path}.gpg")
        except FileNotFoundError:
            print('\nFile does not exist remotely.\n')
    for _device_name in listdir(expanduser('~/.config/sshyp/devices')):
        open(f"{expanduser('~/.config/sshyp/deleted/')}{_file_path.replace('/', '@')}.{_device_name}.del", 'w')


def check(_client_device_name):
    open(expanduser('~/.config/sshyp/deletion_database'), 'w').write('')
    for _file in listdir(expanduser('~/.config/sshyp/deleted')):
        _file_path = _file.replace('.gpg', '').replace('@', '/').split('.')[0]
        _device = _file.replace('.gpg', '').split('.')[1]
        if _device == _client_device_name:
            try:
                remove(f"{expanduser('~/.config/sshyp/deleted/')}{_file}")
            except FileNotFoundError:
                pass
            open(expanduser('~/.config/sshyp/deletion_database'), 'a').write(_file_path + '.gpg\n')