## Requirements
- Python3
- Possibly `xxhash` at https://pypi.org/project/xxhash/ ? The hashing functionality could be commented out of `wabbajack.py` at the moment since it is not used in the scripts.

## Usage to Generate Popularity By Modlist Chart
- Place scripts into same directory as `.wabbajack` files.
- Run `python wabbajack_rename_by_version.py` to rename all the Wabbajack files to `<listname>_<listversion>.wabbajack`.
- Run `python wabbajack_dump_moddata.py` to generate each list's `.moddata.json` file.
- Run `python wabbajack_moddata_json_to_csv.py` to generate `uuids_modlists.csv`.

## Notes
- Not comprehensively ported to WJ 3.x
- `wabbajack_rename_by_version.py` seems to use incorrect version numbers at the moment but the workflow is otherwise correct.
