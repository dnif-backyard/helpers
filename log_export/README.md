**Log Export** 

This utility lets you execute DQL and export the results in JSON or CSV format.


**Usage**

`log_export.py [-h] [-q QUERY] [-sid SCOPE_ID] [-ft FILE_TYPE]`

    optional arguments: 

    -h, --help  show this help message and exit

    -q QUERY, --QUERY QUERY  DQL query 

    -sid SCOPE_ID, --SCOPE_ID SCOPE_ID  scope_id. [default:default]
  
    -ft FILE_TYPE, --FILE_TYPE FILE_TYPE output file format. (json/csv) [default:json]


**Note regarding Limit**

    limit value is used as page size.
    limit 1000 will pull all events in the specified duration - but 1000 records at a time.

**Examples**

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000'`

`python3 log_export.py --QUERY '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000'`

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' -sid Default`

`python3 log_export.py --QUERY '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' --SCOPE_ID Default`

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' -sid Default -ft json`

`python3 log_export.py --QUERY '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' --SCOPE_ID Default --FILE_TYPE csv`
