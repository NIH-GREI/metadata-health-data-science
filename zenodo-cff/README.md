# Zenodo CFF

## Overview
We want to create a proof-of-concept to make it easier for Zenodo users to populate new records with metadata such as:

- ROR names and ROR IDs
- Creators/contributors with ORCID iDs AND affiliations with ROR IDs
- References (relationships to articles, software, etc)
- License
- Funding

We will create a Python script that imports a `.cff` file for the metadata and `.zip` for data if present.

## Notes
- The current version of CFF doesn’t support ROR, but it looks like [ROR in affiliations is on dev](https://github.com/citation-file-format/citation-file-format/pull/523/files#diff-c691faae636a91cb28b95c3e0ff9b17c654b01dcf288a9a3b03d7624f06cd847) and will be supported soon(?) 
- CFF also doesn’t currently support funding references, but there is an [active issue](https://github.com/citation-file-format/citation-file-format/issues/491) that someone appears to be taking forward.
- CFF also doesn’t currently support contributor roles, but it appears that [the contributors field will be added in 1.3.0 release](https://github.com/citation-file-format/citation-file-format/issues/84).
    - [Code for contributors implementation](https://github.com/citation-file-format/citation-file-format/pull/439/files)
    - CFF Contributor roles discussion: [Record contributor roles/contribution types](https://github.com/citation-file-format/citation-file-format/issues/112)

## To Do
- Create example CFF file for datasets with ideal metadata populated
    - ROR names and ROR IDs
    - Creators/contributors with ORCID iDs AND affiliations with ROR IDs
    - References (relationships to articles, software, etc)
    - License
- Create Python script to import `.cff` file and .zip (if present)
- Add funding
- Crosswalk CFF to Zenodo metadata JSON
    - Should already exist somewhere due to current Zenodo/Github integration
- Script to create new Zenodo draft record from CFF via Zenodo API
    - Just for proof of concepts - this would ideally be done automatically in the UI or via a CFF upload 

## Example from ROR Data Upload
- [Zenodo record](https://zenodo.org/records/14728473)
- [JSON](https://zenodo.org/records/14728473/export/json)
- [CFF](https://zenodo.org/records/14728473/export/cff)

## References:
- [CFF format info & file generator](https://citation-file-format.github.io)
- How to [create a .cff file](https://book.the-turing-way.org/communication/citable/citable-cff.html)
- [CFF file format schema guide: Fields](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md#index)
- Tools that [work with .cff files](https://github.com/citation-file-format/citation-file-format#tools-to-work-with-citationcff-files-wrench) 
