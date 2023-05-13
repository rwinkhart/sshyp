#!/usr/bin/env python3
from configparser import ConfigParser
from curses import A_REVERSE, echo, KEY_DOWN, KEY_UP, cbreak, curs_set, endwin, initscr, newwin, noecho, nocbreak
from curses.textpad import rectangle, Textbox
from os import environ, listdir, remove, symlink
from os.path import exists, expanduser, isfile
from pathlib import Path
from random import randint
from re import sub
from shutil import get_terminal_size, which
from sshyp import copy_id_check, string_gen
from subprocess import PIPE, run
# PORT START UNAME-IMPORT
from os import uname
# PORT END UNAME-IMPORT
home, stdscr, sshyp_data = expanduser("~"), initscr(), ConfigParser()
if isfile(f"{home}/.config/sshyp/sshyp.ini"):
    _exists_flag = True
    sshyp_data.read(f"{home}/.config/sshyp/sshyp.ini")
else:
    _exists_flag = False


# writes data stored in ConfigParser to the correct config file
def write_config(_sshyp_data=sshyp_data):
    with open(f"{home}/.config/sshyp/sshyp.ini", 'w') as configfile:
        _sshyp_data.write(configfile)


# creates a radio selection between the provided options
def curses_radio(_options, _pretext):
    curs_set(0)
    _selected = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, _pretext)
        for _i, _option in enumerate(_options):
            _y = _i + 2
            if _i == _selected:
                stdscr.addstr(_y, 0, "[*] " + _option, A_REVERSE)
            else:
                stdscr.addstr(_y, 0, "[ ] " + _option)
        stdscr.refresh()
        _key = stdscr.getch()
        # update _selected based on user input
        if _key == KEY_UP:
            _selected = (_selected - 1) % len(_options)
        elif _key == KEY_DOWN:
            _selected = (_selected + 1) % len(_options)
        elif _key == ord('\n'):
            break
        stdscr.refresh()
    curs_set(1)
    return _selected


# creates a text-box input
def curses_text(_pretext):
    stdscr.clear()
    stdscr.addstr(0, 0, _pretext)
    _term_columns = get_terminal_size()[0]
    _editwin = newwin(1, _term_columns - 2, 3, 1)
    rectangle(stdscr, 2, 0, 4, _term_columns - 1)
    stdscr.refresh()
    _box = Textbox(_editwin)
    # let the user edit until ctrl+g/enter is struck
    _box.edit()
    # return resulting contents
    return _box.gather().strip()


# cleanly exit curses and optionally prints an exit message
def curses_terminate(_term_message):
    nocbreak()
    echo()
    endwin()
    if _term_message:
        print(_term_message)


# device+sync type selection
def install_type():
    _offline_mode = 'false'
    # PORT START TWEAK-DEVTYPE
    _install_type = curses_radio(('server', 'client (ssh-synchronized)', 'client (offline)'),
                                 'device + sync type configuration')
    if _install_type == 0:
        _dev_type = 'server'
        Path(f"{home}/.config/sshyp/deleted").mkdir(mode=0o700, exist_ok=True)
        Path(f"{home}/.config/sshyp/whitelist").mkdir(mode=0o700, exist_ok=True)
        curses_terminate('\nmake sure the ssh service is running and properly configured\n')
    else:
        _dev_type = 'client'
        if _install_type == 2:
            _offline_mode = 'true'
        if not sshyp_data.has_section('CLIENT-GENERAL'):
            sshyp_data.add_section('CLIENT-GENERAL')
        sshyp_data.set('CLIENT-GENERAL', 'offline_mode_enabled', _offline_mode)
    if not sshyp_data.has_section('GENERAL'):
        sshyp_data.add_section('GENERAL')
    sshyp_data.set('GENERAL', 'device_type', _dev_type)
    write_config()
    # PORT END TWEAK-DEVTYPE
    return _dev_type, _offline_mode


