#!/usr/bin/env python3

##
# Import modules
##
import subprocess
import base64
import paramiko

##
# Globals
##

dir_home = '/Users/ldmay'
url_server = 'madcbrain.umms.med.umich.edu'
basedir_mri = '/nfs/psych-bhampstelab/RAW_nopreprocess'
rgx_mri_dir = '"^(hlp|bmh)17umm[0-9]{5}_[0-9]{5}$"'

##
# Establish SSH client for `madcbrain`
##

client = paramiko.SSHClient()
client.load_system_host_keys(filename=f'{dir_home}/.ssh/known_hosts')
client.connect(hostname=url_server)

stdin, stdout, stderr = \
    client.exec_command(f'ls {basedir_mri} | egrep {rgx_mri_dir}')

dirs_mri = [line.strip('\n') for line in stdout]

for dir_mri in dirs_mri:
    print(f'{basedir_mri}/{dir_mri}')

print(f'{basedir_mri}/{dirs_mri[0]}')

foo = {}
for dir_mri in dirs_mri:
    stdin, stdout, stderr = \
        client.exec_command(f'ls {basedir_mri}/{dir_mri} | egrep {"^dicom"}')
    bar = [line.strip('\n') for line in stdout]
    print(dir_mri, ": ", bar, sep="")
    foo[dir_mri] = bar

print(foo)
print(len(foo))

print({key: value for (key, value) in foo.items() if value == []})
print(len({key: value for (key, value) in foo.items() if value == []}))

print({key: value for (key, value) in foo.items() if value == ['dicom.tgz']})  # THIS ONE <<<
print(len({key: value for (key, value) in foo.items() if value == ['dicom.tgz']}))

print({key: value for (key, value) in foo.items() if value == ['dicom']})
print(len({key: value for (key, value) in foo.items() if value == ['dicom']}))

print({key: value for (key, value) in foo.items() if 'dicom.tgz' in value and 'dicom' in value})
print(len({key: value for (key, value) in foo.items() if 'dicom.tgz' in value and 'dicom' in value}))

client.close()

