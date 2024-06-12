import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import os

from helper import *

wikiurl = "https://id.wikipedia.org/wiki/Daftar_gubernur_dan_wakil_gubernur_di_Indonesia"
page = requests.get(wikiurl)
soup = BeautifulSoup(page.content, "html5lib")
table = soup.find("table", class_="wikitable").find_all("tr")

def get_gubernur(tds, communityID):
    try:
        gubernur_region = tds[0].find_all("a")[1].text
        gubernur_source = get_wikiurl(tds[3].find("a").get("href"))

        person_detail = get_person_detail(gubernur_source)
        gubernur_description = person_detail.get("description")
        gubernur_profilePic = person_detail.get("profilePic")
        
        if not gubernur_profilePic:
            try:
                gubernur_profilePic = get_url(tds[1].find("img").get("src", ""))
            except:
                gubernur_profilePic = ""

        gubernur_name = tds[3].find("a").text
        is_pj = True if "penjabat" in tds[3].text.lower() else False
        gubernur_title = "Gubernur (PJ)" if is_pj else "Gubernur"

    except Exception as e:
        print(f"{communityID}: {e}")
        return None

    return format_data(
        name=gubernur_name, 
        description=gubernur_description, 
        profilePic=gubernur_profilePic, 
        url=gubernur_source, 
        title=gubernur_title, 
        level="PROVINSI",
        communityID=communityID
    )

def get_wakil_gubernur(tds, communityID):
    try:
        is_empty = tds[4].text.strip() == "lowong"

        if is_empty:
            return None

        wakil_gubernur_region = tds[0].find_all("a")[1].text
        wakil_gubernur_source = get_wikiurl(tds[6].find("a").get("href"))

        person_detail = get_person_detail(wakil_gubernur_source)
        wakil_gubernur_description = person_detail.get("description")
        wakil_gubernur_profilePic = person_detail.get("profilePic")

        if not wakil_gubernur_profilePic:
            try:
                wakil_gubernur_profilePic = get_url(tds[4].find("img").get("src"))
            except:
                wakil_gubernur_profilePic = ""

        wakil_gubernur_name = tds[6].find("a").text
        wakil_gubernur_title = "Wakil Gubernur"
    except Exception as e:
        print(f"{communityID}: {e}")
        return None

    return format_data(
        name=wakil_gubernur_name, 
        description=wakil_gubernur_description, 
        profilePic=wakil_gubernur_profilePic, 
        url=wakil_gubernur_source, 
        title=wakil_gubernur_title, 
        level="PROVINSI", 
        communityID=communityID
    )

communities = []
for row in table:
    tds = row.find_all("td")

    if not tds:
        continue

    community = format_community(
        title="Gubernur dan Wakil Gubernur __name__",
        source=wikiurl,
        region=tds[0].find_all("a")[1].text,
        level="PROVINSI",
    )

    path = community.get("path", "")
    communityID = community.get("communityID", "")

    gubernur = get_gubernur(tds, communityID)
    wakil_gubernur = get_wakil_gubernur(tds, communityID)
    
    candidates = []
    if (gubernur):
        candidates.append(gubernur)
    if (wakil_gubernur):
        candidates.append(wakil_gubernur)

    community.update({
        "candidates": candidates
    })
    
    communities.append(community)

    filepath = f"incumbent/incumbents/{path}.json"
    with open(filepath, "w") as f:
        json.dump(community, f, indent=4)

    # print(community)
    # print(gubernur)
    # print(wakil_gubernur)

    # if (tds):
    #     for (index, td) in enumerate(tds):
    #         print(f"{index}  -  {td}")
    #         print("")


    #     exit()


# with open("incumbent/incumbents.json", "w") as f:
#     json.dump(communities, f, indent=4)