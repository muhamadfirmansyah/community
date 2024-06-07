import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import os

KABUPATEN_URL = "https://goodkind.id/api/communities?level=Kabupaten&size=500"
KOTA_URL = "https://goodkind.id/api/communities?level=Kota&size=500"
PROVINSI_URL = "https://goodkind.id/api/communities?level=Provinsi&size=500"

KABUPATEN = json.loads(requests.get(KABUPATEN_URL).text)
KOTA = json.loads(requests.get(KOTA_URL).text)
PROVINSI = json.loads(requests.get(PROVINSI_URL).text)

# GET COMMUNITY ID
def get_community_id(level, path):
    lists = []

    if (level == "KABUPATEN"):
        lists = KABUPATEN.get("data", [])

    elif (level == "KOTA"):
        lists = KOTA.get("data", [])

    elif (level == "PROVINSI"):
        lists = PROVINSI.get("data", [])

    for item in lists:
        if (path == item.get("path")):
            return item.get("id")

    return ""

data = []
with open("used/data-with-path.json", "r") as f:
    data = json.load(f)

for item in data:
    del item["candidates"]

    communityID = get_community_id(item['level'], item['path'])

    item.update({
        "communityID": communityID
    })


print('Total: ', len(data))

with open("communities.json", "w") as f:
    f.write(json.dumps(data, indent=4))
    f.close()