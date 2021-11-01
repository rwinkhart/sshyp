#!/usr/bin/python3

# Main Targets:
# TODO Make it so that when a new folder is created in sshyp, it is automatically created on the remote server
# TODO Replace references to rpass/sshyp directory with a changeable variable
# TODO Clean everything up and move sshync to a separate package
# TODO Add dry run support

# sshync 2021.11.01.unreleased3
# sshync was created to solve a problem with rpass/sshyp, and as such, sshync will be bundled with sshyp until it is
# polished enough for a standalone release

# sshync is a wrapper around sftp that allows easy remote directory synchronization via Python
# openssh (on POSIX compliant Unix) is required

# sshync will always overwrite the older files with the newer files, regardless of all other conditions
#   ^the age is determined by the date and time of the last modification to the files

# syncing via sshync is always done recursively

# external modules

from os import walk
from os import system as term
from os.path import getmtime
from os.path import join as path_join


# internal modules


# recursively scans a local directory for all files and saves file paths and mod times to lists
def get_file_paths_mod(directory, name_database, time_database):
    file_paths = []
    temp_mod_times = []
    mod_times = []
    for root, directories, files in walk(directory):
        for filename in files:
            filepath = path_join(root, filename)
            file_paths.append(filepath)
            temp_mod_times.append(str(getmtime(filepath)))
    for time in temp_mod_times:
        mod_times.append(round(float(time), 2))
    open(name_database, 'w').write(str(file_paths))
    open(time_database, 'w').write(str(mod_times))
    return file_paths, mod_times


# recursively scans a remote directory for all files and saves file paths and mod times to lists
def get_file_paths_mod_remote(profile_dir):
    # import profile data
    profile_data = get_profile(profile_dir)
    user = profile_data[0].replace('\n', '')
    ip = profile_data[1].replace('\n', '')
    port = profile_data[2].replace('\n', '')
    remote_dir = profile_data[4].replace('\n', '')
    identity = profile_data[5].replace('\n', '')
    term("ssh -i " + "'" + identity + "'" + " -p " + port + " " + user + "@" + ip + " \"python -c \'import sshync; "
                                                                                    "sshync.get_file_paths_mod(" +
         "\"'\"" + remote_dir + "/\"'\", " + "\"'\"/var/lib/rpass/sshyncdatabase_names\"'\", " +
         "\"'\"/var/lib/rpass/sshyncdatabase_times\"'\")\'\"")
    term(
        'sftp -P ' + port + ' ' + user + '@' + ip + ':/var/lib/rpass/sshyncdatabase_names ' +
        '/var/lib/rpass/sshyncdatabase_names')
    term(
        'sftp -P ' + port + ' ' + user + '@' + ip + ':/var/lib/rpass/sshyncdatabase_times ' +
        '/var/lib/rpass/sshyncdatabase_times')
    remote_mod_names = (open('/var/lib/rpass/sshyncdatabase_names').read()).replace('[', '').replace(']', '').replace(
        ' ', '').replace("'", '').split(',')
    remote_mod_times = (open('/var/lib/rpass/sshyncdatabase_times').read()).replace('[', '').replace(']', '').replace(
        ' ', '').replace("'", '').split(',')
    return remote_mod_names, remote_mod_times


# regular profiles check the mod time of every individual file in the directory, making them slow but versatile
def make_profile(profile_dir, local_dir, remote_dir, identity, ip, port, user):
    open(profile_dir, 'w').write(user + '\n' + ip + '\n' + port + '\n' + local_dir + '\n' + remote_dir + '\n' + identity
                                 + '\n')


# returns the settings for a specified profile
def get_profile(profile_dir):
    try:
        profile_data = open(profile_dir).readlines()
    except (FileNotFoundError, IndexError):
        profile_data = 0
    return profile_data


# sorts name lists so that local and remote are in the same order
def name_sort(local_names, remote_names):
    remote_names_new = []
    for ele in local_names:
        if ele in remote_names:
            remote_names_new.append(ele)
    for ele in remote_names:
        if ele not in remote_names_new:
            remote_names_new.append(ele)
    return remote_names_new


