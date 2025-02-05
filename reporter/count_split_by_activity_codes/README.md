# Activity Code Analyzer

Script to analyze and categorize RePORTER/DataCite Related ITEM DOI overlap by NIH activity codes.

## Usage

```bash
python count_split_by_activity_codes.py -a ACTIVITY_CODES.csv -w WORKS.csv -o OUTPUT_DIR [-v]
```

## Arguments

- `-a, --activity_codes`: CSV file containing activity code definitions (columns: Activity Code, Funding Category, Title, Description)
- `-w, --works`: CSV file containing funded works data with project_number column
- `-o, --output`: Output directory for generated files
- `-v, --verbose`: Enable verbose output

## Output Structure

```
output_dir/
├── statistics.csv                # Summary statistics for all codes
├── A/                           # Directory for 'A' activity codes
│   ├── all_A_entries.csv       # All entries with 'A' codes
│   └── A01/                    # Specific activity code directory
│       └── A01_entries.csv     # Entries for A01 code
└── B/                          # Directory for 'B' activity codes
    └── ...
```

### Statistics CSV Columns
- `level`: 'letter' or 'full' code level
- `code`: Activity code
- `count`: Number of entries
- `title`: Program title
- `category`: Funding category
- `description`: Program description