# gpg configuration
def gpg_config():
    # gpg key selection
    _uid_list = [_item for _item in run(['gpg', '-k', '--with-colons'],
                                        stdout=PIPE, text=True).stdout.splitlines() if _item.startswith('uid')]
    _clean_uid_list = []
    for _uid in _uid_list:
        _clean_uid_list.append(sub(r':+', ':', _uid).split(':')[4])
    _clean_uid_list.append('auto-generate')
    _gpg_id_sel = curses_radio(_clean_uid_list, 'gpg key selection')
    _gpg_id = _clean_uid_list[_gpg_id_sel]
    if _gpg_id == 'auto-generate':
        print('\na unique gpg key is being generated for you...')
        if not isfile(f"{home}/.config/sshyp/gpg-gen"):
            open(f"{home}/.config/sshyp/gpg-gen", 'w').writelines([
                'Key-Type: 1\n', 'Key-Length: 4096\n', 'Key-Usage: sign encrypt\n', 'Name-Real: sshyp\n',
                'Name-Comment: gpg-sshyp\n', 'Name-Email: https://github.com/rwinkhart/sshyp\n',
                'Expire-Date: 0'])
        run(['gpg', '--batch', '--generate-key', f"{home}/.config/sshyp/gpg-gen"])
        remove(f"{home}/.config/sshyp/gpg-gen")
        _gpg_id = run(['gpg', '-k'], stdout=PIPE, text=True).stdout.splitlines()[-3].strip()

        # lock file generation
        if isfile(f"{home}/.config/sshyp/lock.gpg"):
            remove(f"{home}/.config/sshyp/lock.gpg")
            open(f"{home}/.config/sshyp/lock", 'w')
            run(['gpg', '-qr', _gpg_id, '-e', f"{home}/.config/sshyp/lock"])
            remove(f"{home}/.config/sshyp/lock")

    if not sshyp_data.has_section('CLIENT-GENERAL'):
        sshyp_data.add_section('CLIENT-GENERAL')
    sshyp_data.set('CLIENT-GENERAL', 'gpg_id', _gpg_id)
    write_config()


# text editor configuration
def editor_config(_env_mode):
    if _env_mode:
        # set default text editor to value of EDITOR environment variable, otherwise default to nano
        if 'EDITOR' in environ:
            _editor = environ['EDITOR']
        else:
            _editor = 'nano'
    else:
        _editor = curses_text('enter the name of your preferred text editor:\n\n\n\n\n'
                              '(ctrl+g/enter to confirm)\n\nexample input: vim')
    if not sshyp_data.has_section('CLIENT-GENERAL'):
        sshyp_data.add_section('CLIENT-GENERAL')
    sshyp_data.set('CLIENT-GENERAL', 'text_editor', _editor)
    write_config()


# ssh+sshync configuration
def ssh_config():
    # ssh+sshync configuration
    _uiport = curses_text('enter the username, ip, and ssh port of your sshyp server:\n\n\n\n\n('
                          'ctrl+g/enter to confirm)\n\nexample inputs:\n\n ipv4: user@10.10.10.'
                          '10:22\n ipv6: user@[2000:2000:2000:2000:2000:2000:2000:2000]:22\n '
                          'domain: user@mydomain.com:22').lstrip('[').replace(']', '')
    _uiport_split = _uiport.split('@')
    _username_ssh = _uiport_split[0]
    _iport = _uiport_split[1].rsplit(':', 1)

    if not sshyp_data.has_section('SSHYNC'):
        sshyp_data.add_section('SSHYNC')
    sshyp_data.set('SSHYNC', 'user', _username_ssh)
    sshyp_data.set('SSHYNC', 'ip', _iport[0])
    sshyp_data.set('SSHYNC', 'port', _iport[1])
    sshyp_data.set('SSHYNC', 'local_dir', f"{home}/.local/share/sshyp/")
    sshyp_data.set('SSHYNC', 'remote_dir', f"/home/{_username_ssh}/.local/share/sshyp/")
    sshyp_data.set('SSHYNC', 'identity_file', f"{home}/.ssh/sshyp")
    write_config()
    return _iport[1], _username_ssh, _iport[0]


# device id configuration
def dev_id_config(_ip, _username_ssh, _port):
    for _id in listdir(f"{home}/.config/sshyp/devices"):
        remove(f"{home}/.config/sshyp/devices/{_id}")
    _device_id_prefix = curses_text('name this device:\n\n\n\n\n(ctrl+g/enter to confirm)\n\n'
                                    'important:\u001b[0m this id \u001b[4;1mmust\u001b[0m be '
                                    'unique amongst your client devices\n\nthis is used to keep '
                                    'track of database syncing and quick-unlock permissions\n')
    _device_id_suffix = string_gen('f', randint(24, 48))
    _device_id = _device_id_prefix + '-' + _device_id_suffix
    open(f"{home}/.config/sshyp/devices/{_device_id}", 'w')
    # test server connection and attempt to register device id
    copy_id_check(_ip, _username_ssh, _port, _device_id, sshyp_data)


# quick-unlock configuration
def quick_unlock_config(_default):
    if _default:
        _enabled = 'false'
    else:
        _quick_unlock_sel = curses_radio(('yes', 'no'), 'enable quick-unlock?')
        if _quick_unlock_sel == 0:
            _enabled = 'true'
        else:
            _enabled = 'false'
    if not sshyp_data.has_section('CLIENT-ONLINE'):
        sshyp_data.add_section('CLIENT-ONLINE')
    sshyp_data.set('CLIENT-ONLINE', 'quick_unlock_enabled', _enabled)
    write_config()


