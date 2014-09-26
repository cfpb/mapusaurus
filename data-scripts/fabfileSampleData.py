from fabric.api import lcd, local, settings


states = [
    ("California", "ca"),("Georgia", "ga"), ("Illinois", "il"), ("Florida","fl")]


ffiec = "http://www.ffiec.gov/hmdarawdata/OTHER/"


def load_transmittal(working_dir):
    """Download and run the load_transmittal command"""
    with lcd(working_dir):
        local("wget %s2014HMDAInstitutionRecords.zip" % ffiec)
        local("unzip 2014HMDAInstitutionRecords.zip")
        local("rm 2014HMDAInstitutionRecords.zip")
    with lcd("../institutions"):
        local("python manage.py load_transmittal "
              + working_dir + "/2014HMDAInstitutionRecords.txt")
    with lcd(working_dir):
        local("rm 2014HMDAInstitutionRecords.txt")


def load_reporter_panel(working_dir):
    """Download and run the load_reporter_panel command"""
    with lcd(working_dir):
        local("wget %s2014HMDAReporterPanel.zip" % ffiec)
        local("unzip 2014HMDAReporterPanel.zip")
        local("rm 2014HMDAReporterPanel.zip")
    with lcd("../institutions"):
        local("python manage.py load_reporter_panel "
              + working_dir + "/2014HMDAReporterPanel.dat")
    with lcd(working_dir):
        local("rm 2014HMDAReporterPanel.dat")


def load_respondants(working_dir):
    """Load everything for the respondants app"""
    with lcd("../institutions"):
        local("python manage.py loaddata agency")
    load_transmittal(working_dir)
    load_reporter_panel(working_dir)


def load_state_shapefiles(working_dir):
    """For all states, download shape files and load them into the db"""
    base_url = "ftp://ftp2.census.gov/geo/tiger/TIGER2014/TRACT/"
    file_tpl = "tl_2014_%02d_tract.zip"
	codes = [6, 12, 13, 17]
    for i in codes:
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
    filename = "2014HMDALAR - National.zip"
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
