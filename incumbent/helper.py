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

def get_community(level, keyword, key = ""):
    keyword = (level + " " + keyword).lower().replace(" ", "")

    keyword = keyword.replace("sumatera", "sumatra")
    keyword = keyword.replace("kotapadangsidempuan", "kotapadangsidimpuan")
    keyword = keyword.replace("kotatangjungbalai", "kotatanjungbalai")
    keyword = keyword.replace("provinsidaerahkhususibukotajakarta", "provinsidkijakarta")

    lists = []

    if (level == "KABUPATEN"):
        lists = KABUPATEN.get("data", [])

    elif (level == "KOTA"):
        lists = KOTA.get("data", [])

    elif (level == "PROVINSI"):
        lists = PROVINSI.get("data", [])

    for item in lists:
        if (keyword in item.get("name", "").lower().replace(" ", "")):
            if key:
                return item.get(key, "path")
            else:
                return item

    print("NOT FOUND: " + keyword)
    return ""

def format_data(name, description = "", profilePic = "", url = "", title = "", communityID = "", level = "", region = ""):

    if (communityID == ""):
        communityID = get_community(level=level, keyword=region, key="id")

    return {
        "name": name,
        "description": description,
        "profilePic": profilePic,
        "title": title,
        "sites": {
            "name": "Wikipedia",
            "url": url
        } if url else {},
        "communityID": communityID
    }

def format_community(title = "", source = "", region = "", level = ""):
    community = get_community(level=level, keyword=region)
    name = community.get("name", "")
    path = community.get("path", "")
    communityID = community.get("id", "")

    title = title.replace("__name__", name)

    return {
        "title": title,
        "source": source,
        "region": region,
        "level": level,
        "path": path,
        "communityID": communityID
    }

def get_wikiurl(url):
    if not url:
        return ""

    if "action=edit" in url:
        return None

    if "/wiki/" not in url:
        return None

    if "https://id.wikipedia.org" in url:
        return url

    return "https://id.wikipedia.org" + url

def get_url(url):
    if not url:
        return ""

    if "http" in url:
        return url

    return "https:" + url

def get_person_detail(url):
    if not url:
        return ""

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html5lib")

    try:
        description = soup.find("div", class_="mw-parser-output").find("p", class_=lambda x: x != "mw-empty-elt").text
    except:
        description = ""

    try:
        profilePic = soup.find("meta", property="og:image")["content"]
    except:
        profilePic = ""

    return {
        "description": description,
        "profilePic": profilePic,
    }