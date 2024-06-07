import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import os

# from candidates import format_candidate, get_candidate

SAVE_FOLDER = "communities"

# example provinsi-aceh
paths = [
    # "provinsi-nusa-tenggara-timur",
    # "provinsi-papua-barat-daya",
    # "provinsi-papua-selatan",
    # "provinsi-papua-tengah",
    # "provinsi-riau",
    # "provinsi-sulawesi-barat",
    # "provinsi-sulawesi-tengah",
    # "provinsi-sulawesi-tenggara",
    # "provinsi-sumatra-selatan",
    # "provinsi-sumatra-utara",
]

communityID = ""

# FORMAT CANDIDATE
def format_candidate(name, description = "", profilePic = "", url = "", title = ""):
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

# GET CANDIDATE INFO
def get_candidate(url, title, name):
    url = "https://id.wikipedia.org" + url

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html5lib")

    try:
        name = name # soup.find("h1", class_="firstHeading").text

        try:
            description = soup.find("div", class_="mw-parser-output").find("p", class_=lambda x: x != "mw-empty-elt").text
        except:
            description = ""

        try:
            profilePic = soup.find("meta", property="og:image")["content"]
        except:
            profilePic = ""

        return format_candidate(name, description, profilePic, url, title)
    except:
        return

def get_candidate_wiki(el, name):
    url = None

    contentWithoutTitle = [x for x in el.contents if not x.text in ['Letjen', 'TNI', ' (', 'Purn.', ') ', ' ']]

    for content in contentWithoutTitle:
        if isinstance(content, NavigableString):
            break
        elif content.name == 'a' and not content.text.lower() in ['letjen', 'tni', 'purn.']:
            url = content.get('href')

            print(url)

            if "action=edit" in url or "/wiki/" not in url:
                url = None

            break

    return url

def get_candidate_name(el):
    name = None

    for (index, content) in enumerate(el.contents):
        if isinstance(content, NavigableString):
            text = content.strip()
            if ',' in text:
                name = text.split(',')[0]
                break
            elif text != None and text != ' ':
                name = text
                break
        elif content.name == 'a' and 'letjen' in content.text.lower():
            name = el.text.split(',')[0] 
            break
        elif content.name == 'a' or content.name == 'b':
            name = content.text
            break
    
    # print(name)
    # print()
    return name

def get_candidate_title(el, level, name):
    title = None

    text = el.text
    text = text.replace(name, "")

    try:
        if (': ' in text):
            title = text.split(':')[1].strip()
        else:
            title = text.split(',')[1].strip()

        title = re.sub(r'\[.*?\]', '', title) # remove references

        if title[-1] == '.':
            title = title[:-1] # remove trailing dot

        title = title[0].upper() + title[1:] # capitalize first letter
    except:
        pass

    if title is None or title == "":
        switcher = {
            "PROVINSI": "Bakal Calon Gubernur",
            "KABUPATEN": "Bakal Calon Bupati",
            "KOTA": "Bakal Calon Wali Kota"
        }

        title = switcher.get(level, "")

    return title

def get_candidates(source, level):
    page = requests.get(source)
    soup = BeautifulSoup(page.content, "html5lib")

    try:
        parent = soup.find("span", attrs={"id": re.compile("^(Daftar_calon|Bakal_Calon|Potensial|Potensi)")}).parent.find_next_sibling("ul")

        ul = [x for x in parent.find_all("li")]

        candidates = []
        for li in ul:
            name = get_candidate_name(li)
            
            if name is None:
                continue

            href = get_candidate_wiki(li, name)
            title = get_candidate_title(li, level, name)

            print(name)
            print(title)
            # print(href)
            print("\n")
            # input()

            if (href):
                candidate = get_candidate(href, title, name)
            else:
                candidate = format_candidate(name=name, title=title)
            
            candidates.append(candidate)

        return candidates
    except Exception as e:
        print(e)
        return []

for item in paths:
    filepath = f"{SAVE_FOLDER}/{item}.json"

    with open(filepath, "r") as f:
        item = json.load(f)

    title = item['title']
    wiki = item['source']
    level = item['level']
    path = item['path']
    communityID = item["communityID"]

    candidates = get_candidates(wiki, level)

    item.update({"candidates": candidates})

    with open(filepath, "w") as f:
        f.write(json.dumps(item, indent=4))

    print(f"{title} - Saved")

print("Done")