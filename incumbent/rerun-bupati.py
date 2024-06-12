import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import os

from helper import *

list_wikiurl = "https://id.wikipedia.org/wiki/Kategori:Daftar_bupati_dan_wali_kota_di_Indonesia"
page = requests.get(list_wikiurl)
soup = BeautifulSoup(page.content, "html5lib")
links = soup.find_all("a", string=re.compile(r"petahana"))

need_rerun = [
    "kabupaten-banggai-kepulauan",
    "kabupaten-bangka",
    "kabupaten-barito-timur",
    "kabupaten-barito-utara",
    "kabupaten-buol",
    "kabupaten-buton-tengah",
    "kabupaten-buton",
    "kabupaten-hulu-sungai-selatan",
    "kabupaten-indragiri-hilir",
    "kabupaten-katingan",
    "kabupaten-kayong-utara",
    "kabupaten-kerinci",
    "kabupaten-klungkung",
    "kabupaten-kotawaringin-barat",
    "kabupaten-lebak",
    "kabupaten-mamasa",
    "kabupaten-mempawah",
    "kabupaten-merangin",
    "kabupaten-muaro-jambi",
    "kabupaten-murung-raya",
    "kabupaten-polewali-mandar",
    "kabupaten-sanggau",
    "kabupaten-sarolangun",
    "kabupaten-sidenreng-rappang",
    "kabupaten-tanah-laut",
    "kabupaten-tapin",
    "kabupaten-tebo",
    "kota-jambi",
    "kota-kediri",
    "kota-madiun",
    "kota-mojokerto",
    "kota-subulussalam",
]

def get_bupati(tds, communityID, is_kabupaten):
    try:
        bupati_region = tds[0].find_all("a")[1].text
        bupati_source = get_wikiurl(tds[3].find("a").get("href"))

        bupati_name = tds[3].find("a").text
        if bupati_name == "Penjabat":
            bupati_source = ""
            
            try:
                bupati_name = tds[3].contents[0].strip()
            except:
                bupati_name = tds[3].text

        person_detail = get_person_detail(bupati_source)
        bupati_description = person_detail.get("description")
        bupati_profilePic = person_detail.get("profilePic")
        
        if not bupati_profilePic:
            try:
                bupati_profilePic = get_url(tds[1].find("img").get("src", ""))
            except:
                bupati_profilePic = ""

        is_pj = True if "penjabat" in tds[3].text.lower() else False
        title = "Bupati" if is_kabupaten else "Wali Kota"
        bupati_title = f"{title} (PJ)" if is_pj else title

    except Exception as e:
        print(f"{communityID}: {e}")
        return None

    return format_data(
        name=bupati_name, 
        description=bupati_description, 
        profilePic=bupati_profilePic, 
        url=bupati_source, 
        title=bupati_title, 
        level="KABUPATEN" if is_kabupaten else "KOTA",
        communityID=communityID
    )

def get_wakil_bupati(tds, communityID, is_kabupaten):
    try:
        is_empty = tds[6].text.strip() == ""

        if is_empty:
            return None

        wakil_bupati_region = tds[0].find_all("a")[1].text
        try:
            wakil_bupati_source = get_wikiurl(tds[6].find("a").get("href"))
        except:
            wakil_bupati_source = None

        person_detail = get_person_detail(wakil_bupati_source)
        wakil_bupati_description = person_detail.get("description")

        wakil_bupati_profilePic = person_detail.get("profilePic")

        if not wakil_bupati_profilePic:
            try:
                wakil_bupati_profilePic = get_url(tds[4].find("img").get("src"))
            except:
                wakil_bupati_profilePic = ""

        wakil_bupati_name = tds[6].find("a").text
        wakil_bupati_title = "Wakil Bupati" if is_kabupaten else "Wakil Wali Kota"

    except Exception as e:
        print(f"{communityID}: {e}")
        return None

    return format_data(
        name=wakil_bupati_name, 
        description=wakil_bupati_description, 
        profilePic=wakil_bupati_profilePic, 
        url=wakil_bupati_source, 
        title=wakil_bupati_title, 
        level="KABUPATEN" if is_kabupaten else "KOTA", 
        communityID=communityID
    )

for link in links:
    wikiurl = get_wikiurl(link.get("href"))
    page = requests.get(wikiurl)
    soup = BeautifulSoup(page.content, "html5lib")
    table = soup.find("table", class_="wikitable").find_all("tr")

    for row in table:
        tds = row.find_all("td")

        if not tds:
            continue
        
        # for (index, td) in enumerate(tds):
        #     print(f"{index}  -  {td}")
        #     print("")
        # exit()

        region = tds[0].find_all("a")[1].get("title")
        is_kabupaten = "kabupaten" in region.lower()
        title = "Bupati dan Wakil Bupati" if is_kabupaten else "Wali Kota dan Wakil Wali Kota"

        community = format_community(
            title=f"{title} __name__",
            source=wikiurl,
            region=region,
            level="KABUPATEN" if is_kabupaten else "KOTA"
        )

        path = community.get("path", "")
        communityID = community.get("communityID", "")

        if not path in need_rerun:
            continue

        bupati = get_bupati(tds, communityID, is_kabupaten)
        wakil_bupati = get_wakil_bupati(tds, communityID, is_kabupaten)
        
        candidates = []
        if (bupati):
            candidates.append(bupati)
        if (wakil_bupati):
            candidates.append(wakil_bupati)

        community.update({
            "candidates": candidates
        })

        filepath = f"incumbent/incumbents/{path}.json"
        with open(filepath, "w") as f:
            json.dump(community, f, indent=4)

        print(f"{path} done")

        # print(community)
        # exit()