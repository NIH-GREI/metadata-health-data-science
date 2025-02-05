# Find Overlapping RePORTER - DataCite DOIs

Script to find overlap in DOIs between RePORTER publication and related items in DataCite (`.jsonl.gz` format).

## Installation

```bash
pip install orjson pyahocorasick
```

## Usage

```bash
python find_overlapping_reporter_datacite_dois.py -m MAPPING.csv -i DATACITE_DIR -o OUTPUT.csv
```

## Arguments

- `-m, --mapping-csv`: Input CSV with columns: PMID, PROJECT_NUMBER, mapped_id_type, mapped_id
- `-i, --input-dir`: Directory containing DataCite records in `.jsonl.gz` format
- `-o, --output-csv`: Output CSV file path

## Output Format

CSV with columns:
- `pmid`: PubMed ID
- `project_number`: Project identifier
- `mapped_id_type`: Type of identifier (always 'doi')
- `mapped_id`: DOI value
- `matched_datacite_doi`: Matching DataCite DOI
- `matched_relation_type`: Relation type from DataCite
- `matched_resource_type`: Resource type from DataCite