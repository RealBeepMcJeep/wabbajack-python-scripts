import csv
import json
import os
import requests
import datetime

from config import NEXUSMODS_API_KEY, NEXUSMODS_CACHE_DIR, NEXUSMODS_CATEGORY_ID_TO_CATEGORY
from util import get_timestamp_now, format_json

def get_modid_url(modid):
    return f"https://api.nexusmods.com/v1/games/skyrimspecialedition/mods/{modid}.json"

def lookup_nexus_moddata(modid):
    fname = modid + ".json"
    path = os.path.join(NEXUSMODS_CACHE_DIR, fname)

    if os.path.exists(path):
        print("returning cached", modid)
        with open(path, "r") as f:
            return (json.loads(f.read()), 99999999, 9999999)
    else:
        print("retrieving", modid)
        url = get_modid_url(modid)
        print(url)
        r = requests.get(
            url, headers={"accept": "application/json", "apikey": NEXUSMODS_API_KEY}
        )
        moddata = r.json()
        print('gottem')
        print(json.dumps(moddata, indent=2, sort_keys=True))
        is_not_found = len(moddata.keys()) == 1 and 'error' in moddata and 'not found' in moddata['error']
        if not is_not_found:
            moddata['category'] = NEXUSMODS_CATEGORY_ID_TO_CATEGORY[str(moddata['category_id'])]
        moddata["last_retrieved"] = get_timestamp_now()
        with open(path, "w") as f:
            f.write(json.dumps(moddata, indent=2, sort_keys=True))
        hourly_calls_left = int(r.headers['x-rl-hourly-remaining'])
        daily_calls_left = int(r.headers['x-rl-daily-remaining'])
        return (moddata, hourly_calls_left, daily_calls_left)


if __name__ == "__main__":
    with open("uuids_modlists.csv", "r") as f:
        csvreader = csv.reader(f)
        csv_data = [row for row in csvreader]

    csv_headers = csv_data[0]
    csv_data = csv_data[1:]

    categories_seen = {}
    try:
        with open('uuids_categories_modlists.csv', 'w', newline='', encoding='utf-8') as f:
            csvwriter = csv.writer(f)

            # uuid, name, category, count, lists...
            new_csv_headers = csv_headers[0:1] + ['category'] + csv_headers[1:]
            csvwriter.writerow(new_csv_headers)

            new_csv_data = []
            for idx, data in enumerate(csv_data):
                uuid, name, count, *rest = data
                print(uuid,name)
                hourly_calls_left = 99999999
                daily_calls_left = 99999999
                moddata = {}

                if False:
                    pass
                elif 'loverslab.com' in uuid:
                    category = 'LoversLab'
                elif 'vectorplexus.com' in uuid:
                    category = 'VectorPlexus'
                elif uuid.startswith('Nexus'):
                    print(name)
                    modid = uuid.split(':')[1]
                    moddata, hourly_calls_left, daily_calls_left = lookup_nexus_moddata(modid)
                    # print(lookup_nexus_moddata(modid))
                    print(idx, '/', len(csv_data), f'({round(idx / len(csv_data) * 100)}%)', '-', hourly_calls_left, '/', daily_calls_left, 'hourly/daily calls left')
                    if 'category' in moddata:
                        category = moddata['category']
                    elif 'category_id' in moddata:
                        category = moddata['category_id']
                    else:
                        category = 'Missing'
                else:
                    category = 'Unknown'

                if not category.isnumeric():
                    if category not in categories_seen:
                        categories_seen[category] = {'category': category, 'known_data': moddata, 'uuid': uuid, 'count': 1}
                    else:
                        categories_seen[category]['count'] += 1
                    
                csv_row = [uuid, category, name, count, *rest]
                csvwriter.writerow(csv_row)
                if min(int(hourly_calls_left), int(daily_calls_left)) <= 0:
                    print('API LIMIT REACHED, BAILING!')
                    break
            
            categories_seen_by_count = sorted(categories_seen.values(), key=lambda x: x['count'], reverse=True)
            print('categories seen:', ", ".join([f"{x['category']} ({x['count']})" for x in categories_seen_by_count]))

            print('samples of categories missing id->name:')
            for category in categories_seen:
                if category.isnumeric():
                    data = categories_seen[category]
                    print('numeric category', category, 'sample:')
                    print(format_json(data))

    finally:
        print('closing csv')
        f.close()
    
