from csv import reader

from django.core.management.base import BaseCommand, CommandError

from geo.models import StateCensusTract
from hmda.models import HMDARecord


class Command(BaseCommand):
    args = "<path/to/20XXHMDALAR - National.csv>"
    help = """ Load HMDA data (for all states)."""

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Needs a first argument, " + Command.args)

        HMDARecord.objects.all().delete()
        known_states = set(
            row['statefp'] for row in
            StateCensusTract.objects.values('statefp').distinct())
        print "Filtering by states", ", ".join(list(sorted(known_states)))

        def records():
            """A generator returning a new Record with each call. Required as
            there are too many to instantiate in memory at once"""
            datafile = open(args[0], 'r')
            i = 0
            for row in reader(datafile):
                if i % 1000000 == 0:
                    print "Record", i // 1000000, "000,000"
                record = HMDARecord(
                    as_of_year=int(row[0]),
                    respondent_id=row[1],
                    agency_code=row[2],
                    loan_amount_000s=int(row[7]),
                    action_taken=row[9],
                    state_code=row[11],
                    county_code=row[12],
                    census_tract=row[13].replace('.', ''))
                record.auto_fields()
                if row[11] in known_states and 'NA' not in record.geoid_id:
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
