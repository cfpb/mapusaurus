from csv import reader
from django.core.management.base import BaseCommand, CommandError
import os
from django import db
from geo import errors
from geo.models import Geo
from hmda.models import HMDARecord


class Command(BaseCommand):
    args = "<path/to/20XXHMDALAR - National.csv> <delete_file:true>"
    help = """ Load HMDA data (for all states)."""

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Needs a first argument, " + Command.args)


        delete_file = False

        ### if delete_file argument, remove csv file after processing
        ### default is False
        if len(args) > 1:
            if  "delete_file:true" in args[1]:
                delete_file = True
                print "CSV File(s) will not be removed"


        csv_files = []

        if os.path.isfile(args[0]):
            csv_files.append(args[0]);
        elif os.path.isdir(args[0]):
            working_directory = args[0]

            for file in os.listdir(working_directory):
                if os.path.isfile(os.path.join(working_directory,file)) and 'hmda_csv_' in file:
                    #print "CSV File: " + os.path.join(working_directory, file)
                    csv_files.append(os.path.join(working_directory, file))
        else:
            raise Exception("Not a file or Directory! " + args[0])


        geo_states = set(
            row['state'] for row in
            Geo.objects.filter(geo_type=Geo.TRACT_TYPE).values('state').distinct()
        )

        db.reset_queries()

        self.stdout.write("Filtering by states "
                          + ", ".join(list(sorted(geo_states))))

        #todo: hmda query has huge data leak. look into table structure and figure out why.
        known_hmda = set(
            row['statefp'] for row in
            HMDARecord.objects.values('statefp').distinct())

        self.stdout.write("Already have data for "
                         + ", ".join(list(sorted(known_hmda))))

        db.reset_queries()

        def records(f):
            """A generator returning a new Record with each call. Required as
            there are too many to instantiate in memory at once"""

            datafile = open(f, 'r')
            i = 0
            print "Processing " + f
            for row in reader(datafile):

                if i % 25000 == 0:
                        #total_so_far = i // 25000
                    self.stdout.write("Records Processed " + str(i) )#) (i // 25000))
                record = HMDARecord(
                    as_of_year=int(row[0]), respondent_id=row[1],
                    agency_code=row[2], loan_type=int(row[3]),
                    property_type=row[4], loan_purpose=int(row[5]),
                    owner_occupancy=int(row[6]), loan_amount_000s=int(row[7]),
                    preapproval=row[8], action_taken=int(row[9]),
                    msamd=row[10], statefp=row[11], countyfp=row[12],
                    census_tract_number=row[13], applicant_ethnicity=row[14],
                    co_applicant_ethnicity=row[15], applicant_race_1=row[16],
                    applicant_race_2=row[17], applicant_race_3=row[18],
                    applicant_race_4=row[19], applicant_race_5=row[20],
                    co_applicant_race_1=row[21], co_applicant_race_2=row[22],
                    co_applicant_race_3=row[23], co_applicant_race_4=row[24],
                    co_applicant_race_5=row[25], applicant_sex=int(row[26]),
                    co_applicant_sex=int(row[27]), applicant_income_000s=row[28],
                    purchaser_type=row[29], denial_reason_1=row[30],
                    denial_reason_2=row[31], denial_reason_3=row[32],
                    rate_spread=row[33], hoepa_status=row[34],
                    lien_status=row[35], edit_status=row[36],
                    sequence_number=row[37], population=row[38],
                    minority_population=row[39], ffieic_median_family_income=row[40],
                    tract_to_msamd_income=row[41], number_of_owner_occupied_units=row[42],
                    number_of_1_to_4_family_units=row[43], application_date_indicator=row[44])
                censustract = row[11] + row[12] + row[13].replace('.', '')
                record.geoid_id = errors.in_2010.get(censustract, censustract)
                record.auto_fields()
                if (row[11] not in known_hmda and row[11] in geo_states
                        and 'NA' not in record.geoid_id):

                    yield record
                i += 1

            datafile.close()

            if delete_file:
                os.remove(f)




        window = []         # Need to materialize records for bulk_create
        until_insert = 1000
        for f in csv_files:

            for record in records(f):
                if until_insert > 0:
                    until_insert -= 1
                    window.append(record)
                else:
                    HMDARecord.objects.bulk_create(window)
                    db.reset_queries()
                    until_insert = 1000
                    window[:] = []

        HMDARecord.objects.bulk_create(window)
