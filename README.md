# UMMAP MRI DICOM Unzip

This script unzips the `dicom.tgz` files one level beneath a target directory defined by the user. This is intended to be run as a local script on Michigan Alzheimer's Disease Center's `madcbrain` server.

A firm grasp of regular expressions is required to use this app effectively. ([RegexOne](https://regexone.com/) offers a good tutorial on regular expressions.)

_**Regex patterns passed as command-line option arguments should be quoted!**_ See [example run](https://gitlab.com/ldnicolasmay/UMMAP_MRI_DICOM_Unzip/-/tree/master#example-run) or [example run with logging](https://gitlab.com/ldnicolasmay/UMMAP_MRI_DICOM_Unzip/-/tree/master#example-run-with-logging) below.

The directory tree structure is assumed to be this:

```
[mri_path]
  ├──[participant-session-dir-1]
  │    ├──dicom.tgz
  │    └──...
  ├──[participant-session-dir-2]
  │    ├──dicom.tgz
  │    └──...
  └──...
```

## Using the App

Ensure that you have Python 3.6 or higher installed and active in your virtual environment.

To run the app from a Bash command line, you need to know two pieces of information to pass as arguments or options+arguments:

1. `--mri_path` (`-m`) option argument: Path of parent directory that holds all DICOM participant-session subdirectories.
2. `--subfolder_regex` (`-r`) option argument: Regex pattern for the participant-session subdirectory name(s) that contain the `dicom.tgz` file, a zipped tarball of directories with DICOM files.

There is also an option for printing output:

1. `--verbose` option (`-v`): Prints filepath of the `dicom.tgz` being unzipped; handy for simple logging.

### Command Line Help

To see the command line help from a Bash prompt, run:

```
python3 /path/to/ummap_mri_dicom_unzip.py --help
```

### Canonical Run

Here's an example of a canonical run from a Bash prompt:

```
python3 ummap_mri_dicom_unzip.py    \
  --mri_path        MRI_PATH        \
  --subfolder_regex SUBFOLDER_REGEX
```

### Example Run

Here's an example of a verbose run from a Bash prompt:

```
python3 ummap_mri_dicom_unzip.py                     \
  --mri_path /nfs/psych-bhampstelab/RAW_nopreprocess \
  --subfolder_regex "^(hlp|bmh)17umm\d{5}_\d{5}$"    \
  --verbose
```

### Example Run with Logging

Logging can be done with Bash redirect operator `>`:

```
python3 ummap_mri_dicom_unzip.py                     \
  --mri_path /nfs/psych-bhampstelab/RAW_nopreprocess \
  --subfolder_regex "^(hlp|bmh)17umm\d{5}_\d{5}$"    \
  --verbose                                          \
  1>log/$(date +"%Y-%m-%d_%H-%M-%S").log             \
  2>err/$(date +"%Y-%m-%d_%H-%M-%S").log
```
