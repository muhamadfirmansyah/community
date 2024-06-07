import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import os

# from candidates import format_candidate, get_candidate

SAVE_FOLDER = "communities"

# example dki-jakarta
paths = [
    "kota-bekasi"
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
def get_candidate(url, title):
    url = "https://id.wikipedia.org" + url

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html5lib")

    try:
        name = soup.find("h1", class_="firstHeading").text

        try:
            description = soup.find("div", class_="mw-parser-output").find("p").text
        except:
            description = ""

        try:
            profilePic = soup.find("meta", property="og:image")["content"]
        except:
            profilePic = ""

        return format_candidate(name, description, profilePic, url, title)
    except:
        return

def get_candidate_wiki(el):
    url = None

    for content in el.contents:
        if isinstance(content, NavigableString):
            break
        elif content.name == 'a':
            url = content.get('href')

            if "action=edit" in url:
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
            elif text and not ' ' in text:
                name = text
                break
        elif content.name == 'a' or content.name == 'b':
            name = content.text
            break

    return name

def get_candidate_title(el, level):
    title = None

    text = el.text

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
            href = get_candidate_wiki(li)
            title = get_candidate_title(li, level)

            if (href):
                candidate = get_candidate(href, title)
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