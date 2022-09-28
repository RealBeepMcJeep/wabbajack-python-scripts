import os
import sys
import json
import base64
import random

from zipfile import ZipFile

import xxhash

HASH_CACHE = "hashcache.sqlite"

# hash notes:
# mod_data.json -> "Hash" attribute is something like "bhiVn/Ul3Zs="
# if we base64 decode this to binary and further into hex, we get
# > let wj_hash = 'bhiVn/Ul3Zs='
# > let buffer = Buffer.from(wj_hash, 'base64')
# > console.log(buffer.toString('hex'))
# 6e18959ff525dd9b
# using the cli:
# D:\Wabbajack>"D:\Wabbajack\2.5.3.4\wabbajack-cli.exe" hash-file -i "D:\Wabbajack\downloads\BethINI Standalone Version-4875-3-5-1593829244.zip"
# D:\Wabbajack\downloads\BethINI Standalone Version-4875-3-5-1593829244.zip hash: bhiVn/Ul3Zs= 6e18959ff525dd9b -7215569291103102866


def pprint_json(_json):
    return json.dumps(_json, indent=True, sort_keys=True)


def get_mod_data(fname):
    with ZipFile(fname, "r") as myzip:
        with myzip.open("modlist") as myfile:
            mod_data = json.loads(myfile.read())
    return mod_data


def extract_mod_data(fname):
    mod_data_fname = ".".join(fname.split(".")[0:-1]) + ".moddata.json"
    data = get_mod_data(fname)
    pprint_data = pprint_json(data)
    with open(mod_data_fname, "w") as f:
        f.write(pprint_data)


def get_file_xxhash(fname):
    x = xxhash.xxh64(seed=0)

    with open(fname, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            x.update(data)

    return x.hexdigest()


def get_file_wabbajack_hash(fname):
    xxh64_hash = get_file_xxhash(fname)
    hash_reversed = xxh64_hash[::-1]
    hash_chunked_reversed = "".join(
        [hash_reversed[i : i + 2][::-1] for i in range(0, len(hash_reversed), 2)]
    )
    return hash_chunked_reversed


def b64_to_hex(b64):
    return base64.b64decode(b64).hex()


def hex_to_b64(hex):
    return base64.b64encode(bytes.fromhex(hex))


def save_hashcache_entry(hashcache, filename, hash, size, modtime):
    data = {"filename": filename, "hash": hash, "size": size, "modtime": modtime}

    new_hashcache = hashcache + [data]

    with open("hashcache.json", "w") as f:
        f.write(json.dumps(new_hashcache, indent=2, sort_keys=True))

    return new_hashcache


def get_hashcache():
    if not os.path.exists("hashcache.json"):
        return []
    with open("hashcache.json", "r") as f:
        data = f.read()
    return json.loads(data)


def get_hashcache_entries(hashcache, fname=None, modtime=None, hash=None, size=None):
    retval = hashcache
    if fname:
        retval = [x for x in hashcache if x["filename"] == fname]
    if modtime:
        retval = [x for x in retval if x["modtime"] == modtime]
    if hash:
        retval = [x for x in retval if x["hash"] == hash]
    if size:
        retval = [x for x in retval if x["size"] == size]
    return retval


def get_file_wabbajack_hashcache(hashcache, fname):
    size = os.path.getsize(fname)
    modtime = int(os.path.getmtime(fname))
    possible = get_hashcache_entries(
        hashcache, fname, modtime=modtime, hash=None, size=size
    )
    # print('p[osssi')
    # print(possible)
    if len(possible) != 0:
        print("using cache for " + fname)
        return {"cache": hashcache, "hash": possible[0]["hash"]}
    else:
        _hash = get_file_wabbajack_hash(fname)
        hashcache = save_hashcache_entry(
            hashcache, filename=fname, hash=_hash, size=size, modtime=modtime
        )
        return {"cache": hashcache, "hash": _hash}


# hashcache_db = None
# def get_hashcache_db():
#     if hashcache_db is None: hashcache_db = sqlite3.connect(HASH_CACHE)
#     c = hashcache_db.cursor()
#     c.execute('CREATE TABLE IF NOT EXISTS hash_cache (filename TEXT, hash TEXT, size INTEGER, modtime INTEGER)')
#     return hashcache_db

# def save_hashcache_entry(sqc, fname, hashhex, size, modtime):
#     values = {}
#     values['filename'] = fname
#     values['hash'] = hashhex
#     values['size'] = size
#     values['modtime'] = modtime

#     c = sqc.cursor()
#     cursor.execute("INSERT INTO hash_cache VALUES (:filename, :hash, :size, :modtime)", values)

# def get_hashcache_entries(sqc, fname):
#     c = sqc.cursor()
#     rows = c.execute("SELECT * FROM hash_cache WHERE filename = ?", (fname,))
#     return c.fetchall()

if __name__ == "__main__":
    FAIL_MAX = 999999

    import sys

    fnames = sys.argv[1:]

    hashcache = get_hashcache()
    errors = []
    for fname in fnames:
        try:
            fail_cnt = 0

            mod_data = get_mod_data(fname)
            extract_mod_data(fname)
            archives = mod_data["Archives"]
            random.shuffle(archives)
            for archive in archives:
                archive_name = archive["Name"]
                archive_type = archive["$type"]
                archive_state_type = archive["State"]["$type"]
                archive_hash = archive["Hash"]
                hash_hex = b64_to_hex(archive_hash)
                print(f"{archive_type}")
                print(
                    f'working on "{archive_name}" with hash of {archive_hash} (hex is {hash_hex})'
                )
                if archive_state_type == "GameFileSourceDownloader, Wabbajack.Lib":
                    print("this type was gamefilesourcedownloader, skipping")
                    continue
                path = r"../downloads/" + archive_name
                print("trying to hash " + path)
                if not os.path.exists(path):
                    print("doesn't exist, wtf?")
                    error = f"{archive_name} file doesn't exist!"
                    errors += [[fname, error, archive]]
                    print(error)
                    continue
                hashcache_lookup = get_file_wabbajack_hashcache(hashcache, path)
                hashcache = hashcache_lookup["cache"]
                wabbajack_hash = hashcache_lookup["hash"]
                print("got hash wabbajack")
                print(wabbajack_hash)
                if hash_hex != wabbajack_hash:
                    print("wtf failure")
                    print(archive)
                    error = f"hash failure on {archive_name} with hash of {archive_hash} (hex is {hash_hex}) ; we got {wabbajack_hash}"
                    errors += [[fname, error, archive]]
                    print(error)
                    if fail_cnt > FAIL_MAX:
                        raise Exception()
                    else:
                        fail_cnt += 1

                else:
                    print("success!")
                print("---")
        except Exception as e:
            # raise e
            print(fname + "failed exception")
            print(e)

    if len(errors):
        input("done, press enter for errors")
        for fname, error, archive in errors:
            print(fname, error)
            print(pprint_json(archive))
    input("done!")
