#!/usr/bin/python

# rpass 2021.09.08.pr4
# rpass is the gnu pass alternative for those who don't want to use git
# rpass is freely licensed for modification and redistribution under the GNU General Public License V3

from os import system
from os import remove
from os import environ
from shutil import move
from shutil import rmtree
from sys import argv
import random
import string


def clear():
    print("\n" * 100)


def term(cmd):
    _ = system(cmd)


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def encrypt():
    term('gpg -r ' + str(gpgid) + ' -e ' + "'" + '/dev/shm/' + shmfolder + '/' + shmentry + "'")
    move('/dev/shm/' + shmfolder + '/' + shmentry + '.gpg', directory + entryname.replace('/', '', 1) + '.gpg')
    rmtree('/dev/shm/' + shmfolder)


def encryptfolder():
    term('gpg -r ' + str(gpgid) + ' -e ' + "'" + '/dev/shm/' + shmfolder + '/' + shmentry + "'")
    move('/dev/shm/' + shmfolder + '/' + shmentry + '.gpg', directory + folder + '/' + folderentry + '.gpg')
    rmtree('/dev/shm/' + shmfolder)


def rsyncup():
    term(rsyncupp + ' ' + directory + ' ' + usernamessh + '@' + ip + ':' + directoryssh)


def rsyncdown():
    term(rsyncdownn + ' ' + usernamessh + '@' + ip + ':' + directoryssh + ' ' + directory)


# argument - filter the argument to usable text - some replacements are only done once to prevent interference

argument = str(argv).replace('[', '', 1).replace(']', '', 1).replace(',', '').replace("'", '') \
    .replace(' ', '', 1).replace('/usr/bin/', '', 1).replace('rpass', '', 1).replace('./', '', 1).replace('.py', '', 1)

# startup help

if argument == '':
    clear()
    print("use 'help', '--help', or '-h' to see a list of commands")
    print()
    print('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>')
    print("If you are receiving errors, run 'rpass config' and go through the guided setup wizard.")
    print('This MUST be done before rpass will function!!')
    print('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>')
    print()
    print('rpass is currently early software with very little polish')
    print()

# help

if argument == 'help' or argument == '--help' or argument == '-h':
    print()
    print('rpass  Copyright (C) 2021  Randall Winkhart')
    print("This program comes with ABSOLUTELY NO WARRANTY; for details type `rpass show w'. This is free software, "
          "and you are welcome to redistribute it under certain conditions; type `rpass show c' for details.")
    print()
    print('USAGE: rpass [/<entry name>] [OPTION] [FLAG]')
    print()
    print('Options: ')
    print('help/--help/-h           bring up this menu')
    print('version/-v               display rpass version info')
    print('config                   configure rpass')
    print('add                      add an entry')
    print('gen                      generate a new password')
    print('edit                     edit an existing entry')
    print('remove/-rm               delete an existing entry')
    print('sync/-s                  manually sync the entry directory via rsync')
    print()
    print('Flags:')
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
    print('gen:')
    print(' update/-u               generate a password for an existing entry')
    print()
    print("Tip: You can quickly read an entry with 'rpass /<entry name>'!")
    print("When specifying entry names, do not include the file extension! '.gpg' is assumed!")
    print()

# version info

if argument == 'version' or argument == '-v':
    print()
    print('////////////////////////////////////////////////////////')
    print('/                                                      /')
    print('/     rpass  Copyright (C) 2021  Randall Winkhart      /')
    print('/                                                      /')
    print('/               version 2021.09.08.pr4                 /')
    print('/                                                      /')
    print('////////////////////////////////////////////////////////')
    print()

# licensing info

if argument == 'show w':
    clear()
    print('This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;')
    print('without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.')
    print('See the GNU General Public License for more details.')
    print()
    print('https://opensource.org/licenses/GPL-3.0')
    print()

if argument == 'show c':
    clear()
    print('This program is free software: you can redistribute it and/or modify it under the terms of the GNU General')
    print('Public License as published by the Free Software Foundation, either version 3 of the License,')
    print('or (at your option) any later version.')
    print()

# config

