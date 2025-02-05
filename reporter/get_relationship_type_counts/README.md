# Count Relationship Types

Script to count relationship types from for RePORTER DataCite Overlap

## Usage

```bash
python get_relationship_type_counts.py -i INPUT.csv -o OUTPUT.csv [--delimiter DELIMITER]
```

## Arguments

- `-i, --input`: Input CSV file containing publication data with matched_relation_type column
- `-o, --output`: Output CSV file path for results
- `--delimiter`: CSV delimiter character (default: comma)

## Output Format

CSV with columns:
- `matched_relation_type`: Type of relationship
- `count`: Number of occurrences

Empty relation types are labeled as 'MISSING' in the output.