# NIH RePORTER - DataCiteDOI Relationship Analysis

## Data Flow Overview

For input, we start with the NIH RePORTER publication link tables, which provide mappings between PubMed IDs (PMIDs) and NIH project numbers. These tables are downloaded and concatenated into a single dataset.

Using `parse_pubmed_xml.py`, we process PubMed XML files to extract non-PubMed article identifiers, particularly DOIs, creating a mapping between PMIDs and their associated identifiers. 

These two datasets (the concacatenated RePORTER data and the article identifiers extracted from PubMed) are then combined using `merge_pmid_id_mapping_reporter_file.py`, which creates a mapping between NIH funder projects, PMIDs, and their corresponding DOIs.

The merged dataset feeds into `find_overlapping_reporter_datacite_dois.py`, which matches these DOIs against DataCite records from the public data file. This allows to identify relationships between NIH-funded publications and various research outputs registered with DataCite.