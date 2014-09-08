Mapusaurus
=======

## Introduction

Just some notes on the more complex APIs we have. Most of the APIs are 
reasonably straightforward. 

## batch

To limit the number of open HTTP requests, we have a "batch" API, which allows
you to collect multiple requests and response in a single cycle. 

URL: '.../batch?endpoint=minority&county=11222&county=11223'
INPUT:

* endpoint - One of `minority` or `loanVolume`; indicates what type of results
  you want back. Can be repeated to get both types of data
* county - The five-digit FIPS code for a county. Can be repeated to query
  multiple counties

OUTPUT:
```json
{
    "minority": {"1122233333": ...}
    "loanVolume": {"1122233333": ...}
}
```

## Institution Search

Results for institution search can be returned as both nicely styled markup
and as JSON. Use the 'Accept: application/json' header for JSON.

URL: '.../institutions/search?q=search+term'
INPUT:

* q - search term. Can be either a phrase (searches the institution name) or
  an 11-digit lender id (agency id + ffiec id)
* auto - if present, search completes using an ngram field (i.e. partial
  match). Most useful for auto-complete fields

OUTPUT:
```json
{
    "institutions": [
        {"id": ..., "name": ..., ....}
    ]
}
```
