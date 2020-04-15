#!/usr/bin/env python3

##
# Import modules
##
import sys
import traceback
import math
from colored import fg, attr
import paramiko


##
# Colors
##
grn = fg(2)
org = fg(214)
red = fg(1)
reset = attr('reset')

##
# Globals
##
home_dir = '/Users/ldmay'
server_url = 'madcbrain.umms.med.umich.edu'
mri_basedir = '/nfs/psych-bhampstelab/RAW_nopreprocess'
mri_dir_rgx = '"^(hlp|bmh)17umm[0-9]{5}_[0-9]{5}$"'

try:
    # Establish SSH client
    client = paramiko.SSHClient()
    client.load_system_host_keys(filename=f'{home_dir}/.ssh/known_hosts')
    client.connect(hostname=server_url)

    # Get targeted MRI session directories
    _, stdout, _ = \
        client.exec_command(f'ls {mri_basedir} | egrep {mri_dir_rgx}')

    # Listify stdout
    mri_dirs = [line.strip('\n') for line in stdout]
    len_mri_dirs = len(mri_dirs)

    mri_dirs_dicom_entries = {}
    mri_dirs_dicom_entries_processed = len(mri_dirs_dicom_entries)
    progress_bar_width = min(80, len_mri_dirs)
    new_perc_processed = math.floor(mri_dirs_dicom_entries_processed / len_mri_dirs * progress_bar_width)

    print('+', '-' * progress_bar_width, '+', sep='')
    print('|', end='')
    for mri_dir in mri_dirs:
        _, stdout, _ = client.exec_command(f'ls {mri_basedir}/{mri_dir} | egrep {"^dicom"}')
        dicom_entries_list = [line.strip('\n') for line in stdout]
        mri_dirs_dicom_entries[mri_dir] = dicom_entries_list
        mri_dirs_dicom_entries_processed = mri_dirs_dicom_entries_processed + 1
        old_perc_processed = new_perc_processed
        new_perc_processed = math.floor(mri_dirs_dicom_entries_processed / len_mri_dirs * progress_bar_width)
        if old_perc_processed < new_perc_processed:
            print('=', end='', flush=True)
    print('|')

    no_mri_dirs_dicom_entries = \
        {key: value for (key, value) in mri_dirs_dicom_entries.items() if value == []}

    unzipped_mri_dirs_dicom_entries = \
        {key: value for (key, value) in mri_dirs_dicom_entries.items() if 'dicom' in value}

    to_be_unzipped_mri_dirs_dicom_entries = \
        {key: value for (key, value) in mri_dirs_dicom_entries.items() if value == ['dicom.tgz']}

    len_unzipped_mri_dirs_dicom_entries = len(unzipped_mri_dirs_dicom_entries)
    len_to_be_unzipped_mri_dirs_dicom_entries = len(to_be_unzipped_mri_dirs_dicom_entries)
    len_no_mri_dirs_dicom_entries = len(no_mri_dirs_dicom_entries)
    len_mri_dirs_dicom_entries = len(mri_dirs_dicom_entries)

    all_entries_lens = [len_unzipped_mri_dirs_dicom_entries,
                        len_to_be_unzipped_mri_dirs_dicom_entries,
                        len_no_mri_dirs_dicom_entries,
                        len_mri_dirs_dicom_entries]

    def pad_len_entries(len_entry, all_entries, filler=' '):
        max_len = max([len(str(entry)) for entry in all_entries])
        len_diff = max_len - len(str(len_entry))
        return filler * len_diff + str(len_entry)

    assert sum(all_entries_lens[:-1]) == sum(all_entries_lens[-1:])

    print()
    print(f"{grn}MRI directories containing `dicom` (unzipped):    ",
          f"{pad_len_entries(len_unzipped_mri_dirs_dicom_entries, all_entries_lens)}{reset}")
    print(f"{org}MRI directories missing `dicom` (to be unzipped): ",
          f"{pad_len_entries(len_to_be_unzipped_mri_dirs_dicom_entries, all_entries_lens)}{reset}")
    print(f"{red}MRI directories missing `dicom.tgz` and `dicom`:  ",
          f"{pad_len_entries(len_no_mri_dirs_dicom_entries, all_entries_lens)}{reset}")
    print("                                                  ",
          f"{pad_len_entries('', all_entries_lens, filler='-')}")
    print(f"MRI directories total:                             "
          f"{pad_len_entries(len_mri_dirs_dicom_entries, all_entries_lens)}")
    print()

    client.close()

except Exception as e:
    print("*** Caught exception: %s: %s" % (e.__class__, e))
    traceback.print_exc()
    try:
        client.close()
    except:
        pass
    sys.exit(1)
