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

