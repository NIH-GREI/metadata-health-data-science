# Script to get JSON from Zenodo

The script gets records from Zenodo API and saves them in a JSON file.

In order to run you'll need to create a secrets.py file following the secrets_example.py file
but with your Zenodo API token filled in.

## Prepare

```python
pip install -r requirements.txt
```

## Edit for the dates you want to get

Find the line like below and change to your date ranges.  It will aggregate
all records into the output file.

```python
ranges = [['2024-12-01', '2024-12-31'], ['2024-11-01', '2024-11-30']]
```

The reason for having more than one date range is that only 10,000 records
can be returned for a query from the Zenodo API, even with paging 100 at a time.

So, to get all records, ensure that your date ranges are small enough that
they return less than 10k records for each date range query.

## Run

```python
python zenodo_output.py
```

Output shows the date range and then each individual paged query to the API.

At the end, the output file is written like:

```python
Total records collected: 14729
Data saved to zenodo_records.json
done
```

Open the zenodo_records.json file to see the records.