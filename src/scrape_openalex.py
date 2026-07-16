import requests
import json
import os
import time


OPENALEX = "https://api.openalex.org/works"

CRDC_FILE = "data/crdc/crdc.json"
OUTPUT = "data/research/forestry.json"


# -------------------------
# Load CRDC taxonomy
# -------------------------

def load_crdc():

    with open(CRDC_FILE) as f:
        return json.load(f)



# -------------------------
# Find CRDC matches
# -------------------------

def map_crdc(work, crdc):

    text = " ".join([
        work.get("title", ""),
        work.get("abstract", "")
    ]).lower()


    matches = []


    keywords = {
        "forestry": [
            "forest",
            "forestry",
            "wood",
            "timber",
            "tree",
            "silviculture",
            "biodiversity"
        ],

        "climate": [
            "carbon",
            "climate",
            "emission"
        ]
    }


    for category, words in keywords.items():

        if any(w in text for w in words):

            matches.append(category)


    return matches



# -------------------------
# Query OpenAlex
# -------------------------

def fetch_forestry():

    params = {

        "search":
            "forestry",

        "filter":
            "institutions.country_code:CA",

        "per-page":
            100,

        "sort":
            "cited_by_count:desc"
    }


    r = requests.get(
        OPENALEX,
        params=params
    )

    r.raise_for_status()

    return r.json()["results"]



# -------------------------
# Normalize record
# -------------------------

def normalize(work, crdc):


    authors = [
        a["author"]["display_name"]
        for a in work.get("authorships", [])
    ]


    institutions = []

    for a in work.get("authorships", []):

        for inst in a.get("institutions", []):

            institutions.append(
                inst["display_name"]
            )


    return {

        "id":
            work["id"],


        "title":
            work["title"],


        "year":
            work["publication_year"],


        "doi":
            work.get("doi"),


        "authors":
            list(set(authors)),


        "institutions":
            list(set(institutions)),


        "citations":
            work["cited_by_count"],


        "openalex_concepts":
            [
                c["display_name"]
                for c in work.get(
                    "concepts",
                    []
                )[:10]
            ],


        "crdc":
            map_crdc(
                work,
                crdc
            )
    }



# -------------------------
# Main
# -------------------------

def main():

    crdc = load_crdc()


    works = fetch_forestry()


    output = []


    for work in works:

        output.append(
            normalize(
                work,
                crdc
            )
        )


        time.sleep(.1)


    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )


    print(
        f"Saved {len(output)} records"
    )



if __name__ == "__main__":
    main()