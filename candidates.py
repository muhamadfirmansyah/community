import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import os

FROM_FILE = "communities.json"
SAVE_FOLDER = "communities"

data = []
if os.path.exists(FROM_FILE):
    with open(FROM_FILE, "r") as f:
        data = json.load(f)

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

    for content in el.contents:
        if isinstance(content, NavigableString):
            text = content.strip()
            if ',' in text:
                name = text.split(',')[0]
                break
            else:
                name = text
                break
        elif content.name == 'a':
            name = content.text
            break

    return name

def get_candidate_title(el, level):
    title = None

    text = el.text

    try:
        title = text.split(',')[1].strip()

        title = re.sub(r'\[.*?\]', '', title) # remove references

        if title[-1] == '.':
            title = title[:-1] # remove trailing dot

        title = title[0].upper() + title[1:] # capitalize first letter
    except:
        pass

    if title == "":
        switcher = {
            "PROVINSI": "Calon Gubernur",
            "KABUPATEN": "Calon Bupati",
            "KOTA": "Calon Wali Kota"
        }

        title = switcher.get(level, "")

    return title

# GET CANDIDATES
def get_candidates(source, level):
    page = requests.get(source)
    soup = BeautifulSoup(page.content, "html5lib")

    try:
        parent = soup.find("span", attrs={"id": re.compile("^(Bakal_Calon|Potensial|Potensi)")}).parent.find_next_sibling("ul")

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

def if_file_exists(path):
    filename = SAVE_FOLDER + "/" + path + ".json"
    return os.path.isfile(filename)

def save_data(path, data):
    filename = SAVE_FOLDER + "/" + path + ".json"
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))
        f.close()

if SAVE_FOLDER and not os.path.exists(SAVE_FOLDER):
    os.mkdir(SAVE_FOLDER)

pilkada_with_wiki = 0
pilkada_with_no_wiki = 0
pilkada_with_candidates = 0
pilkada_with_no_candidates = 0
pilkada_skipped = 0

for index, item in enumerate(data):
    title = item['title']
    wiki = item['source']
    level = item['level']
    path = item['path']

    message = title + " - " + str(index + 1) + "/" + str(len(data))

    if (if_file_exists(path)):
        pilkada_skipped += 1
        message += " - " + "Skiped"
        print(message)
        continue
    
    if (wiki != ""):
        communityID = item["communityID"]
        
        candidates = get_candidates(wiki, level)

        if (len(candidates) == 0):
            pilkada_with_no_candidates += 1
        else:
            pilkada_with_candidates += 1

        pilkada_with_wiki += 1
        item.update({"candidates": candidates})
    else:
        item.update({"candidates": []})
        pilkada_with_no_wiki += 1
        pilkada_with_no_candidates += 1

    message = item['title'] + " - " + str(index + 1) + "/" + str(len(data))

    if (not if_file_exists(path)):
        save_data(path, item)
        message += " - " + "Saved"

    print(message)

print("\n")
print("Pilkada with wiki: ", (pilkada_with_wiki))
print("Pilkada with no wiki: ", (pilkada_with_no_wiki))
print("Pilkada with candidates: ", (pilkada_with_candidates))
print("Pilkada with no candidates: ", (pilkada_with_no_candidates))
print("Pilkada skipped: ", (pilkada_skipped))
print("Total: ", len(data))
print("Correct Total: 545")
print("Missing: ", (545 - len(data)))
print("\n")
