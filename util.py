import datetime
import json

def get_timestamp_now():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

def format_json(_json):
    return json.dumps(_json, indent=True, sort_keys=True)