if argument == 'config':
    print()
    directorychoice = str(input('Would you like to use the default entry directory (~/.rpass-store/)? (Y/n) '))
    if directorychoice != 'n':
        with open("/var/lib/rpass/rpassdir", 'w') as f:
            f.write('/home/' + environ.get('USER') + '/.rpass-store/' + '\n')
    if directorychoice == 'n':
        print()
        print('Format: /this/path/ends/with/a/slash/')
        print()
        directory = str(input('Please input a custom directory: '))
        with open("/var/lib/rpass/rpassdir", 'w') as f:
            f.write(directory + '\n')
    print()
    gpgpresent = str(input('rpass requires the use of a unique gpg key. Do you already have one you are willing to '
                           'use? (y/N) '))
    if gpgpresent == 'y' or gpgpresent == 'Y':
        print()
        gpgid = str(input('Please input the ID of your gpg key: '))
        with open("/var/lib/rpass/rpassgpg", 'w') as f:
            f.write(gpgid + '\n')
    if gpgpresent != 'y':
        print()
        gpggen = str(input('Would you like to generate one now? Note that if you choose not to do this, you will have '
                           'to re-run "rpass config" to specify a gpg key when you acquire one (Y/n) '))
        if gpggen != 'n':
            term('gpg --full-generate-key')
            print()
            gpgid = str(input('Please input the ID of your gpg key: '))
            with open("/var/lib/rpass/rpassgpg", 'w') as f:
                f.write(gpgid + '\n')
        if gpggen == 'n' or gpggen == 'N':
            exit()
    print()
    syncsetup = str(input('Would you like to configure rsync over ssh for entry backup and syncing? (Y/n) '))
    if syncsetup != 'n':
        print()
        sshgen = str(input('rsync support requires a unique ssh key. Would you like to have this '
                           'automatically generated? (Y/n) '))
        if sshgen != 'n':
            term('ssh-keygen -f ~/.ssh/rpass')
        print()
        print('The server device(s) should be configured first.')
        print()
        devicetype = str(input('Will this be a client or a server device? (c/S) '))
        if devicetype != 'c':
            print()
            print('Make sure the ssh service is running and that the proper port is forwarded.')
        if devicetype == 'c':
            print()
            print('Make sure the ssh service is running and that the proper port is forwarded on the remote server.')
            print('Example input: 10.10.10.10:9999')
            print()
            ip_port = str(input('What is the IP and ssh port of the remote server? '))
            print()
            usernamessh = str(input('What is the username of the remote server? '))
            ip, sep, port = ip_port.partition(':')
            with open("/var/lib/rpass/rpassuserssh", 'w') as f:
                f.write(usernamessh + '\n')
            with open("/var/lib/rpass/rpassrsyncup", 'w') as f:
                f.write('rsync -v -H -r -l -t -p -e ' + '"ssh -i ~/.ssh/rpass -p ' + port + '" ' + '\n')
            with open("/var/lib/rpass/rpassrsyncdown", 'w') as f:
                f.write('rsync -v -H -r -l -t -p --delete -e ' + '"ssh -i ~/.ssh/rpass -p ' + port + '" ' + '\n')
            with open("/var/lib/rpass/rpassip", 'w') as f:
                f.write(ip + '\n')
            print()
            print('Default directory: ' + '/home/' + usernamessh + '/.rpass-store/')
            print()
            directoryssh = str(input('Is the remote server using the default password directory? (Y/n) '))
            if directoryssh != 'n':
                directoryssh = ('/home/' + usernamessh + '/.rpass-store/')
            if directoryssh == 'n' or directoryssh == 'N':
                print()
                print('Format: /this/path/ends/with/a/slash/')
                print()
                directoryssh = str(input('What directory is the server using?: '))
            with open("/var/lib/rpass/rpassdirssh", 'w') as f:
                f.write(directoryssh + '\n')

# import userdata

with open("/var/lib/rpass/rpassgpg") as f:
    gpgid = f.read().strip()
with open("/var/lib/rpass/rpassdir") as f:
    directory = f.read().strip()
term('mkdir -p ' + directory)
with open("/var/lib/rpass/rpassdirssh") as f:
    directoryssh = f.read().strip()
with open("/var/lib/rpass/rpassrsyncup") as f:
    rsyncupp = f.read().strip()
with open("/var/lib/rpass/rpassrsyncdown") as f:
    rsyncdownn = f.read().strip()
with open("/var/lib/rpass/rpassip") as f:
    ip = f.read().strip()
with open("/var/lib/rpass/rpassuserssh") as f:
    usernamessh = f.read().strip()

