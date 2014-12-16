Mapusaurus
=======

## Introduction

Just some notes on the more complex APIs we have. Most of the APIs are 
reasonably straightforward. 


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
