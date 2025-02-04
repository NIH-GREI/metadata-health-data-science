import argparse
import json
import os
import requests

ZENODO_API_URL_SANDBOX = "https://sandbox.zenodo.org/api/"
ZENODO_API_URL_PROD = "https://zenodo.org/api/"
ZENODO_API_URL = ""
ZENODO_TOKEN = ""
HEADERS = {"Content-Type": "application/json"}


def update_metadata(version_url, release_data):
    print("Updating metadata")
    try:
        r = requests.get(version_url, params={'access_token': ZENODO_TOKEN})
        r.raise_for_status()
        metadata = r.json()['metadata']
        related_ids = metadata['related_identifiers']
        related_ids.append({'identifier': release_data['previous_version_doi'], 'relation': 'isNewVersionOf', 'resource_type': 'dataset', 'scheme': 'doi'})
        metadata['publication_date'] = release_data['filename'].split('-', 1)[1].split('-ror-data.zip')[0]
        metadata['version'] = release_data['filename'].split('-', 1)[0]
        metadata['description'] = format_description(release_data)
        metadata['related_identifiers'] = related_ids
        updated_metadata = {'metadata': metadata}
        try:
            r = requests.put(version_url, params={'access_token': ZENODO_TOKEN}, data=json.dumps(updated_metadata), headers=HEADERS)
            r.raise_for_status()
            if r.status_code == 200:
                "Metadata updated successfully"
        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def publish_version(version_url):
    print("Publishing new version")
    try:
        r = requests.post(version_url + '/actions/publish', params={'access_token': ZENODO_TOKEN})
        r.raise_for_status()
        if r.status_code == 202:
            print("Data dump published successfully!")
            print("DOI is " + r.json()['doi'])
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def upload_new_file(version_url, release_data):
    print("Uploading new file")
    data = {'name': release_data['filename']}
    files = {'file': open(DUMP_FILE_DIR + release_data['filename'], 'rb')}
    try:
        r = requests.post(version_url + '/files', params={'access_token': ZENODO_TOKEN}, data=data, files=files)
        r.raise_for_status()
        if r.status_code == 201:
            print("File " + r.json()['filename'] + " uploaded successfully")
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)


def create_zenodo_version(release_data):
    print("Creating new Zenodo version")
    id = release_data['previous_version_doi'].rsplit(".", 1)[1]
    try:
        r = requests.post(ZENODO_API_URL + 'deposit/depositions/' + id + '/actions/newversion', params={'access_token': ZENODO_TOKEN})
        r.raise_for_status()
        if r.status_code == 201:
            new_version_url = r.json()['links']['latest_draft']
            print("New version created. URL is " + new_version_url)
            existing_files = delete_existing_files(new_version_url)
            if len(existing_files) == 0:
                new_file = upload_new_file(new_version_url, release_data)
                if new_file['filename'] == release_data['filename']:
                    update_metadata(new_version_url, release_data)
                    publish_version(new_version_url)
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def create_zenodo_deposit(zenodo_metadata_json, zipfile):
    #Create Zenodo deposit draft and add metadata
    zenodo_record = None
    #Create upload
    #Create metadata
    return zenodo_record


 def get_json_from_citation_file():
    #Convert CFF file to Zenodo JSON format
    zenodo_metadata_json = None
    return zenodo_metadata_json


def get_citation_file(zipfile):
    #Find CFF file in zipfile
    citation_file = None
    return citation_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', '--zipfile', type=str, help='Path to zip file containing dataset and CFF citation file', required=True)
    parser.add_argument('-e', '--zenodoenv', type=str, choices=['prod', 'sandbox'], required=True, help='Zenodo environment')
    args = parser.parse_args()

    global ZENODO_API_URL
    global ZENODO_API_URL_PROD
    global ZENODO_TOKEN

    if args.zenodoenv == 'prod':
        ZENODO_API_URL = ZENODO_API_URL_PROD
        ZENODO_TOKEN = os.environ['ZENODO_TOKEN_PROD']
    else:
        ZENODO_API_URL = ZENODO_API_URL_SANDBOX
        ZENODO_TOKEN = os.environ['ZENODO_TOKEN_SANDBOX']

    if os.path.exists(args.zipfile):
        citation_file = get_citation_file(zipfile)
        if citation_file:
            zenodo_metadata_json = get_json_from_citation_file(citation_file)
            zenodo_record = create_zenodo_deposit(zenodo_metadata_json, zipfile)
            print(f"New Zenodo record created: {zenodo_record}")
        else:
            print(f"Could not create Zenodo record. No CITATION.cff file found in zip file {zipfile}.")

    else:
        raise Exception("Dump file name, previous version record or release notes could not be found")

if __name__ == "__main__":
    main()
