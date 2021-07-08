## Log Export 

This utility lets you execute DQL and bulk export the results from the entire specified duration in JSON or CSV format.


## Usage

`log_export.py [-h] [-q QUERY] [-sid SCOPE_ID] [-ft FILE_TYPE] [-no_scroll NO_SCROLL]`

    optional arguments: 

    -h, --help  show this help message and exit

    -q QUERY, --QUERY QUERY  DQL query 

    -sid SCOPE_ID, --SCOPE_ID SCOPE_ID  scope_id. [default:default]
  
    -ft FILE_TYPE, --FILE_TYPE FILE_TYPE output file format. (json/csv) [default:json]

    -no_scroll, --NO_SCROLL to run query with out scroll. [default:true]

## Connection Parameters

This utility requires you DNIF Console IP and a <a href="https://docs.dnif.it/docs/manage-token">Token</a> to function.

You'll be prompted to enter these values the first time you run this script.

We cache these values for you in a config.yaml file to save on time and efforts.
        

## Note regarding Limit

    limit value is used as page size.
    limit 1000 will pull all events in the specified duration - but 1000 records at a time.

## Examples

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000'`

`python3 log_export.py --QUERY '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000'`

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' -sid Default`

`python3 log_export.py --QUERY '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' --SCOPE_ID Default`

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' -sid Default -ft json`

`python3 log_export.py --QUERY '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' --SCOPE_ID Default --FILE_TYPE csv`

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' -no_scroll`

`python3 log_export.py -q '_fetch * from event where $Stream=FIREWALL AND $Duration=1m limit 1000' --NO_SCROLL`