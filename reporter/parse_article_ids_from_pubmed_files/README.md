# PubMed Data Article ID Extractor

Script to extract primary article identifiers from PubMed XML files (`.xml.gz`), excluding references those in references.


## Installation

```bash
pip install -r lxml
```

## Usage

```bash
python script.py -i INPUT_DIR -o OUTPUT_FILE.csv [-p NUM_PROCESSES]
```

## Arguments

- `-i, --input_dir`: Directory containing `.xml.gz` PubMed XML files
- `-o, --output_csv`: Output CSV file path
- `-p, --processes`: Number of parallel processes (default: 1)


## Output Format

CSV with columns:
- `pmid`: PubMed ID
- `mapped_id_type`: Type of external identifier
- `mapped_id`: External identifier value

