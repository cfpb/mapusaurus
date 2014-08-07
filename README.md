Mapusaurus
=======

## Description 

This small piece of software loads institution data from HMDA, and maps HMDA
reporter ids to National Information Center ids for easy identification. 


## Data

The data you can load is:

* HMDA Transmittal Sheet
* HMDA Reporter Panel 

Both are available from the FFIEC. 

Here are the 2012 files:

Transmittal sheet:
http://www.ffiec.gov/hmdarawdata/OTHER/2012HMDAInstitutionRecords.zip

Reporter panel:
http://www.ffiec.gov/hmdarawdata/OTHER/2012HMDAReporterPanel.zip

## Requirements 

This currently uses: 
Django 1.6
Python 3.2.3

Postgres 9.1.13
(You could likely use other databases, I just haven't tested them)

There's also a requirements.txt file in the repository root directory.  


## Loading the data

This uses South. 

To create the tables, you need to run:

```
    python manage.py migrate respondants
```

There's also a fixture that you need to load some information from:

```
    python manage.py loaddata agency
```

This loads static regulator agency data. 

Download the two transmittal sheet and reporter panel flat files. 

There are two management commands that will load data, and need to be run 
in the following order:

``` 
1. python manage.py load_transmittal <path/to/transmittal_sheet>
2. python manage.py load_reporter_panel <path/to/reporter_panel>
```

## GEO

The 'geo' application requires GeoDjango and PostGIS. Follow the instructions
for installing GeoDjango. 

Here are some separate instructions for running the geo application. 

```
    python manage.py migrate geo
```

Currently, we load census tract, county, and CBSA files. You can download them 
from the census' FTP site:

```
ftp://ftp2.census.gov/geo/tiger/TIGER2013/TRACT/
ftp://ftp2.census.gov/geo/tiger/TIGER2013/COUNTY/
ftp://ftp2.census.gov/geo/tiger/TIGER2013/CBSA/
```

This is how you load the data:

```
    # This example only loads census tracts from IL (FIPS code: 17); repeat 
    # for other states as needed
    python manage.py load_geos_from /path/to/tl_2013_17_tract.shp
    python manage.py load_geos_from /path/to/tl_2013_us_county.shp
    python manage.py load_geos_from /path/to/tl_2013_us_cbsa.shp
```

These import scripts are set up to update geos in place -- no need to delete
records manually.

Once census tracts and counties are loaded, run the following command to
associate census tracts with their CBSAs.

```
    python manage.py set_tract_csa_cbsa
```


## Census Data

The 'censusdata' app loads census data to the census tracts found in the 'geo'
application. As such, 'censusdata' relies on 'geo'.

First, run migrate to create the appropriate tables

```
    python manage.py migrate censusdata
```

You'll then want to import census data related to the tracts you've loaded
while setting up the 'geo' app. Go to
```
http://www2.census.gov/census_2010/04-Summary_File_1/
```
and select the state you care about. Download the associated `*.sf1.zip` file,
which you should then unzip.

Loading the data looks like this:
```
    python manage.py load_summary_one /path/to/XXgeo2010.sf1
```

Warning: currently, data will not be updated in place; to re-import, you'll
need to delete everything from the `censusdata_census2010*` tables.


## HMDA

The 'hmda' app loads HMDA data to the census tracts found in the 'geo'
application. As such, 'hmda' relies on 'geo'. In fact, 'hmda' will only store
data for states that are loaded via the 'geo' app.

First, run migrate to create the appropriate tables

```
    python manage.py migrate hmda
```

Next, download a flat file representing all of the HMDA LAR data:
```
http://www.ffiec.gov/hmda/hmdaflat.htm
```
and download the zip file. Unzip it and then:
```
    python manage.py load_hmda /path/to/2012HMDALAR\ -\ National.csv
```

Note that this process takes several minutes (though you will receive progress
notifications). This import can be ran repeatedly (if additional geos are
added later, for example).

Warning: At the moment, the import assumes a single year of information.
That's a todo.


## Styles

While the base application attempts to appear "acceptable", you will likely
wish to provide your own icons, colors, etc. We provide an example app
(`cfpbstyle`) which you can modify directly or copy into a separate Django
app. If you go the latter route, remember to activate your new app and
deactivate the CFPB style.
