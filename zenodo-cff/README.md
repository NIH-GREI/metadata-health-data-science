# Zenodo CFF

This project aims to reduce work needed by researchers depositing data into generalist repositories in order to supply rich metadata by allowing depositors to submit metadata in a text file along with their dataset rather than filling out a form.

This approach utilizes [Citation File Format (CFF)](https://citation-file-format.github.io/), which is already used in the Zenodo/Github integration.

## Proposed workflow
1. Researcher creates a CFF text file with rich metadata (authors/contributors with ORCID IDs, affiliations with ROR IDs, etc)
2. Research incudes CFF file in the root of their datafile upload
3. Repository automatically parses CFF and populates metadata fields.
4. Repository registers DOI and sends corresponding metadata to DOI registration agency.

## Advatages of this approach
1. Text file can easily be created re-used by researchers, to avoid entering the same author, contributor, funding, etc data in repository upload forms for each data deposit.
2. CFF format is independently maintained and tooling exists to create/validate CFF files.
3. CFF format is repository-agnostic and could be implemented by multiple GREI respositories


## Notes
- The current version of CFF doesn’t support ROR, but it looks like [ROR in affiliations is on dev](https://github.com/citation-file-format/citation-file-format/pull/523/files#diff-c691faae636a91cb28b95c3e0ff9b17c654b01dcf288a9a3b03d7624f06cd847) and will be supported soon(?) 
- CFF also doesn’t currently support funding references, but there is an [active issue](https://github.com/citation-file-format/citation-file-format/issues/491) that someone appears to be taking forward.
- CFF also doesn’t currently support contributor roles, but it appears that [the contributors field will be added in 1.3.0 release](https://github.com/citation-file-format/citation-file-format/issues/84).
    - [Code for contributors implementation](https://github.com/citation-file-format/citation-file-format/pull/439/files)
    - CFF Contributor roles discussion: [Record contributor roles/contribution types](https://github.com/citation-file-format/citation-file-format/issues/112)

## To Do
### Current Work
- Create example CFF file for datasets with ideal metadata populated
    - Authors with ORCID IDs and affiliations with ROR names and ROR IDs
- Create crosswalk of CFF fields to Zenodo metadata JSON (based on existing Zenodo/Github crosswalk)
- Create Python script to import `.cff` file and .zip (if present)
- Script to create new Zenodo draft record from CFF via Zenodo API
    - Just for proof of concepts - this would ideally be done automatically in the UI or via a CFF upload
    - 
### Future Work
- Enhance CFF file example with funding, references (relationships to articles, software, etc), contributors/roles, etc
- Enhance CFF to Zenodo JSON crosswalk to include additional CFF fields

## Example from ROR Data Upload
- [Zenodo record](https://zenodo.org/records/14728473)
- [JSON](https://zenodo.org/records/14728473/export/json)
- [CFF](https://zenodo.org/records/14728473/export/cff)

## References:
- [CFF format info & file generator](https://citation-file-format.github.io)
- How to [create a .cff file](https://book.the-turing-way.org/communication/citable/citable-cff.html)
- [CFF file format schema guide: Fields](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md#index)
- Tools that [work with .cff files](https://github.com/citation-file-format/citation-file-format#tools-to-work-with-citationcff-files-wrench) 
