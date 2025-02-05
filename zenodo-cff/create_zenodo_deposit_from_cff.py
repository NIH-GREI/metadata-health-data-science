import argparse
import json
import os
import requests
import yaml
from zipfile import ZipFile, ZIP_DEFLATED


ZENODO_API_URL_SANDBOX = "https://sandbox.zenodo.org/api/"
ZENODO_API_URL_PROD = "https://zenodo.org/api/"
ZENODO_API_URL = ""
ZENODO_TOKEN = ""
HEADERS = {"Content-Type": "application/json"}


def upload_file_zenodo(input_file, zenodo_record):
    print("Uploading data file {input_file}")
    deposition_id = zenodo_record["id"]
    data = {"name": os.path.split(input_file)[1]}
    files = {"file": open(input_file, "rb")}

    try:
        r = requests.post(
            ZENODO_API_URL + "deposit/depositions/%s/files" % deposition_id,
            params={"access_token": ZENODO_TOKEN},
            data=data,
            files=files,
        )
        r.raise_for_status()
        if r.status_code == 201:
            print(f"File {r.json()['filename']} uploaded successfully")
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)


def create_zenodo_deposit(zenodo_metadata_json, inputfile):
    # Create Zenodo deposit draft and add metadata
    print("Creating new Zenodo deposit")
    try:
        # headers = {"Content-Type": "application/json"}
        r = requests.post(
            ZENODO_API_URL + "deposit/depositions",
            params={"access_token": ZENODO_TOKEN},
            json={},
        )
        r.raise_for_status()
        if r.status_code == 201:
            deposition_id = r.json()["id"]

        r = requests.put(
            ZENODO_API_URL + "deposit/depositions/%s" % deposition_id,
            params={"access_token": ZENODO_TOKEN},
            data=json.dumps(zenodo_metadata_json),
            headers=HEADERS,
        )
        r.raise_for_status()
        zenodo_record = r.json()

    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return zenodo_record


def get_json_from_citation_file(citation_file):
    # Convert CFF file to Zenodo JSON format
    with open(citation_file) as stream:
        try:
            citation_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    creators = []
    for author in citation_data["authors"]:
        creator = {}
        if "orcid" in author:
            creator["orcid"] = author["orcid"]
        if "affiliation" in author:
            creator["affiliation"] = author["affiliation"]
        if "given-names" in author:
            creator["name"] = author["family-names"] + ", " + author["given-names"]
        else:
            creator["name"] = author["family-names"]
        creators.append(creator)

    zenodo_metadata_json = {
        "metadata": {
            "title": citation_data["title"],
            "upload_type": "poster",  # citation_data['type']
            "description": citation_data["abstract"],
            "creators": creators,
            "publication_date": citation_data["date-released"],
        }
    }

    # TODO: Match https://github.com/zenodo/zenodo-rdm/blob/master/site/zenodo_rdm/github/schemas.py

    return zenodo_metadata_json


def get_citation_file(input_file):
    citation_file = None
    extension = os.path.splitext(input_file)[1]
    # If file input is zip, get CFF file from zipfile
    if extension == ".zip":
        with ZipFile(input, "r") as zf:
            cff_files = [f for f in zf.namelist() if ".cff" in f]
            if len(cff_files) == 1:
                citation_file = zf.extract(cff_files[0])
    # If file input is cff, return file
    if extension == ".cff":
        citation_file = input_file
    return citation_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--inputfile",
        type=str,
        help="Path to zip file containing dataset and CFF citation file",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--zenodoenv",
        type=str,
        choices=["prod", "sandbox"],
        required=True,
        help="Zenodo environment",
    )
    args = parser.parse_args()

    global ZENODO_API_URL
    global ZENODO_API_URL_PROD
    global ZENODO_TOKEN

    if args.zenodoenv == "prod":
        ZENODO_API_URL = ZENODO_API_URL_PROD
        ZENODO_TOKEN = os.environ["ZENODO_TOKEN_PROD"]
    else:
        ZENODO_API_URL = ZENODO_API_URL_SANDBOX
        ZENODO_TOKEN = os.environ["ZENODO_TOKEN_SANDBOX"]

    if os.path.exists(args.inputfile):
        citation_file = get_citation_file(args.inputfile)
        if citation_file:
            zenodo_metadata_json = get_json_from_citation_file(citation_file)
            zenodo_record = create_zenodo_deposit(zenodo_metadata_json, args.inputfile)
            print(
                f"New Zenodo record created: {zenodo_record['links']['latest_draft_html']}"
            )
            if zenodo_record and os.path.splitext(args.input_file)[1] == ".zip":
                # If input file is zip, assume it is the data file and add upload
                file_upload = upload_file_zenodo(args.input_file, zenodo_record)
                print(f"New Zenodo file upload created: {file_upload['links']['self']}")
        else:
            print(
                f"Could not create Zenodo record. No .cff file or multiple .cff files found in input file {args.inputfile}."
            )

    else:
        raise Exception(
            "Dump file name, previous version record or release notes could not be found"
        )


if __name__ == "__main__":
    main()
