import csv
import sys
import gzip
import orjson
import logging
import argparse
import ahocorasick
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("large-scale-substring-match")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Match CSV-supplied DOIs (exact) against large .jsonl.gz DataCite records"
    )
    parser.add_argument('-m', '--mapping-csv', required=True,
                        help='Path to CSV of mappings (no header). Columns: PMID,PROJECT_NUMBER,mapped_id_type,mapped_id')
    parser.add_argument('-i', '--input-dir', required=True,
                        help='Directory containing .jsonl.gz DataCite records.')
    parser.add_argument('-o', '--output-csv', required=True,
                        help='Path to output CSV with match results.')
    return parser.parse_args()


def load_mappings(csv_path):
    out = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(
            f,
            fieldnames=["PMID", "PROJECT_NUMBER", "mapped_id_type", "mapped_id"]
        )
        for row in reader:
            if row["mapped_id_type"] and row["mapped_id_type"].strip().lower() == 'doi':
                out.append(row)
    return out


def build_aho_corasick_automaton(mappings):
    logger.info("Building trie for exact DOI matching...")
    A = ahocorasick.Automaton()
    valid_mappings = 0
    
    for row in mappings:
        if not row.get('mapped_id'):
            continue
        doi = row['mapped_id'].strip()
        if not doi:
            continue
        A.add_word(doi, (doi, row))
        valid_mappings += 1
    if valid_mappings == 0:
        raise ValueError("No valid DOIs found in mappings")
        
    A.make_automaton()
    logger.info(f"Built trie with {valid_mappings} DOIs.")
    return A


def iter_datacite_records(jsonl_gz_path, chunk_size=2**24):
    buffer = bytearray()
    try:
        with gzip.open(jsonl_gz_path, 'rb') as gz_file:
            while True:
                chunk = gz_file.read(chunk_size)
                if not chunk:
                    break
                buffer.extend(chunk)

                lines = buffer.split(b'\n')
                buffer = bytearray(lines.pop())

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield orjson.loads(line)
                    except orjson.JSONDecodeError as ex:
                        logger.warning(f"JSON decode error in {jsonl_gz_path}: {ex}")
            if buffer.strip():
                try:
                    yield orjson.loads(buffer.strip())
                except orjson.JSONDecodeError as ex:
                    logger.warning(f"JSON decode error (leftover) in {jsonl_gz_path}: {ex}")
    except Exception as e:
        logger.error(f"Error reading {jsonl_gz_path}: {e}")


def find_matches_in_record(record, automaton):
    results = []
    attrs = record.get('attributes', {})
    if attrs.get('state') != 'findable':
        return results
    datacite_doi = attrs.get('doi', '')
    if datacite_doi:
        for end_idx, (matched_doi, row_data) in automaton.iter(datacite_doi):
            start_idx = end_idx - len(matched_doi) + 1
            if start_idx == 0 and end_idx == len(datacite_doi) - 1:
                results.append({
                    "pmid": row_data['PMID'],
                    "project_number": row_data['PROJECT_NUMBER'],
                    "mapped_id_type": row_data['mapped_id_type'],
                    "mapped_id": matched_doi,
                    "matched_datacite_doi": datacite_doi,
                    "matched_relation_type": "Same",
                    "matched_resource_type": attrs.get('resourceType', {}).get('resourceTypeGeneral', '')
                })

    related_identifiers = attrs.get('relatedIdentifiers') or []
    for rid in related_identifiers:
        rid_value = str(rid.get('relatedIdentifier', '')).strip()
        relation_type = rid.get('relationType', '')
        resource_type = rid.get('resourceTypeGeneral', '')
        for end_idx, (matched_doi, row_data) in automaton.iter(rid_value):
            start_idx = end_idx - len(matched_doi) + 1
            if start_idx == 0 and end_idx == len(rid_value) - 1:
                results.append({
                    "pmid": row_data['PMID'],
                    "project_number": row_data['PROJECT_NUMBER'],
                    "mapped_id_type": row_data['mapped_id_type'],
                    "mapped_id": matched_doi,
                    "matched_datacite_doi": datacite_doi,
                    "matched_relation_type": relation_type,
                    "matched_resource_type": resource_type,
                })
    
    return results


def main():
    args = parse_arguments()
    logger.info(f"Loading mappings from {args.mapping_csv}...")
    all_mappings = load_mappings(args.mapping_csv)
    logger.info(f"Loaded {len(all_mappings)} total mappings (mapped_id_type='doi').")
    automaton = build_aho_corasick_automaton(all_mappings)
    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow([
            'pmid',
            'project_number',
            'mapped_id_type',
            'mapped_id',
            'matched_datacite_doi',
            'matched_relation_type',
            'matched_resource_type'
        ])
        input_dir = Path(args.input_dir)
        gz_files = list(input_dir.rglob('*.jsonl.gz'))
        if not gz_files:
            logger.warning(f"No .jsonl.gz files found in {input_dir}")
            sys.exit(0)
        total_matches = 0
        for gzfile in gz_files:
            logger.info(f"Processing {gzfile} ...")
            for record in iter_datacite_records(gzfile):
                match_rows = find_matches_in_record(record, automaton)
                if match_rows:
                    for row in match_rows:
                        writer.writerow([
                            row['pmid'],
                            row['project_number'],
                            row['mapped_id_type'],
                            row['mapped_id'],
                            row['matched_datacite_doi'],
                            row['matched_relation_type'],
                            row['matched_resource_type'],
                        ])
                    total_matches += len(match_rows)
        logger.info(f"Done. Total matches: {total_matches}")

    return 0


if __name__ == '__main__':
    sys.exit(main())