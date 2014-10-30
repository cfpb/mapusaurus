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
        local("wget %s2013HMDAInstitutionRecords.zip" % ffiec)
        local("unzip 2013HMDAInstitutionRecords.zip")
        local("rm 2013HMDAInstitutionRecords.zip")
    with lcd("../institutions"):
        local("python manage.py load_transmittal "
              + working_dir + "/2013HMDAInstitutionRecords.txt")
    with lcd(working_dir):
        local("rm 2013HMDAInstitutionRecords.txt")


def load_reporter_panel(working_dir):
    """Download and run the load_reporter_panel command"""
    with lcd(working_dir):
        local("wget %s2013HMDAReporterPanel.zip" % ffiec)
        local("unzip 2013HMDAReporterPanel.zip")
        local("rm 2013HMDAReporterPanel.zip")
    with lcd("../institutions"):
        local("python manage.py load_reporter_panel "
              + working_dir + "/2013HMDAReporterPanel.dat")
    with lcd(working_dir):
        local("rm 2013HMDAReporterPanel.dat")


def load_respondants(working_dir):
    """Load everything for the respondants app"""
    with lcd("../institutions"):
        local("python manage.py loaddata agency")
    load_transmittal(working_dir)
    load_reporter_panel(working_dir)


def load_geos(working_dir):
    """In addition to tracts, we need to load counties, metros, and more."""
    for geo_type in ('county', 'cbsa', 'metdiv'):
        filename = "tl_2014_us_" + geo_type + ".zip"
        with lcd(working_dir):
            local("wget ftp://ftp2.census.gov/geo/tiger/TIGER2014/"
                  + geo_type.upper() + "/" + filename)
            local("unzip " + filename)
        with lcd("../institutions"):
            local("python manage.py load_geos_from " + working_dir + "/"
                  + filename.replace("zip", "shp"))
        with lcd(working_dir):
            local("rm " + filename.replace("zip", "*"))
    with lcd("../institutions"):
        local("python manage.py set_tract_csa_cbsa")


def load_census(working_dir):
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
    filename = "2013HMDALAR - National.zip"
    with lcd(working_dir):
        local("wget '" + base_url + filename + "'")
        local("unzip '" + filename + "'")
        local("rm '" + filename + "'")
        local('split -l 500000 -d "'+ filename.replace("zip", "csv") + '" hmda_csv_')
        local("rm '" + filename.replace("zip", "csv") + "'")
    with lcd("../institutions"):
        local("python manage.py load_hmda '" + working_dir + "' delete_file:true" )
        local("sudo su postgres")
        local("reindex flc_demo)

def precache_hmda():
    """We precache median loan amount per lender x metro"""
    with lcd("../institutions"):
        local("python manage.py calculate_loan_stats")


def load_all(working_dir="/tmp"):
    """Download and import all data for the app"""
    load_respondants(working_dir)
    load_geos(working_dir)
    load_census(working_dir)
    load_hmda(working_dir)
    precache_hmda()
