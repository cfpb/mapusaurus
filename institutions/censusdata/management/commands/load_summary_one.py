from csv import reader

from django.core.management.base import BaseCommand, CommandError

from censusdata.models import (
    Census2010Age, Census2010HispanicOrigin, Census2010Race, Census2010Sex)


class Command(BaseCommand):
    args = "<path/to/XXgeo2010.sf1>"
    help = """
        Load Decennial Census data for a state.
        Assumes XX#####2010.sf1 files are in the same directory."""

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Needs a first argument, "
                               + "path/to/XXgeo2010.sf1")
        geoids_by_record = {}
        geofile = open(args[0], 'r')
        for line in geofile:
            if line[8:11] == '140':    # Aggregated by Census Tract
                recordnum = line[18:25]
                geoids_by_record[recordnum] = line[27:32] + line[54:60]
        geofile.close()
        self.handle_filethree(args[0], geoids_by_record)
        self.handle_filefour(args[0], geoids_by_record)

    def handle_filethree(self, geofile_name, geoids_by_record):
        file3_name = geofile_name[:-11] + "000032010.sf1"
        datafile = open(file3_name, 'r')
        race, hispanic = [], []
        for row in reader(datafile):
            recordnum = row[4]
            if recordnum in geoids_by_record:
                data = Census2010Race(
                    total_pop=int(row[5]), white_alone=int(row[6]),
                    black_alone=int(row[7]), amind_alone=int(row[8]),
                    asian_alone=int(row[9]), pacis_alone=int(row[10]),
                    other_alone=int(row[11]), two_or_more=int(row[12]))
                # Save geoid separately so we don't need to load the Tracts
                data.geoid_id = geoids_by_record[recordnum]
                race.append(data)

                data = Census2010HispanicOrigin(
                    total_pop=int(row[13]), non_hispanic=int(row[14]),
                    hispanic=int(row[15]))
                data.geoid_id = geoids_by_record[recordnum]
                hispanic.append(data)
        datafile.close()

        Census2010Race.objects.bulk_create(race)
        Census2010HispanicOrigin.objects.bulk_create(hispanic)

    def handle_filefour(self, geofile_name, geoids_by_record):
        file4_name = geofile_name[:-11] + "000042010.sf1"
        datafile = open(file4_name, 'r')
        sex, age = [], []
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

        Census2010Sex.objects.bulk_create(sex)
        Census2010Age.objects.bulk_create(age)
