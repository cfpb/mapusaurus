# The 2010 census had a few errors that got fixed in later TIGER files.
# Unfortunately, both HMDA and census population statistics refer to the
# original, erroneous census tracts. See
# http://www.census.gov/geo/reference/pdfs/Geography_Notes.pdf
# https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes.201X.html, where X is the last digit of the year
in_2010 = {
    # Original -> Correct

    # 2012
    # https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2012/geography-changes.html
    "04019002701": "04019002704",
    "04019002903": "04019002906",
    "04019410501": "04019004118",
    "04019410502": "04019004121",
    "04019410503": "04019004125",
    "04019470400": "04019005200",
    "04019470500": "04019005300",

    "06037930401": "06037137000",

    # 2011
    # https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2011/geography-changes.html
    "36053940101": "36053030101",
    "36053940102": "36053030102",
    "36053940103": "36053030103",
    "36053940200": "36053030200",
    "36053940300": "36053030300",
    "36053940401": "36053030401",
    "36053940403": "36053030403",
    "36053940600": "36053030600",
    "36053940700": "36053030402",

    "36065940000": "36065024800",
    "36065940100": "36065024700",
    "36065940200": "36065024900",

    # This tract should never have existed; also zero population so no harm
    # removing it
    "36085008900": None,
}

changes = {
  #https://www.census.gov/geo/maps-data/maps/2010ref/stXX_tract.html, XX to replace with the state code
    2014: {
        "51515050100": "51019050100",
    },
    2015: {
        "02270000100": "02158000100",
        "46113940500": "46102940500",
        "46113940800": "46102940800",
        "46113940900": "46102940900",
        # More soon
    }
}
def change_specific_year(census_tract, year):
    new_census_tract = census_tract
    for yr in sorted(changes):
        if int(year) > yr:
            new_census_tract = changes[yr].get(new_census_tract, new_census_tract)
    return new_census_tract
