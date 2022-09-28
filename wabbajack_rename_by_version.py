import os
import sys
import json
import zipfile

from zipfile import ZipFile

print("Wabbajack to Meta v0.01")

if len(sys.argv) < 2:
    print("You must provide a filename.")
    print("usage: wabbajack_to_meta.exe [wabbajack_file(s)]")

for fname in sys.argv[1:]:
    if not os.path.exists(fname):
        print('The file "' + fname + "\" doesn't exist! Exiting.")
        sys.exit(1)

failure_occured = False

for fname in sys.argv[1:]:
    print("working on " + fname + "...")

    try:
        with ZipFile(fname, "r") as myzip:
            try:
                with myzip.open("modlist") as myfile:
                    mod_data = json.loads(myfile.read())
            except KeyError as e:
                print("could not pull metadata from the wabbajack file! skipping")
                failure_occured = True
                continue
    except zipfile.BadZipFile as e:
        print(fname + " is not a valid wabbajack file! skipping")
        failure_occured = True
        continue

    BLOCK_KEYS = ["$type", "Archives", "Directives"]
    stripped_data_keys = [x for x in mod_data.keys() if x not in BLOCK_KEYS]

    meta_data = {k: mod_data[k] for k in stripped_data_keys}
    modname = meta_data["Name"]
    modver = meta_data["Version"]

    basename = modname + "_" + modver
    meta_fname = modname + "_" + modver + ".meta.json"
    new_fname = basename + ".wabbajack"

    if os.path.exists(meta_fname) and os.path.exists(new_fname):
        print(
            "there already exists a wabbajack and meta file of this wabbajack properly named"
        )
        print("no rename will occur")
        meta_fname = ".wabbajack".join(fname.split(".wabbajack")[:-1]) + ".meta.json"

    with open(meta_fname, "w") as f:
        f.write(json.dumps(meta_data, indent=2))
    print("saved metadata to " + meta_fname)

    if fname == new_fname:
        print("this wabbajack file is already named correctly")
    elif os.path.exists(new_fname):
        print(
            "correctly named wabbajack file ("
            + new_fname
            + ") already exists! skipping wabbajack rename."
        )
    else:
        print("renaming " + fname + " to " + new_fname)
        os.rename(fname, new_fname)

input("Done! Please press any key.")

if failure_occured:
    sys.exit(1)
else:
    sys.exit()
