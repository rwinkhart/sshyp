#!/usr/bin/env python3
from curses import curs_set, newwin, A_REVERSE, KEY_UP, KEY_DOWN, noecho, nocbreak, endwin, initscr, cbreak
from curses.textpad import rectangle, Textbox
from os import environ, listdir, remove, symlink
from pathlib import Path
from random import randint
from re import sub
from shutil import get_terminal_size, which
from sshync import make_profile
from sshyp import copy_id_check, string_gen
from subprocess import run, PIPE
# PORT START UNAME-IMPORT
from os import uname
from os.path import exists, expanduser, isfile
# PORT END UNAME-IMPORT
home = expanduser("~")
sshyp_data = []


# creates a radio selection between the provided options
def settings_radio(_stdscr, _options, _pretext):
    curs_set(0)
    _selected = 0
    while True:
        _stdscr.clear()
        _stdscr.addstr(0, 0, _pretext)
        for _i, _option in enumerate(_options):
            _y = _i + 2
            if _i == _selected:
                _stdscr.addstr(_y, 0, "[*] " + _option, A_REVERSE)
            else:
                _stdscr.addstr(_y, 0, "[ ] " + _option)
        _stdscr.refresh()
        _key = _stdscr.getch()
        # update _selected based on user input
        if _key == KEY_UP:
            _selected = (_selected - 1) % len(_options)
        elif _key == KEY_DOWN:
            _selected = (_selected + 1) % len(_options)
        elif _key == ord('\n'):
            break
        _stdscr.refresh()
    curs_set(1)
    return _selected


# creates a text-box input
def settings_text(_stdscr, _pretext):
    _stdscr.clear()
    _stdscr.addstr(0, 0, _pretext)
    _term_columns = get_terminal_size()[0]
    _editwin = newwin(1, _term_columns - 2, 3, 1)
    rectangle(_stdscr, 2, 0, 4, _term_columns - 1)
    _stdscr.refresh()
    _box = Textbox(_editwin)
    # let the user edit until ctrl+g/enter is struck
    _box.edit()
    # return resulting contents
    return _box.gather().strip()


# cleanly exit curses
def settings_terminate(_stdscr):
    nocbreak()
    _stdscr.keypad(False)  # TODO Needed??
    noecho()
    endwin()


# device+sync type selection
def install_type(_stdscr):
    _offline_mode = False
    # PORT START TWEAK-DEVTYPE
    _install_type = settings_radio(_stdscr, ('server', 'client (ssh-synchronized)', 'client (offline)'),
                                   'device + sync type configuration')
    if _install_type == 0:
        _dev_type = 'server'
        Path(f"{home}/.config/sshyp/deleted").mkdir(mode=0o700, exist_ok=True)
        Path(f"{home}/.config/sshyp/whitelist").mkdir(mode=0o700, exist_ok=True)
        settings_terminate(_stdscr)
        print(f"\nmake sure the ssh service is running and properly configured")
    else:
        _dev_type = 'client'
        if _install_type == 2:
            _offline_mode = True
        Path(f"{home}/.local/share/sshyp").mkdir(mode=0o700, parents=True, exist_ok=True)
    # PORT END TWEAK-DEVTYPE
    return _dev_type, _offline_mode


# gpg configuration
def gpg_config(_stdscr):
    # gpg key selection
    _uid_list = [_item for _item in run(['gpg', '-k', '--with-colons'],
                                        stdout=PIPE, text=True).stdout.splitlines() if _item.startswith('uid')]
    _clean_uid_list = []
    for _uid in _uid_list:
        _clean_uid_list.append(sub(r':+', ':', _uid).split(':')[4])
    _clean_uid_list.append('auto-generate')
    _gpg_id_sel = settings_radio(_stdscr, _clean_uid_list, 'gpg key selection')
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
    return _gpg_id


# text editor configuration
def editor_config(_stdscr):
    _editor = settings_text(_stdscr, 'enter the name of your preferred text editor:\n\n\n\n\n'
                                     '(ctrl+g/enter to confirm)\n\nexample input: vim')
    return _editor


# ssh+sshync configuration
def ssh_config(_stdscr):
    # ssh+sshync configuration
    _uiport = settings_text(_stdscr, 'enter the username, ip, and ssh port of your sshyp server:\n\n\n\n\n('
                                     'ctrl+g/enter to confirm)\n\nexample inputs:\n\n ipv4: user@10.10.10.'
                                     '10:22\n ipv6: user@[2000:2000:2000:2000:2000:2000:2000:2000]:22\n '
                                     'domain: user@mydomain.com:22').lstrip('[').replace(']', '')
    _uiport_split = _uiport.split('@')
    _username_ssh = _uiport_split[0]
    _iport = _uiport_split[1].rsplit(':', 1)

    # sshync profile generation
    make_profile(f"{home}/.config/sshyp/sshyp.sshync",
                 f"{home}/.local/share/sshyp/", f"/home/{_username_ssh}/.local/share/sshyp/",
                 f"{home}/.ssh/sshyp", _iport[0], _iport[1], _username_ssh)
    return _iport[1], _username_ssh, _iport[0]


