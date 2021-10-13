#!/usr/bin/python3

# sshync 2021.10.12.unreleased1

# sshync is a wrapper around sftp that functions as a Python library alternative to scp
# openssh (on POSIX compliant Unix) is required

# sshync will always overwrite the older files with the newer files, regardless of all other conditions
#   ^the age is determined by the date and time of the last modification to the files

# syncing via sshync is always done recursively

# external modules

from os.path import getmtime
from subprocess import getoutput as term_output


# internal modules


def make_profile(profile_dir, local_dir, remote_dir, identity, ip, port, user):
    open(profile_dir, 'w').write(user + '\n' + ip + '\n' + port + '\n' + local_dir + '\n' + remote_dir + '\n' + identity
                                 + '\n\n\n')


def make_sentinel_profile(profile_dir, local_dir, remote_dir, identity, ip, port, user, local_sentinel, rem_sentinel):
    open(profile_dir, 'w').write(user + '\n' + ip + '\n' + port + '\n' + local_dir + '\n' + remote_dir + '\n' + identity
                                 + '\n' + local_sentinel + '\n' + rem_sentinel + '\n')


def get_profile(profile_dir):
    try:
        profile_data = open(profile_dir).readlines()
    except (FileNotFoundError, IndexError):
        profile_data = 0
    return profile_data


def run_profile(profile_dir):
    # import profile data
    profile_data = get_profile(profile_dir)
    user = profile_data[0].replace('\n', '')
    ip = profile_data[1].replace('\n', '')
    port = profile_data[2].replace('\n', '')
    local_dir = profile_data[3].replace('\n', '')
    remote_dir = profile_data[4].replace('\n', '')
    identity = profile_data[5].replace('\n', '')
    local_sentinel = profile_data[6].replace('\n', '')
    rem_sentinel = profile_data[7].replace('\n', '')
    # get file modification times
    if local_sentinel == '':
        local_modification_time = getmtime(local_dir)
        remote_modification_time = float(
            term_output("ssh -i " + "'" + identity + "'" + " -p " + port + " " + user + "@" +
                        ip + " \"python -c 'from os.path import getmtime; mod_time = "
                             "(getmtime(" + '\\"' + remote_dir + '\\"' + ")); print(mod_time);"
                                                                         "'" + "\""))
    else:
        local_modification_time = getmtime(local_sentinel)
        remote_modification_time = float(
            term_output("ssh -i " + "'" + identity + "'" + " -p " + port + " " + user + "@" +
                        ip + " \"python -c 'from os.path import getmtime; mod_time = "
                             "(getmtime(" + '\\"' + rem_sentinel + '\\"' + ")); print(mod_time);"
                                                                           "'" + "\""))
    # compare file modification times
    if local_modification_time > remote_modification_time:
        print('\nLocal is newer, uploading...\n')  # upload
    else:
        print('\nRemote is newer, downloading...\n')  # download
