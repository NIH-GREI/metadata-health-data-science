#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description='Analyze relation types from publication data CSV file')
    parser.add_argument('-i', '--input', required=True, type=str,
                        help='Path to input CSV file')
    parser.add_argument('-o', '--output', required=True, type=str,
                        help='Path to output CSV file')
    parser.add_argument('--delimiter', default=',', type=str,
                        help='CSV delimiter (default: tab)')
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        parser.error(f"Input file not found: {args.input}")
    output_path = Path(args.output)
    if not output_path.parent.exists():
        parser.error(f"Output directory does not exist: {output_path.parent}")
    return args


def load_data(file_path, delimiter):
    try:
        df = pd.read_csv(file_path, delimiter=delimiter)
        required_cols = ['matched_relation_type']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        return df
    except pd.errors.EmptyDataError:
        raise ValueError("Input file is empty")
    except pd.errors.ParserError:
        raise ValueError(
            "Failed to parse input file - check delimiter and format")


def calculate_relation_counts(data):
    data['matched_relation_type'] = data['matched_relation_type'].replace(
        '', pd.NA)
    counts = data['matched_relation_type'].value_counts(dropna=False)
    if pd.NA in counts.index:
        counts = counts.rename({pd.NA: 'MISSING'})
    return counts


def export_results(counts, output_path):
    try:
        results_df = counts.reset_index()
        results_df.columns = ['matched_relation_type', 'count']
        results_df = results_df.sort_values('count', ascending=False)
        results_df.to_csv(output_path, index=False)
        return True
    except (PermissionError, OSError) as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return False


def main():
    try:
        args = parse_args()
        print(f"Loading data from {args.input}")
        data = load_data(args.input, args.delimiter)
        print("Calculating relation type frequencies")
        counts = calculate_relation_counts(data)
        print(f"Exporting results to {args.output}")
        if export_results(counts, args.output):
            print("Analysis complete")
            return 0
        else:
            print("Failed to write output file", file=sys.stderr)
            return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
