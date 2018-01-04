from csv import reader

from django.core.management.base import BaseCommand, CommandError

from censusdata.models import (
    Census2010Age, Census2010HispanicOrigin, Census2010Households,
    Census2010Race, Census2010RaceStats, Census2010Sex)
from geo import errors


class Command(BaseCommand):
    """Loads Summary File 1 data from the decennial census. Official
    documentation for fields at
    http://www.census.gov/prod/cen2010/doc/sf1.pdf"""
    args = "<path/to/XXgeo2010.sf1> <year>"
    help = """
        Load Decennial Census data for a state.
        Assumes XX#####2010.sf1 files are in the same directory."""

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("Needs 2 arguments, "
                               + "path/to/XXgeo2010.sf1 year")
        geoids_by_record = {}
        geofile_name = args[0]
        geofile = open(geofile_name, 'r')
        year = args[1]
        # As each file covers one state, all geos will have the same state id
        state = ""
        for line in geofile:
            if line[8:11] == '140':    # Aggregated by Census Tract
                recordnum = line[18:25]
                censustract = line[27:32] + line[54:60]
                censustract = errors.in_2010.get(censustract, censustract)
                censustract = errors.change_specific_year(censustract, year)
                if censustract is not None:
                    geoids_by_record[recordnum] = year + censustract
                state = line[27:29]
        geofile.close()
        self.handle_filethree(geofile_name, year, state, geoids_by_record)
        self.handle_filefour(geofile_name, year, state, geoids_by_record)
        self.handle_filefive(geofile_name, year, state, geoids_by_record)

    def handle_filethree(self, geofile_name, year, state, geoids_by_record):
        """File three (XX000032010.sf1) contains race and ethnicity summaries.
        Documentation starts at page 6-22."""
        file3_name = geofile_name[:-11] + "000032010.sf1"
        datafile = open(file3_name, 'r')
        race, hispanic, stats = [], [], []
        skip_race = Census2010Race.objects.filter(
            geoid__state=state, geoid__year=year).exists()
        skip_hisp = Census2010HispanicOrigin.objects.filter(
            geoid__state=state, geoid__year=year).exists()
        skip_stats = Census2010RaceStats.objects.filter(
            geoid__state=state, geoid__year=year).exists()

        if not skip_race or not skip_hisp or not skip_stats:
            for row in reader(datafile):
                recordnum = row[4]
                if recordnum in geoids_by_record:
                    data = Census2010Race(
                        total_pop=int(row[5]), white_alone=int(row[6]),
                        black_alone=int(row[7]), amind_alone=int(row[8]),
                        asian_alone=int(row[9]), pacis_alone=int(row[10]),
                        other_alone=int(row[11]), two_or_more=int(row[12]))
                    # Save geoid separately so we don't need to load the
                    # Tracts
                    data.geoid_id = geoids_by_record[recordnum]
                    race.append(data)

                    data = Census2010HispanicOrigin(
                        total_pop=int(row[13]), non_hispanic=int(row[14]),
                        hispanic=int(row[15]))
                    data.geoid_id = geoids_by_record[recordnum]
                    hispanic.append(data)

                    data = Census2010RaceStats(
                        total_pop=int(row[16]), hispanic=int(row[25]),
                        non_hisp_white_only=int(row[18]),
                        non_hisp_black_only=int(row[19]),
                        non_hisp_asian_only=int(row[21]))
                    data.geoid_id = geoids_by_record[recordnum]
                    data.auto_fields()
                    stats.append(data)
        datafile.close()

        if not skip_race:
            Census2010Race.objects.bulk_create(race)
        if not skip_hisp:
            Census2010HispanicOrigin.objects.bulk_create(hispanic)
        if not skip_stats:
            Census2010RaceStats.objects.bulk_create(stats)

    def handle_filefour(self, geofile_name, year, state, geoids_by_record):
        """File four (XX000042010.sf1) contains age demographics and
        correlations with race, ethnicity, and sex. Documentation starts at
        page 6-30"""
        file4_name = geofile_name[:-11] + "000042010.sf1"
        datafile = open(file4_name, 'r')
        sex, age = [], []
        skip_sex = Census2010Sex.objects.filter(geoid__state=state, geoid__year=year).exists()
        skip_age = Census2010Age.objects.filter(geoid__state=state, geoid__year=year).exists()
        if not skip_sex or not skip_age:
            for row in reader(datafile):
                recordnum = row[4]
                if recordnum in geoids_by_record:
                    data = Census2010Sex(
                        total_pop=int(row[149]), male=int(row[150]),
                        female=int(row[174]))
                    # Save geoid separately so we don't need to load the Tracts
                    data.geoid_id = geoids_by_record[recordnum]
                    sex.append(data)

                    fields = [None]     # Ignore geoid until later
                    fields.append(int(row[149]))    # total_pop
                    # age groups are calculated by adding male to female values
                    fields.extend(map(
                        lambda i: int(row[i + 151]) + int(row[i + 175]),
                        range(23)))
                    data = Census2010Age(*fields)
                    data.geoid_id = geoids_by_record[recordnum]
                    age.append(data)
        datafile.close()

        if not skip_sex:
            Census2010Sex.objects.bulk_create(sex)
        if not skip_age:
            Census2010Age.objects.bulk_create(age)

    def handle_filefive(self, geofile_name, year, state, geoids_by_record):
        """File five (XX000052010.sf1) contains household metrics, including
        divisions by household type, household size, etc. Documentation starts
        at page 6-38"""
        file4_name = geofile_name[:-11] + "000052010.sf1"
        datafile = open(file4_name, 'r')
        households = []
        skip_households = Census2010Households.objects.filter(
            geoid__state=state, geoid__year=year).exists()
        if not skip_households:
            for row in reader(datafile):
                recordnum = row[4]
                if recordnum in geoids_by_record:
                    fields = [None]     # Ignore geoid until later
                    # fields match the values in the census
                    fields.extend(int(row[idx]) for idx in range(28, 37))
                    data = Census2010Households(*fields)
                    data.geoid_id = geoids_by_record[recordnum]
                    households.append(data)
        datafile.close()

        if not skip_households:
            Census2010Households.objects.bulk_create(households)
