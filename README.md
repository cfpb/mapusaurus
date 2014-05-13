Ventura
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


## Loading the data

Download the two transmittal sheet and reporter panel flat files. 

There are two management commands that will load data, and need to be run 
in the following order:

1. python manage.py load_transmittal <path/to/transmittal sheet >
2. python manage.py load_reporter_panel <path/to/reporter_panel>