# sorts time lists to compensate for name list re-ordering
def time_sort(old_names, new_names, old_times):
    remote_mod_times_new = []
    new_pos = -1
    for title in new_names:
        new_pos += 1
        if title in old_names:
            old_pos = old_names.index(title)
            remote_mod_times_new.append(old_times[old_pos])
    return remote_mod_times_new


getter_loop_count = -1


def loop_getter(split_remote_dir):
    global getter_loop_count
    getter_loop_count += 1
    new_var = split_remote_dir[getter_loop_count] + '/'
    return new_var


def run_profile(profile_dir):
    # import profile data
    profile_data = get_profile(profile_dir)
    user = profile_data[0].replace('\n', '')
    ip = profile_data[1].replace('\n', '')
    port = profile_data[2].replace('\n', '')
    local_dir = profile_data[3].replace('\n', '')
    remote_dir = profile_data[4].replace('\n', '')
    identity = profile_data[5].replace('\n', '')
    # get file modification times
    local_mod_names, local_mod_times = get_file_paths_mod(local_dir + '/', '/var/lib/rpass/sshyncdatabase_names',
                                                          '/var/lib/rpass/sshyncdatabase_times')
    remote_mod_times = []
    remote_mod_names, remote_mod_times_temp = get_file_paths_mod_remote('/var/lib/rpass/rpass.sshync')
    for time in remote_mod_times_temp:  # remove quotes from remote_mod_times
        remote_mod_times.append(float(time))
    lmod_short = []
    rmod_short = []
    matching_names = []
    matching_times_local = []
    matching_times_remote = []
    for lmod in local_mod_names:
        lmod_short.append(lmod.replace(local_dir, ''))
    for rmod in remote_mod_names:
        rmod_short.append(rmod.replace(remote_dir, ''))
    rmod_short_old = rmod_short
    rmod_short = name_sort(lmod_short, rmod_short)
    remote_mod_times = time_sort(rmod_short_old, rmod_short, remote_mod_times)
    i = -1
    for lshort in lmod_short:
        i += 1
        if lshort in rmod_short:
            matching_names.append(lshort)
            matching_times_local.append(local_mod_times[i])
        else:
            print('Uploading ' + lshort)
            lshort_split = lshort.replace('/', '', 1).split('/')

            c = -1
            for _ in lshort_split:
                c += 1

            global getter_loop_count
            getter_loop_count = -1
            q = ''
            for _ in range(c):
                q += loop_getter(lshort_split)

            term('sftp -p -i ' + "'" + identity + "' " + '-P ' + port + ' ' + user + '@' + ip + ':' + remote_dir + q +
                 " <<< $'put " + local_dir + lshort.replace('/', '', 1) + "'")
    i = -1
    for rshort in rmod_short:
        i += 1
        if rshort in lmod_short:
            matching_times_remote.append(float(remote_mod_times[i]))
        else:
            print('Downloading ' + rshort)
            term('sftp -p -i ' + "'" + identity + "' " + '-P ' + port + ' ' + user + '@' + ip + ':' + remote_dir +
                 rshort.replace('/', '', 1) + ' ' + local_dir + rshort.replace('/', '', 1))
    i = -1
    for ltime in matching_times_local:
        i += 1
        ltime = int(ltime)
        if ltime == int(matching_times_remote[i]):
            print('Local ' + matching_names[i] + ' is up to date, not syncing.')
        elif ltime > int(matching_times_remote[i]):
            print('Local ' + matching_names[i] + ' is newer, uploading.')
            matching_names_split = matching_names[i].replace('/', '', 1).split('/')

            c = -1
            for _ in matching_names_split:
                c += 1

            getter_loop_count = -1
            q = ''
            for _ in range(c):
                q += loop_getter(matching_names_split)

            term('sftp -p -i ' + "'" + identity + "' " + '-P ' + port + ' ' + user + '@' + ip + ':' + remote_dir + q +
                 " <<< $'put " + local_dir + matching_names[i].replace('/', '', 1) + "'")

        elif ltime < int(matching_times_remote[i]):
            print('Local ' + matching_names[i] + ' is older, downloading.')
            term('sftp -p -i ' + "'" + identity + "' " + '-P ' + port + ' ' + user + '@' + ip + ':' + remote_dir +
                 matching_names[i].replace('/', '', 1) + ' ' + local_dir + matching_names[i].replace('/', '', 1))
