#!/usr/bin/env python3

import csv
import json
from pathlib import Path


# -----------------------------
# CONFIG
# -----------------------------

ROOT = Path(__file__).resolve().parents[1]

CRDC = ROOT / "data" / "crdc"

FOR_STRUCTURE = CRDC / "CRDC-CCRD-2020-FOR-DDR-StructureV2-eng.csv"
FOR_ELEMENTS = CRDC / "CRDC-CCRD-2020-FOR-DDR-ElementV2-eng.csv"

SEO_STRUCTURE = CRDC / "CRDC-CCRD-2020-SEO-OSE-StructureV2-eng.csv"
SEO_ELEMENTS = CRDC / "CRDC-CCRD-2020-SEO-OSE-ElementV2-eng.csv"

TOA_STRUCTURE = CRDC / "CRDC-CCRD-2020-TOA-TDA-StructureV2-eng.csv"

OUTPUT = CRDC / "crdc.json"


# -----------------------------
# HELPERS
# -----------------------------

def read_csv(path):

    print("Reading:", path)

    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if rows:
        print("Columns:", list(rows[0].keys()))

    return rows



def find_column(row, possibilities):

    for key in row.keys():

        lower = key.lower().replace("_", " ")

        for p in possibilities:

            if p in lower:
                return key

    return None



def clean(value):

    if value is None:
        return ""

    return value.strip()



# -----------------------------
# CLASSIFICATION PARSER
# -----------------------------

def parse_structure(path):

    rows = read_csv(path)

    if not rows:
        return {}

    sample = rows[0]


    code_col = find_column(
        sample,
        [
            "code",
            "identifier",
            "id"
        ]
    )


    title_col = find_column(
        sample,
        [
            "class title",
            "title",
            "name",
            "description"
        ]
    )


    level_col = find_column(
        sample,
        [
            "level"
        ]
    )


    parent_col = find_column(
        sample,
        [
            "parent"
        ]
    )


    print(
        "Detected columns:",
        {
            "code": code_col,
            "title": title_col,
            "level": level_col,
            "parent": parent_col
        }
    )


    result = {}


    for row in rows:

        code = clean(row.get(code_col))

        if not code:
            continue


        result[code] = {

            "title": clean(row.get(title_col)),

            "level": clean(row.get(level_col)),

            "parent": clean(row.get(parent_col)),

            "keywords": []

        }


    print("Loaded", len(result), "records")

    return result



# -----------------------------
# ELEMENT PARSER
# -----------------------------

def parse_elements(path, lookup):

    rows = read_csv(path)

    if not rows:
        return


    sample = rows[0]


    code_col = find_column(
        sample,
        [
            "code"
        ]
    )


    description_col = find_column(
        sample,
        [
            "element description",
            "description"
        ]
    )


    type_col = find_column(
        sample,
        [
            "element type label",
            "type"
        ]
    )


    print(
        "Element columns:",
        {
            "code": code_col,
            "description": description_col,
            "type": type_col
        }
    )


    count = 0


    for row in rows:

        code = clean(row.get(code_col))

        description = clean(row.get(description_col))

        element_type = clean(row.get(type_col))


        if code not in lookup:
            continue


        if not description:
            continue


        # Ignore exclusions
        if "exclusion" in element_type.lower():
            continue


        lookup[code]["keywords"].append(description)

        count += 1


    print("Added", count, "elements")



# -----------------------------
# COMPUTE HIERARCHY PATH
# -----------------------------

def add_paths(lookup):


    def get_path(code):

        path = []

        current = code


        while current:

            item = lookup.get(current)

            if not item:
                break


            title = item.get("title")

            if title:
                path.insert(0, title)


            current = item.get("parent")


        return path



    for code, item in lookup.items():

        item["path"] = get_path(code)



# -----------------------------
# MAIN
# -----------------------------

def main():

    output = {

        "for": {},

        "seo": {},

        "toa": {}

    }


    print("\nLoading FOR structure...")

    output["for"] = parse_structure(
        FOR_STRUCTURE
    )

    add_paths(
        output["for"]
    )


    print("\nLoading FOR elements...")

    parse_elements(
        FOR_ELEMENTS,
        output["for"]
    )


    print("\nLoading SEO structure...")

    output["seo"] = parse_structure(
        SEO_STRUCTURE
    )

    add_paths(
        output["seo"]
    )


    print("\nLoading SEO elements...")

    parse_elements(
        SEO_ELEMENTS,
        output["seo"]
    )


    print("\nLoading TOA structure...")

    output["toa"] = parse_structure(
        TOA_STRUCTURE
    )

    add_paths(
        output["toa"]
    )


    print("\nWriting JSON...")


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )


    print()
    print("Created:")
    print(OUTPUT)



if __name__ == "__main__":

    main()