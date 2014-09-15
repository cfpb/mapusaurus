from fabric.api import lcd, local, settings


states = [
    ("Alabama", "al"), ("Alaska", "ak"), ("Arizona", "az"), ("Arkansas", "ar"),
    ("California", "ca"), ("Colorado", "co"), ("Connecticut", "ct"),
    ("Delaware", "de"), ("District_of_Columbia", "dc"), ("Florida", "fl"),
    ("Georgia", "ga"), ("Hawaii", "hi"), ("Idaho", "id"), ("Illinois", "il"),
    ("Indiana", "in"), ("Iowa", "ia"), ("Kansas", "ks"), ("Kentucky", "ky"),
    ("Louisiana", "la"), ("Maine", "me"), ("Maryland", "md"),
    ("Massachusetts", "ma"), ("Michigan", "mi"), ("Minnesota", "mn"),
    ("Mississippi", "ms"), ("Missouri", "mo"), ("Montana", "mt"),
    ("Nebraska", "ne"), ("Nevada", "nv"), ("New_Hampshire", "nh"),
    ("New_Jersey", "nj"), ("New_Mexico", "nm"), ("New_York", "ny"),
    ("North_Carolina", "nc"), ("North_Dakota", "nd"), ("Ohio", "oh"),
    ("Oklahoma", "ok"), ("Oregon", "or"), ("Pennsylvania", "pa"),
    ("Rhode_Island", "ri"), ("South_Carolina", "sc"), ("South_Dakota", "sd"),
    ("Tennessee", "tn"), ("Texas", "tx"), ("Utah", "ut"), ("Vermont", "vt"),
    ("Virginia", "va"), ("Washington", "wa"), ("West_Virginia", "wv"),
    ("Wisconsin", "wi"), ("Wyoming", "wy")]


ffiec = "http://www.ffiec.gov/hmdarawdata/OTHER/"


def load_transmittal(working_dir):
    """Download and run the load_transmittal command"""
    with lcd(working_dir):
        local("wget %s2012HMDAInstitutionRecords.zip" % ffiec)
        local("unzip 2012HMDAInstitutionRecords.zip")
        local("rm 2012HMDAInstitutionRecords.zip")
    with lcd("../institutions"):
        local("python manage.py load_transmittal "
              + working_dir + "/2012HMDAInstitutionRecords.txt")
    with lcd(working_dir):
        local("rm 2012HMDAInstitutionRecords.txt")


def load_reporter_panel(working_dir):
    """Download and run the load_reporter_panel command"""
    with lcd(working_dir):
        local("wget %s2012HMDAReporterPanel.zip" % ffiec)
        local("unzip 2012HMDAReporterPanel.zip")
        local("rm 2012HMDAReporterPanel.zip")
    with lcd("../institutions"):
        local("python manage.py load_reporter_panel "
              + working_dir + "/2012HMDAReporterPanel.dat")
    with lcd(working_dir):
        local("rm 2012HMDAReporterPanel.dat")


def load_respondants(working_dir):
    """Load everything for the respondants app"""
    with lcd("../institutions"):
        local("python manage.py loaddata agency")
    load_transmittal(working_dir)
    load_reporter_panel(working_dir)


def load_state_shapefiles(working_dir):
    """For all states, download shape files and load them into the db"""
    base_url = "ftp://ftp2.census.gov/geo/tiger/TIGER2013/TRACT/"
    file_tpl = "tl_2013_%02d_tract.zip"
    for i in range(1, 70):
        filename = file_tpl % i
        with lcd(working_dir):
            with settings(warn_only=True):
                result = local("wget " + base_url + filename, capture=True)
            if result.failed:
                continue
            local("unzip " + filename)
            local("rm " + filename)
        with lcd("../institutions"):
            local("python manage.py load_geos_from " + working_dir + "/"
                  + filename.replace("zip", "shp"))
        with lcd(working_dir):
            local("rm " + filename.replace("zip", "*"))


def load_other_geos(working_dir):
    """In addition to tracts, we need to load counties, metros, and more."""
    for geo_type in ('county', 'cbsa', 'metdiv'):
        filename = "tl_2013_us_" + geo_type + ".zip"
        with lcd(working_dir):
            local("wget ftp://ftp2.census.gov/geo/tiger/TIGER2013/"
                  + geo_type.upper() + "/" + filename)
            local("unzip " + filename)
        with lcd("../institutions"):
            local("python manage.py load_geos_from " + working_dir + "/"
                  + filename.replace("zip", "shp"))
        with lcd(working_dir):
            local("rm " + filename.replace("zip", "*"))
    with lcd("../institutions"):
        local("python manage.py set_tract_csa_cbsa")


def load_summary_ones(working_dir):
    """For all states, download census files and load them into the db"""
    url_tpl = "http://www2.census.gov/census_2010/04-Summary_File_1/%s/"
    url_tpl += "%s2010.sf1.zip"
    for long_name, short_name in states:
        with lcd(working_dir):
            local("wget " + url_tpl % (long_name, short_name))
            local("unzip {0}2010.sf1.zip {0}geo2010.sf1 {0}0000?2010.sf1"
                  .format(short_name))
            local("rm %s2010.sf1.zip" % short_name)
        with lcd("../institutions"):
            local("python manage.py load_summary_one "
                  + working_dir + "/%sgeo2010.sf1" % short_name)
        with lcd(working_dir):
            local("rm %sgeo2010.sf1" % short_name)
            local("rm %s0000?2010.sf1" % short_name)


def load_hmda(working_dir):
    """Download HMDA data and then load it into the db"""
    base_url = "http://www.ffiec.gov/hmdarawdata/LAR/National/"
    filename = "2012HMDALAR - National.zip"
    with lcd(working_dir):
        local("wget '" + base_url + filename + "'")
        local("unzip '" + filename + "'")
        local("rm '" + filename + "'")
    with lcd("../institutions"):
        local("python manage.py load_hmda '" + working_dir + "/"
              + filename.replace("zip", "csv") + "'")
    with lcd(working_dir):
        local("rm '" + filename.replace("zip", "csv") + "'")


def precache_hmda():
    """We precache median loan amount per lender x metro"""
    with lcd("../institutions"):
        local("python manage.py calculate_loan_stats")


def load_all(working_dir="/tmp"):
    """Download and import all data for the app"""
    load_respondants(working_dir)
    load_state_shapefiles(working_dir)
    load_other_geos(working_dir)
    load_summary_ones(working_dir)
    load_hmda(working_dir)
    precache_hmda()
