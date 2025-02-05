import os
import csv
import gzip
import shutil
import tempfile
import argparse
from lxml import etree
from multiprocessing import Pool


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract non-pubmed ArticleIds from PubMed XML (.xml.gz) files, excluding references."
    )
    parser.add_argument('-i', '--input_dir', required=True,
                        help="Directory containing the .xml.gz files.")
    parser.add_argument('-o', '--output_csv', required=True,
                        help="Path to the output CSV file.")
    parser.add_argument('-p', '--processes', type=int, default=1,
                        help="Number of parallel processes. Default=1 (no parallelism).")
    return parser.parse_args()


def is_in_reference(elem):
    """Check if the element is inside a <Reference> tag to avoid pulling in cite DOIs vs that for the work"""
    parent = elem.getparent()
    while parent is not None:
        if parent.tag == 'Reference':
            return True
        parent = parent.getparent()
    return False


def extract_ids_from_pubmed_article(article_elem):
    try:
        pmid_elem = article_elem.find('.//PMID')
        if pmid_elem is None or not pmid_elem.text:
            return
        pmid = pmid_elem.text.strip()
        
        for article_id in article_elem.findall('.//ArticleId'):
            if is_in_reference(article_id):
                continue
            id_type = article_id.get('IdType', '').strip().lower()
            if id_type and id_type != 'pubmed':
                mapped_id = (article_id.text or '').strip()
                yield (pmid, id_type, mapped_id)
    except Exception as e:
        print(f"Error processing article: {e}")


def parse_pubmed_xml(filepath, tmp_filepath):
    with open(tmp_filepath, 'w', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        with gzip.open(filepath, 'rb') as f:
            context = etree.iterparse(f, events=('end',), tag='PubmedArticle')
            
            for event, elem in context:
                try:
                    for row in extract_ids_from_pubmed_article(elem):
                        writer.writerow(row)
                    # Memory cleanup
                    elem.clear()
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]
                except Exception as e:
                    print(f"Error processing element: {e}")
                finally:
                    elem = None
            del context
    return tmp_filepath


def process_single_file(filepath):
    tmp_handle, tmp_name = tempfile.mkstemp(suffix='.tsv', prefix='pubmed-')
    os.close(tmp_handle)
    try:
        parse_pubmed_xml(filepath, tmp_name)
        return tmp_name
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None


def main():
    args = parse_args()
    input_dir = args.input_dir
    output_csv = args.output_csv
    processes = args.processes

    all_files = [
        os.path.join(input_dir, fn)
        for fn in os.listdir(input_dir)
        if fn.endswith('.xml.gz')
    ]
    if not all_files:
        print(f"No .xml.gz files found in {input_dir}")
        return

    try:
        if processes > 1:
            with Pool(processes=processes) as pool:
                tmp_files = pool.map(process_single_file, all_files)
        else:
            tmp_files = [process_single_file(f) for f in all_files]

        tmp_files = [f for f in tmp_files if f is not None]

        with open(output_csv, 'w', encoding='utf-8') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(['pmid', 'mapped_id_type', 'mapped_id'])
            for tmp_file in tmp_files:
                try:
                    with open(tmp_file, 'r', encoding='utf-8') as in_f:
                        shutil.copyfileobj(in_f, f_out)
                    os.remove(tmp_file)
                except Exception as e:
                    print(f"Error merging {tmp_file}: {e}")

        print(f"Done. Output written to {output_csv}")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == '__main__':
    main()