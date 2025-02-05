#!/usr/bin/env python3
import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Process funding program data and funded works.')
    parser.add_argument('-a', '--activity_codes', required=True,
                        help='Path to funding activity_codes CSV file')
    parser.add_argument('-w', '--works', required=True,
                        help='Path to funded works CSV file')
    parser.add_argument('-o', '--output', required=True,
                        help='Output directory path')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    args = parser.parse_args()
    if not os.path.exists(args.activity_codes):
        raise FileNotFoundError(f"Programs file not found: {args.activity_codes}")
    if not os.path.exists(args.works):
        raise FileNotFoundError(f"Works file not found: {args.works}")
    os.makedirs(args.output, exist_ok=True)
    return args


def load_program_data(filepath):
    activity_codes = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                activity_codes[row['Activity Code']] = {
                    'category': row['Funding Category'],
                    'title': row['Title'],
                    'description': row['Description']
                }
    except csv.Error as e:
        raise ValueError(f"Error parsing activity_codes CSV: {str(e)}")
    return activity_codes


def load_funded_works(filepath):
    works = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                works.append(row)
    except csv.Error as e:
        raise ValueError(f"Error parsing works CSV: {str(e)}")
    return works


def extract_activity_codes(funded_works):
    letter_codes = defaultdict(list)
    full_codes = defaultdict(list)
    for work in funded_works:
        project_num = work['project_number']
        if len(project_num) >= 3:
            activity_code = project_num[:3]
            letter = activity_code[0]
            letter_codes[letter].append(work)
            full_codes[activity_code].append(work)
    return letter_codes, full_codes


def generate_statistics(letter_codes, full_codes, program_data):
    letter_stats = []
    code_stats = []
    for letter, entries in sorted(letter_codes.items()):
        letter_stats.append({
            'level': 'letter',
            'code': letter,
            'count': len(entries),
            'title': f'All {letter} Programs',
            'category': 'Multiple',
            'description': f'Combined entries for all {letter} activity codes'
        })
    for code, entries in sorted(full_codes.items()):
        program_info = program_data.get(code, {
            'title': 'Unknown Program',
            'category': 'Unknown',
            'description': 'No program description available'
        })
        code_stats.append({
            'level': 'full',
            'code': code,
            'count': len(entries),
            'title': program_info['title'],
            'category': program_info['category'],
            'description': program_info['description']
        })
    return letter_stats + code_stats


def write_entries_to_file(filepath, entries, headers=None):
    if not entries:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        if headers is None:
            headers = entries[0].keys()
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(entries)


def create_file_structure(output_dir, letter_codes, full_codes, program_data):
    stats = generate_statistics(letter_codes, full_codes, program_data)
    stats_path = os.path.join(output_dir, 'statistics.csv')
    with open(stats_path, 'w', encoding='utf-8') as f:
        fieldnames = ['level', 'code', 'count',
                      'title', 'category', 'description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stats)
    for letter, entries in letter_codes.items():
        letter_dir = os.path.join(output_dir, letter)
        os.makedirs(letter_dir, exist_ok=True)
        write_entries_to_file(
            os.path.join(letter_dir, f'all_{letter}_entries.csv'),
            entries
        )
    for code, entries in full_codes.items():
        letter = code[0]
        code_dir = os.path.join(output_dir, letter, code)
        os.makedirs(code_dir, exist_ok=True)
        write_entries_to_file(
            os.path.join(code_dir, f'{code}_entries.csv'),
            entries
        )


def main():
    try:
        args = parse_arguments()
        if args.verbose:
            print("Loading program data...")
        program_data = load_program_data(args.activity_codes)
        if args.verbose:
            print("Loading funded works...")
        funded_works = load_funded_works(args.works)
        if args.verbose:
            print("Extracting activity codes...")
        letter_codes, full_codes = extract_activity_codes(funded_works)
        if args.verbose:
            print("Creating file structure...")
        create_file_structure(args.output, letter_codes,
                              full_codes, program_data)
        if args.verbose:
            print("Processing complete!")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
