import os
import sys

from wabbajack import extract_mod_data

if len(sys.argv) == 1:
    (_, _, fnames) = next(os.walk("."))
    fnames = [x for x in fnames if x.endswith(".wabbajack")]
else:
    fnames = sys.argv[1:]

for fname in fnames:
    print("dumping modlist for", fname)
    extract_mod_data(fname)
