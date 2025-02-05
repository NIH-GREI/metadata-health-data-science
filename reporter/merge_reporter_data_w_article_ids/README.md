# Merge Article IDs w/ RePORTER data

Script to merge RePORTER project data with article identifiers extracted from PubMed files.

## Usage

```bash
python merge_reporter_data_w_article_ids.py -f1 FIRST_FILE.csv -f2 SECOND_FILE.csv -o OUTPUT_FILE.csv
```

## Arguments

- `-f1, --file_1`: First input CSV (RePORTER data) containing PMID and PROJECT_NUMBER columns f
- `-f2, --file_2`: Second input CSV (Article IDs extracted from PubMed data) containing pmid, mapped_id_type, and mapped_id columns
- `-o, --output`: Output CSV file path

## Output Format

CSV with columns:
- `PMID`: PubMed ID
- `PROJECT_NUMBER`: Project identifier from first file
- `mapped_id_type`: Type of external identifier from second file
- `mapped_id`: External identifier value from second file

For PMIDs not found in the second file, `mapped_id_type` and `mapped_id` will be empty.