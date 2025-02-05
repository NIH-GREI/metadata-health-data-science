import argparse
import csv


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f1', '--file_1', required=True)
    parser.add_argument('-f2', '--file_2', required=True)
    parser.add_argument('-o', '--output', required=True)
    return parser.parse_args()


def read_csv_file_1(file_path):
    rows = []
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            rows.append(row)
    return rows


def read_csv_file_2(file_path):
    b_dict = {}
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            pmid = row['pmid']
            if pmid not in b_dict:
                b_dict[pmid] = []
            b_dict[pmid].append((row['mapped_id_type'], row['mapped_id']))
    return b_dict


def reconcile_data(file_1_rows, file_2_dict):
    merged = []
    for row_a in file_1_rows:
        pmid_a = row_a['PMID']
        if pmid_a in file_2_dict:
            for mt, mv in file_2_dict[pmid_a]:
                merged.append(
                    {'PMID': pmid_a, 'PROJECT_NUMBER': row_a['PROJECT_NUMBER'], 'mapped_id_type': mt, 'mapped_id': mv})
        else:
            merged.append(
                {'PMID': pmid_a, 'PROJECT_NUMBER': row_a['PROJECT_NUMBER'], 'mapped_id_type': ', 'mapped_id': '})
    return merged


def write_output_csv(merged_rows, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['PMID', 'PROJECT_NUMBER', 'mapped_id_type', 'mapped_id'])
        writer.writeheader()
        for row in merged_rows:
            writer.writerow(row)


def main():
    args = parse_arguments()
    a = read_csv_file_1(args.file_1)
    b = read_csv_file_2(args.file_2)
    m = reconcile_data(a, b)
    write_output_csv(m, args.output)


if __name__ == '__main__':
    main()
