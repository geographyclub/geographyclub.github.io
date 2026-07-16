import requests

url = "https://www.nserc-crsng.gc.ca/ase-oro/index_eng.asp"

headers = {
    "User-Agent":
        "ResearchCanadaBot/0.1"
}

r = requests.get(
    url,
    headers=headers,
    timeout=60
)

print(r.status_code)
print(r.url)

with open(
    "nserc_debug.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(r.text)

print(len(r.text))