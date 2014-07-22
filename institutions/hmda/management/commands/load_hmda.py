from csv import reader

from django.core.management.base import BaseCommand, CommandError

from geo.management.commands.load_state_shapefile import errors_in_2010
from geo.models import Geo
from hmda.models import HMDARecord


class Command(BaseCommand):
    args = "<path/to/20XXHMDALAR - National.csv>"
    help = """ Load HMDA data (for all states)."""

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Needs a first argument, " + Command.args)

        geo_states = set(
            row['state'] for row in
            Geo.objects.values('state').distinct())
        self.stdout.write("Filtering by states "
                          + ", ".join(list(sorted(geo_states))))
        known_hmda = set(
            row['statefp'] for row in
            HMDARecord.objects.values('statefp').distinct())
        self.stdout.write("Already have data for "
                          + ", ".join(list(sorted(known_hmda))))

        def records():
            """A generator returning a new Record with each call. Required as
            there are too many to instantiate in memory at once"""
            datafile = open(args[0], 'r')
            i = 0
            for row in reader(datafile):
                if i % 1000000 == 0:
                    self.stdout.write("Record %d 000,000" % (i // 1000000))
                record = HMDARecord(
                    as_of_year=int(row[0]), respondent_id=row[1],
                    agency_code=row[2], loan_amount_000s=int(row[7]),
                    action_taken=row[9], statefp=row[11], countyfp=row[12])
                censustract = row[11] + row[12] + row[13].replace('.', '')
                record.geoid_id = errors_in_2010.get(censustract, censustract)
                record.auto_fields()
                if (row[11] not in known_hmda and row[11] in geo_states
                        and 'NA' not in record.geoid_id):
                    yield record
                i += 1
            datafile.close()

        window = []         # Need to materialize records for bulk_create
        until_insert = 1000
        for record in records():
            if until_insert > 0:
                until_insert -= 1
                window.append(record)
            else:
                HMDARecord.objects.bulk_create(window)
                until_insert = 1000
                window = []
        HMDARecord.objects.bulk_create(window)