if argument == '':
    print()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    readentry = str(input('Entry to read: '))
    clear()
    term('gpg -d ' + directory + "'" + readentry.replace('/', '', 1) + "'" + '.gpg')
    print()

# read shortcut

if argument.startswith('/'):
    if argument.replace('/', '', 1).__contains__('/'):
        folder, sep, folderentry = argument.replace('/', '', 1).partition('/')
        term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
    else:
        term('gpg -d ' + directory + "'" + argument.replace('/', '', 1) + '.gpg' + "'")

# add

if argument == 'add':
    print()
    print('USAGE: rpass add [FLAG]')
    print('Flags:')
    print('add:')
    print(' password/-p             add a password entry')
    print(' note/-n                 add a note entry')
    print(' folder/-f               add a new folder for entries')
    print()

if argument == 'add note' or argument == 'add -n':
    clear()
    entryname = str(input('Name of note: '))
    notes = str(input('Contents of note: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
                f.writelines('\n\n\n' + notes + '\n\n')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
                f.writelines('\n\n\n' + notes + '\n\n')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
            f.writelines('\n\n\n' + notes + '\n\n')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

if argument == 'add password' or argument == 'add -p':
    clear()
    entryname = str(input('Name of service: '))
    username = str(input('Username: '))
    password = str(input('Password: '))
    url = str(input('URL: '))
    notes = str(input('Additional notes: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
                f.writelines(username + '\n' + password + '\n' + url + '\n' + notes + '\n\n')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
                f.writelines(username + '\n' + password + '\n' + url + '\n' + notes + '\n\n')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
            f.writelines(username + '\n' + password + '\n' + url + '\n' + notes + '\n\n')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

if argument == 'add folder' or argument == 'add -f':
    newfolder = str(input('Name of new folder: '))
    term('mkdir ' + "'" + directory + newfolder + "'")

# edit

if argument == 'edit':
    print()
    print('USAGE: rpass edit [FLAG]')
    print('Flags:')
    print('edit:')
    print(' rename/relocate/-r      rename or relocate an entry')
    print(' username/-u             change the username of an entry')
    print(' password/-p             change the password of an entry')
    print(' note/-n                 change the note attached to an entry')
    print(' url/-l                  change the url attached to an entry')
    print()

if argument == 'edit rename' or argument == 'edit relocate' or argument == 'edit -r':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('What file would you like to edit? '))
    newname = str(input('New Name: '))
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            move(directory + folder + '/' + folderentry + '.gpg', directory + '/' + newname + '.gpg')
        else:
            move(directory + entryname.replace('/', '', 1) + '.gpg', directory + newname.replace('/', '', 1) + '.gpg')
    else:
        move(directory + entryname + '.gpg', directory + newname + '.gpg')

if argument == 'edit username' or argument == 'edit -u':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('What file would you like to edit? '))
    username = str(input('New Username: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 folder + '/' + folderentry + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 0, username + '\n')
            remove(directory + folder + '/' + folderentry + '.gpg')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 entryname.replace('/', '', 1) + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 0, username + '\n')
            remove(directory + entryname.replace('/', '', 1) + '.gpg')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory + entryname + '.gpg')
        replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 0, username + '\n')
        remove(directory + entryname + '.gpg')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

if argument == 'edit password' or argument == 'edit -p':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('What file would you like to edit? '))
    password = str(input('New Password: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 folder + '/' + folderentry + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 1, password + '\n')
            remove(directory + folder + '/' + folderentry + '.gpg')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 entryname.replace('/', '', 1) + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 1, password + '\n')
            remove(directory + entryname.replace('/', '', 1) + '.gpg')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory + entryname + '.gpg')
        replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 1, password + '\n')
        remove(directory + entryname + '.gpg')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

if argument == 'edit url' or argument == 'edit -l':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('What file would you like to edit? '))
    url = str(input('New URL: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 folder + '/' + folderentry + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 2, url + '\n')
            remove(directory + folder + '/' + folderentry + '.gpg')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 entryname.replace('/', '', 1) + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 2, url + '\n')
            remove(directory + entryname.replace('/', '', 1) + '.gpg')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory + entryname + '.gpg')
        replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 2, url + '\n')
        remove(directory + entryname + '.gpg')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

