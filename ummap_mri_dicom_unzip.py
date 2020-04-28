#!/usr/bin/env python3

##################
# Import modules #

import argparse
import os
import re
import logging
import subprocess


###################################
# Helper Function for Arg Parsing #

def str2bool(val):
    if isinstance(val, bool):
        return val
    elif val.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


########
# Main #

def main():

    ##############
    # Parse Args #

    parser = argparse.ArgumentParser(description="Unzip DICOM tarballs on `madcbrain`.")

    parser.add_argument('-m', '--mri_path', required=True,
                        help=f"required: "
                             f"absolute path to directory containing source MRI folders")
    parser.add_argument('-s', '--subfolder_regex', required=True,
                        help=f"quoted regular expression strings to use for subfolder matches")
    parser.add_argument('-v', '--verbose',
                        type=str2bool, nargs='?', const=True, default=False,
                        help=f"print actions to stdout")

    args = parser.parse_args()

    ###########
    # Globals #

    mri_basedir = args.mri_path
    mri_dir_rgx = re.compile(r'^(hlp|bmh)17umm\d{5}_\d{5}$')
    if args.subfolder_regex:
        mri_dir_rgx = re.compile(args.subfolder_regex)
    dicom_rgx = re.compile(r'^dicom(\.tgz)?$')
    verbose = args.verbose

    # Get DirEntry objects for all files and directories in `mri_path`
    dir_entries = os.scandir(mri_basedir)

    # Filter `dir_entries` for only participant-session directories
    pt_dir_entries = [de for de in dir_entries if re.match(mri_dir_rgx, de.name) and de.is_dir()]

    # Build dict for participant-session directories (keys, DirEntry objects) and
    # sub-files/-directories matching `dicom.tgz` or `dicom` (values, lists of DirEntry objects)
    pt_sess_dir_entries_dict = {}
    for pde in pt_dir_entries:
        sess_dir_entries = [sde for sde in os.scandir(f"{mri_basedir}/{pde.name}") if re.match(dicom_rgx, sde.name)]
        pt_sess_dir_entries_dict[pde] = sess_dir_entries

    # Filter participant-session dir entries dict into 4 categories
    # | dicom.tgz | dicom |
    # +-----------+-------+
    # |     0     |   0   | => Throw warning
    # |     0     |   1   | => Ignore b/c already unzipped
    # |     1     |   0   | => Unzip tarballs
    # |     1     |   1   | => Ignore b/c already unzipped
    no_dicomtgz_no_dicom_dict = \
        {k: v for (k, v) in pt_sess_dir_entries_dict.items() if not v}
    no_dicomtgz_yes_dicom_dict = \
        {k: v for (k, v) in pt_sess_dir_entries_dict.items()
         if "dicom" in map(lambda de: de.name, v) and "dicom.tgz" not in map(lambda de: de.name, v)}
    yes_dicomtgz_no_dicom_dict = \
        {k: v for (k, v) in pt_sess_dir_entries_dict.items()
         if "dicom" not in map(lambda de: de.name, v) and "dicom.tgz" in map(lambda de: de.name, v)}
    yes_dicomtgz_yes_dicom_dict = \
        {k: v for (k, v) in pt_sess_dir_entries_dict.items()
         if "dicom" in map(lambda de: de.name, v) and "dicom.tgz" in map(lambda de: de.name, v)}

    # Combine `no_dicomtgz_yes_dicom_dict` and `yes_dicomtgz_yes_dicom_dict`
    yes_dicom_dict = no_dicomtgz_yes_dicom_dict
    yes_dicom_dict.update(yes_dicomtgz_yes_dicom_dict)

    # Throw warning if there are pt directories with no `dicom` and no `dicom.tgz`
    if no_dicomtgz_no_dicom_dict:
        logging.warning(f"MRI session directories without necessary DICOM tarball or directory:"
                        f"\n\t{no_dicomtgz_no_dicom_dict}")
        if verbose:
            print(f"Already unzipped: {len(yes_dicom_dict)}")
            print(f"To be unzipped:   {len(yes_dicomtgz_no_dicom_dict)}")

    # Unzip the tarballs where the `dicom.tgz` exists but `dicom` directories don't exist
    for pde, dicom_list in yes_dicomtgz_no_dicom_dict.items():
        if verbose:
            print(f"Decompressing {pde.path}/{dicom_list[0].name}")
        subprocess.run(["tar", "-C", f"{pde.path}", "-x", "-z", "-f", f"{pde.path}/{dicom_list[0].name}"])


if __name__ == "__main__":
    main()
