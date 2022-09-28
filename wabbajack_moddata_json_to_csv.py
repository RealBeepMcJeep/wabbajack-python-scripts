import json
import os

# archive state types and how to handle them
# we use the entire thing here, there's nothing unique to pull out
RAW_STATE_TYPES = [
    "GoogleDriveDownloader",
    "MegaDownloader",
    "WabbajackCDNDownloader",
    "HTTPDownloader+State",
    "MediaFireDownloader",
    "ManualDownloader",
    "ModDBDownloader",
]

# this includes forumID
FIRSTSPLIT_STATE_TYPES = ["VectorPlexus", "LoversLab"]

# Nexus includes modID, we skip fileID
# GameFileSourceDownloader includes game version, we skip the fname
SECONDSPLIT_STATE_TYPES = ["NexusDownloader", "GameFileSourceDownloader"]

seen = set()
URL_TYPES = [
    "HttpDownloader, Wabbajack.Lib",
    "MegaDownloader, Wabbajack.Lib",
    "ManualDownloader, Wabbajack.Lib",
    "MediaFireDownloader+State, Wabbajack.Lib",
]


def archive_to_uuid_nofile(archive):
    state = archive["State"]
    _type = state["$type"]
    if _type == "HttpDownloader, Wabbajack.Lib":
        return {"uuid": state["Url"]}
    elif _type == "NexusDownloader, Wabbajack.Lib":
        return {"uuid": "Nexus:" + str(state["ModID"])}
    elif _type == "GameFileSourceDownloader, Wabbajack.Lib":
        return False
    elif _type == "WabbajackCDNDownloader+State, Wabbajack.Lib":
        return False
    elif _type == "GoogleDriveDownloader, Wabbajack.Lib":
        return {"uuid": "GDRIVE_" + state["Id"]}
    elif _type in URL_TYPES:
        return {"uuid": state["Url"]}
    elif _type == "VectorPlexusOAuthDownloader+State, Wabbajack.Lib":
        return {"uuid": state["URL"]}
    elif _type == "ModDBDownloader, Wabbajack.Lib":
        return {"uuid": state["Url"].split("?")[0]}
    else:
        print(archive)
        raise Exception("Unhandled archive type!", _type)


def pprint(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))


# state_types = []
modlist_uuids = {}
uuids_modlists = {}
uuid_name = {}
uuid_archive = {}


def comp_version(version_str1, version_str2):
    parts1 = version_str1.split(".")
    parts2 = version_str2.split(".")

    tuple1 = tuple([int(x) for x in parts1])
    tuple2 = tuple([int(x) for x in parts2])

    if tuple1 > tuple2:
        return version_str1
    if tuple2 > tuple1:
        return version_str2
    else:
        return 0


if __name__ == "__main__":
    latest_mod_version = {}

    fnames_moddata = [x for x in os.listdir() if x.endswith(".moddata.json")]
    for fname in fnames_moddata:
        basename = fname.replace(".moddata.json", "")
        try:
            (mod, version) = basename.split("_")
        except Exception as e:
            print("failed to", basename)
            continue

        print(mod, version)

        if mod == "Tsukiro" and version.split(".")[1] != "0":
            print("tsukiro 2 is not 0")
            continue
        if mod not in latest_mod_version:
            print(mod, "latest version is actually", version)
            latest_mod_version[mod] = version
        else:
            if comp_version(version, latest_mod_version[mod]) == version:
                print(mod, "latest version is actually", version)
                latest_mod_version[mod] = version

    for (mod, version) in latest_mod_version.items():
        fname = "_".join([mod, version]) + ".moddata.json"
        modlist = " ".join([mod, version])

        with open(fname, "r") as f:
            d = f.read()
        j = json.loads(d)
        archives = j["Archives"]

        if modlist not in modlist_uuids:
            modlist_uuids[modlist] = []

        for archive in archives:
            print(archive)
            uuid_data = archive_to_uuid_nofile(archive)
            if uuid_data is False:
                continue
            if uuid_data == "":
                continue
            uuid = uuid_data["uuid"]
            # if uuid == '40565':
            #     print('asdaoidhjasihjdsahjodiajsdjuoaisdj')
            #     print(archive)
            #     raise Exception

            uuid_archive[uuid] = archive

            name = False
            if "Name" in archive["State"] and archive["State"]["Name"] != "":
                uuid_name[uuid] = archive["State"]["Name"]
            elif "Name" in archive and archive["Name"] != "":
                uuid_name[uuid] = archive["Name"]
            else:
                uuid_name[uuid] = uuid

            if uuid not in modlist_uuids[modlist]:
                modlist_uuids[modlist] += [uuid]

            if uuid not in uuids_modlists:
                uuids_modlists[uuid] = [modlist]
            else:
                if modlist not in uuids_modlists[uuid]:
                    uuids_modlists[uuid].append(modlist)

        print("done with", fname, ", dumping progress to files")

        with open("uuids_modlists.csv", "w") as f:
            modlists_by_size = sorted(
                modlist_uuids.keys(), key=lambda x: len(modlist_uuids[x]), reverse=True
            )
            uuids_by_count = sorted(
                [x for x in uuids_modlists],
                key=lambda x: len(uuids_modlists[x]),
                reverse=True,
            )

            lines = []

            # headers
            header_line = ["uuid", "name", "count"] + modlists_by_size
            header_line = ",".join(header_line)
            lines += [header_line]

            for uuid in uuids_by_count:
                source = uuid

                if uuid in uuid_name:
                    modname = uuid_name[uuid]
                    _id = uuid.split("|")[-1]
                    if _id == modname:
                        name = modname
                    else:
                        name = f"{modname} ({_id})"
                else:
                    name = "|".join(uuid.split("|")[1:])
                # first column is name or uuid
                line = [source, name]

                modlists_with_uuid = uuids_modlists[uuid]

                # second column is count
                line.extend([len(modlists_with_uuid)])

                # further columns are if the modlist has the mod or not
                for modlist in modlists_by_size:
                    line += ["x" if modlist in modlists_with_uuid else ""]

                line = ",".join(['"' + str(x) + '"' for x in line])
                if "-29235" in line:
                    print(";123h9f8032f108uh21398h213hf123120398f129830f21938fh")
                    print("wtf")
                    print(uuid)
                    pprint(print(uuid_archive[uuid]))
                    print(";123h9f8032f108uh21398h213hf123120398f129830f21938fh")
                lines += [line]

            f.write("\n".join(lines))