# device id configuration
def dev_id_config(_stdscr):
    for _id in listdir(f"{home}/.config/sshyp/devices"):
        remove(f"{home}/.config/sshyp/devices/{_id}")
    _device_id_prefix = settings_text(_stdscr, 'name this device:\n\n\n\n\n(ctrl+g/enter to confirm)\n\n'
                                               'important:\u001b[0m this id \u001b[4;1mmust\u001b[0m be '
                                               'unique amongst your client devices\n\nthis is used to keep '
                                               'track of database syncing and quick-unlock permissions\n')
    _device_id_suffix = string_gen('f', randint(24, 48))
    _device_id = _device_id_prefix + '-' + _device_id_suffix
    open(f"{home}/.config/sshyp/devices/{_device_id}", 'w')
    return _device_id


# quick-unlock configuration
def quick_unlock_config(_stdscr):
    _quick_unlock_sel = settings_radio(_stdscr, ('yes', 'no'), 'enable quick-unlock?')
    if _quick_unlock_sel == 0:
        _enabled = 'yes'
    else:
        _enabled = 'no'
    return _enabled


# runs initial configuration wizard
def initial_setup():
    # config directory creation
    Path(f"{home}/.config/sshyp/devices").mkdir(mode=0o700, parents=True, exist_ok=True)

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
    _stdscr = initscr()
    noecho()
    cbreak()
    _stdscr.keypad(True)

    # curses menu tree
    try:
        # device+sync type selection
        _dev_sync_types = install_type(_stdscr)
        sshyp_data.append(_dev_sync_types[0])

        if _dev_sync_types[0] == 'client':

            # gpg configuration
            sshyp_data.append(gpg_config(_stdscr))

            # lock file generation (requires gpg configuration)
            if isfile(f"{home}/.config/sshyp/lock.gpg"):
                remove(f"{home}/.config/sshyp/lock.gpg")
                open(f"{home}/.config/sshyp/lock", 'w')
                run(['gpg', '-qr', str(sshyp_data[1]), '-e', f"{home}/.config/sshyp/lock"])
                remove(f"{home}/.config/sshyp/lock")

            # text editor configuration
            sshyp_data.append(editor_config(_stdscr))

            # online (synchronized mode) configuration
            if not _dev_sync_types[1]:

                # ssh+sshync configuration
                _ip, _username_ssh, _port = ssh_config(_stdscr)

                # device id configuration
                _device_id = dev_id_config(_stdscr)

                # quick-unlock configuration
                sshyp_data.append(quick_unlock_config(_stdscr))

                # cleanly exit curses
                settings_terminate(_stdscr)

                # test server connection and attempt to register device id
                copy_id_check(_ip, _username_ssh, _port, _device_id)

            else:
                if isfile(f"{home}/.config/sshyp/sshyp.sshync"):
                    remove(f"{home}/.config/sshyp/sshyp.sshync")
                # cleanly exit curses
                settings_terminate(_stdscr)

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

    except KeyboardInterrupt:
        # cleanly exit curses
        settings_terminate(_stdscr)

    # write main config file (sshyp-data)
    with open(f"{home}/.config/sshyp/sshyp-data", 'w') as _config_file:
        _lines = 0
        for _item in sshyp_data:
            _lines += 1
            _config_file.write(str(_item) + '\n')
        while _lines < 4:
            _lines += 1
            _config_file.write('n')
    print('\nconfiguration complete\n')


# runs secondary configuration menu
def global_menu(_post_setup):
    # curses initialization
    _stdscr = initscr()
    noecho()
    cbreak()
    _stdscr.keypad(True)

    # a client device is assumed, the server should never show this menu
    _options = []
    if not _post_setup:
        _options = ['change device/synchronization types', 'change gpg key', 're-configure ssh', 'change device name']
        _message = 'all configuration options'
    _options.extend(['[OPTIONAL, RECOMMENDED] set custom text editor',
                     '[OPTIONAL, RECOMMENDED] enable/disable quick-unlock',
                     '[OPTIONAL, NOT IMPLEMENTED] su security mode',
                     '[OPTIONAL, NOT IMPLEMENTED] extensions and updates', 'exit'])
    _message = 'additional configuration options'

    _choice = settings_radio(_stdscr, _options, _message)
