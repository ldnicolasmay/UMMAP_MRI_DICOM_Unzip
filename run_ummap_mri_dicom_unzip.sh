echo $(date)

python3 ummap_mri_dicom_unzip.py                     \
  --mri_path /nfs/psych-bhampstelab/RAW_nopreprocess \
  --subfolder_regex "^(hlp|bmh)17umm\d{5}_\d{5}$"    \
  --verbose

echo $(date)

