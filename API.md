Mapusaurus
=======

## Introduction

Just some notes on the more complex APIs we have. Most of the APIs are 
reasonably straightforward. 

## censusdata

The censusdata application adds a statistics API which gives a bit more 
power and flexibility when requesting data about census tracts. 

URL: '.../census/statistics'

You can POST to this URL with a JSON structure that contains the request
parameters. Here's an example:

```
{
    "county_fips": "031",
    "fields": [
        {
            "bins": [
                0,
                0.5,
                0.8,
                1.01
            ],
            "name": "non_hisp_white_only_perc",
            "type": "binned"
        },
        {
            "name": "non_hisp_white_only_perc",
            "type": "raw"
        }
    ],
    "state_fips": "17"
}
```

The bins are specified as in:
http://docs.scipy.org/doc/numpy/reference/generated/numpy.digitize.html with
right=False. 
