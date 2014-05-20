from csv import reader

from django.core.management.base import BaseCommand, CommandError

from censusdata.models import Census2010Race


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

        file3_name = args[0][:-11] + "000032010.sf1"
        datafile = open(file3_name, 'r')
        to_save = []
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
                to_save.append(data)
        datafile.close()

        Census2010Race.objects.bulk_create(to_save)