if argument == 'edit note' or argument == 'edit -n':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('What file would you like to edit? '))
    notes = str(input('New Note: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 folder + '/' + folderentry + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 3, notes + '\n')
            remove(directory + folder + '/' + folderentry + '.gpg')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 entryname.replace('/', '', 1) + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 3, notes + '\n')
            remove(directory + entryname.replace('/', '', 1) + '.gpg')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory + entryname + '.gpg')
        replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 3, notes + '\n')
        remove(directory + entryname + '.gpg')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

# gen

if argument == 'gen':
    clear()
    entryname = str(input('Name of service: '))
    username = str(input('Username: '))
    passlength = int(input('How many characters should be in the password? '))
    passtype = str(input('Should the password be simple (for compatibility) or complex (for security)? (s/C) '))
    if passtype != 's':
        passtype = string.ascii_letters + string.digits + string.punctuation
    if passtype == 's':
        passtype = string.ascii_letters + string.digits
    passgen = ''.join(random.SystemRandom().choice(passtype) for _ in range(passlength))
    url = str(input('URL: '))
    notes = str(input('Additional notes: '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
                f.writelines(username + '\n' + passgen + '\n' + url + '\n' + notes + '\n\n')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
                f.writelines(username + '\n' + passgen + '\n' + url + '\n' + notes + '\n\n')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        with open('/dev/shm/' + shmfolder + '/' + shmentry, 'w') as f:
            f.writelines(username + '\n' + passgen + '\n' + url + '\n' + notes + '\n\n')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

if argument == 'gen update' or argument == 'gen -u':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('Which password would you like to re-generate? '))
    passlength = int(input('How many characters should be in the password? '))
    passtype = str(input('Should the password be simple (for compatibility) or complex (for security)? (s/C) '))
    # generate random strings for /dev/shm
    shmfolder = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                        for _ in range(random.randint(10, 30)))
    shmentry = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                       for _ in range(random.randint(10, 30)))
    term('mkdir -p /dev/shm/' + shmfolder)
    # end string and folder generation
    if passtype != 's':
        passtype = string.ascii_letters + string.digits + string.punctuation
    if passtype == 's':
        passtype = string.ascii_letters + string.digits
    passgen = ''.join(random.SystemRandom().choice(passtype) for _ in range(passlength))
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            folder, sep, folderentry = entryname.replace('/', '', 1).partition('/')
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 folder + '/' + folderentry + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 1, passgen + '\n')
            remove(directory + folder + '/' + folderentry.replace('/', '', 1) + '.gpg')
            encryptfolder()
            term('gpg -d ' + directory + folder + '/' + "'" + folderentry + '.gpg' + "'")
        else:
            term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory +
                 entryname.replace('/', '', 1) + '.gpg')
            replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 1, passgen + '\n')
            remove(directory + entryname.replace('/', '', 1) + '.gpg')
            encrypt()
            term('gpg -d ' + directory + "'" + entryname.replace('/', '', 1) + '.gpg' + "'")
    else:
        term('gpg -d --output /dev/shm/' + shmfolder + '/' + shmentry + ' ' + directory + entryname + '.gpg')
        replace_line('/dev/shm/' + shmfolder + '/' + shmentry, 1, passgen + '\n')
        remove(directory + entryname + '.gpg')
        encrypt()
        term('gpg -d ' + directory + "'" + entryname + '.gpg' + "'")

# remove

if argument == 'remove' or argument == '-rm':
    clear()
    term('cd ~/.rpass-store; ls -1 *')
    print()
    entryname = str(input('What would you like to delete? '))
    if entryname.startswith('/'):
        if entryname.replace('/', '', 1).__contains__('/'):
            remove(directory + entryname.replace('/', '', 1) + '.gpg')
        else:
            rmtree(directory + entryname.replace('/', '', 1))
    else:
        remove(directory + entryname + '.gpg')

# permissions - applied pre-sync to ensure permissions are correct before upload

term('find ' + directory + ' -type d -exec chmod -R 700 {} +')
term('find ' + directory + ' -type f -exec chmod -R 600 {} +')

# rsync - ran at end of program to ensure all files are properly synced

if argument.__contains__('add') or argument.__contains__('-rm') or argument.__contains__('remove') or argument. \
        __contains__('edit') or argument.__contains__('gen') or argument == 'sync' or argument == '-s':
    rsyncup()
    rsyncdown()
    print()
    print('Please note that as of this time, entries can only be deleted if removed from the central server in a '
          'client-server scenario. This will be adjusted soon.')
    print()
