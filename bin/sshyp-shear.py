#!/usr/bin/python3

# external modules

from os import remove, listdir
from os.path import expanduser


# utility functions

def delete(_file_path, _client_device_name):
    remove(f"{expanduser('~/.password-pasture/')}{_file_path}")
    for _device_name in listdir(expanduser('~/.config/sshyp/devices')):
        open(f"{expanduser('~/.config/sshyp/deleted/')}{_file_path}.{_device_name}.del", 'w')
    remove(f"{expanduser('~/.config/sshyp/deleted/')}{_file_path}.{_client_device_name}.del")