# runs secondary configuration menu
def global_menu(_post_setup):
    # curses initialization
    noecho()
    cbreak()
    stdscr.keypad(True)

    _options, _choice, _term_message = [], 4, False
    try:
        if not _post_setup:
            _options.extend(['change device/synchronization types', 'change gpg key', 're-configure ssh(ync)',
                             'change device name'])
            _message, _choice = 'all configuration options:', 0
        _options.extend(['[OPTIONAL, RECOMMENDED] set custom text editor',
                         '[OPTIONAL, RECOMMENDED] enable/disable quick-unlock',
                         '[OPTIONAL, NOT IMPLEMENTED] su security mode',
                         '[OPTIONAL, NOT IMPLEMENTED] extensions and updates', 'exit/done'])
        _message = 'required configuration complete - additional configuration options:'
        _choice += curses_radio(_options, _message)

        if _choice == 0:
            _dev_sync_types = install_type()
            # if not running in server or offline mode and a sshync config has not been made
            if _dev_sync_types[0] != 'server' and _dev_sync_types[1] != 'true' and not sshyp_data.has_section('SSHYNC'):
                _ip, _username_ssh, _port = ssh_config()
                # if no device id is set
                if not listdir(f"{home}/.config/sshyp/devices"):
                    dev_id_config(_ip, _username_ssh, _port)
        elif _choice == 1:
            gpg_config()
        elif _choice == 2:
            ssh_config()
        elif _choice == 3:
            dev_id_config(sshyp_data.get('SSHYNC', 'ip'), sshyp_data.get('SSHYNC', 'user'),
                          sshyp_data.get('SSHYNC', 'port'))
        elif _choice == 4:
            editor_config(False)
        elif _choice == 5:
            quick_unlock_config(False)
        else:
            pass
        curses_terminate(_term_message)
    except KeyboardInterrupt:
        curses_terminate(False)


# runs initial configuration wizard
def initial_setup():
    # required directory creation
    Path(f"{home}/.config/sshyp/devices").mkdir(mode=0o700, parents=True, exist_ok=True)
    Path(f"{home}/.local/share/sshyp").mkdir(mode=0o700, parents=True, exist_ok=True)

    # removal of old config files
    if _exists_flag:
        sshyp_data.clear()

    # temporary file symlink creation
    if not exists(f"{home}/.config/sshyp/tmp"):
        # PORT START UNAME-TMP
        if uname()[0] in ('Haiku', 'FreeBSD', 'Darwin'):
            symlink('/tmp', f"{home}/.config/sshyp/tmp")
        elif exists('/data/data/com.termux'):
            symlink('/data/data/com.termux/files/usr/tmp', f"{home}/.config/sshyp/tmp")
        else:
            symlink('/dev/shm', f"{home}/.config/sshyp/tmp")
        # PORT END UNAME-TMP

    # curses initialization
    noecho()
    cbreak()
    stdscr.keypad(True)

    # curses menu tree
    try:
        # device+sync type selection
        _dev_sync_types = install_type()

        if _dev_sync_types[0] == 'client':

            # gpg configuration
            gpg_config()

            # text editor configuration (automated)
            editor_config(True)

            # quick-unlock configuration (disabled by default)
            quick_unlock_config(True)

            # online (synchronized mode) configuration
            if _dev_sync_types[1] != 'true':

                # ssh+sshync configuration
                _ip, _username_ssh, _port = ssh_config()

                # device id configuration
                dev_id_config(_ip, _username_ssh, _port)

                # cleanly exit curses
                curses_terminate(False)

            else:
                # cleanly exit curses
                curses_terminate(False)

            # PORT START CLIPTOOL
            # check for clipboard tool and display warning if missing
            if uname()[0] in ('Linux', 'FreeBSD'):
                if 'WAYLAND_DISPLAY' in environ:
                    _display_server, _clipboard_tool, _clipboard_package = 'Wayland', 'wl-copy', 'wl-clipboard'
                else:
                    _display_server, _clipboard_tool, _clipboard_package = 'X11', 'xclip', 'xclip'
                if which(_clipboard_tool) is None:
                    print(f'\n\u001b[38;5;9mwarning: you are using {_display_server} and "{_clipboard_tool}" is not '
                          f'present - \ncopying entry fields will not function until '
                          f'"{_clipboard_package}" is installed\u001b[0m')
            # PORT END CLIPTOOL

        global_menu(True)

    except KeyboardInterrupt:
        # cleanly exit curses
        curses_terminate(False)
