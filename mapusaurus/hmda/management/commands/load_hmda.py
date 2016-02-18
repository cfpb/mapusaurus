from csv import reader
from django.core.management.base import BaseCommand, CommandError
import os
from django import db
from geo import errors
from geo.models import Geo
from hmda.models import HMDARecord
import sys
import traceback
import logging



class Command(BaseCommand):
    args = "<path/to/20XXHMDALAR - National.csv> <year> <delete_file:true/false> <filterhmda>"
    help = """ Load HMDA data (for all states)."""


    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Need args for CSV path and year, " + Command.args)

        delete_file = False
        filter_hmda = False

        self.total_skipped = 0
        self.na_skipped = 0
        self.total_lines_read = 0
        self.other_skipped  = 0

        def get_logger():
            logging.basicConfig(filename='hmdaload.log',
                                level=logging.INFO,
                                format='%(asctime)s %(message)s')

        def log_info(message):
            logging.info(message)
            print message

        get_logger()



        ### if delete_file argument, remove csv file after processing
        ### default is False
        ### if filter_hmda is passed in, setup known_hmda & geo_states
        ### else load all HMDA records without filtering
        lar_path = args[0]
        year = args[1]
        if len(args) > 2:
            for arg in args:
                if  "delete_file:" in arg:
                    tmp_delete_flag= arg.split(":")
                    if tmp_delete_flag[1] == "true" or tmp_delete_flag[1] == "True":
                        delete_file = True

                        print "************* CSV File(s) WiLL BE REMOVED AFTER PROCESSING ***********"

                if "filterhmda" in arg:
                    filter_hmda = True



        csv_files = []
        if os.path.isfile(lar_path):
            csv_files.append(lar_path);
        elif os.path.isdir(lar_path):
            working_directory = lar_path

            for file in os.listdir(working_directory):
                if os.path.isfile(os.path.join(working_directory,file)) and 'hmda_csv_'+year+'_' in file:
                    csv_files.append(os.path.join(working_directory, file))
        else:
            raise Exception("Not a file or Directory! " + lar_path)



        geo_states = set(
                row['state'] for row in
                Geo.objects.filter(geo_type=Geo.TRACT_TYPE).values('state').distinct()
            )

        db.reset_queries()

        log_info("Filtering by states " + ", ".join(list(sorted(geo_states))))

        if filter_hmda:
            known_hmda = set(
                row['statefp'] for row in
                HMDARecord.objects.values('statefp').distinct())

            log_info("Already have data for "+ ", ".join(list(sorted(known_hmda))))

            db.reset_queries()



        def records(self,csv_file):
            """A generator returning a new Record with each call. Required as
            there are too many to instantiate in memory at once"""
            prevent_delete= False
            datafile = open(csv_file, 'r')
            i = 0
            inserted_counter = 0
            skipped_counter = 0
            log_info("Processing " + csv_file)
            for row in reader(datafile):
                i += 1
                if i % 25000 == 0:
                    log_info("Records Processed For File " + str(i) )

                try:

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
                    censustract = errors.in_2010.get(censustract, censustract)
                    record.geo_id = str(record.as_of_year) + censustract

                    record.institution_id = str(record.as_of_year) + record.agency_code + record.respondent_id

                    self.total_lines_read = self.total_lines_read + 1

                    if filter_hmda:
                        if (row[11] not in known_hmda and row[11] in geo_states and 'NA' not in record.geo_id):
                            inserted_counter  +=1
                            yield record
                        else:
                            skipped_counter += 1
                    else:
                        if row[11] in geo_states and 'NA' not in record.geo_id:
                            inserted_counter  =inserted_counter + 1
                            yield record
                        else:
                            if 'NA' in record.geo_id:
                                self.na_skipped = self.na_skipped + 1
                            else:
                                self.other_skipped = self.other_skipped +1

                            self.total_skipped = self.total_skipped + 1

                        skipped_counter += 1

                except:
                    prevent_delete= True
                    log_info('*****************************')
                    log_info("Error processing csv_file")
                    log_info("Record Line Number " + str(i))
                    log_info("Row: "+ str(row))
                    log_info("Unexpected error:", sys.exc_info()[0])
                    log_info(traceback.print_exc())
                    log_info('*****************************')

            datafile.close()

            log_info("Finished Processing File: " + str(i))
            log_info("Records That have been yield/Inserted For File: " + str(inserted_counter) )
            log_info("Records Skipped For File: " + str(skipped_counter) )

            if delete_file:
                if not prevent_delete:
                    os.remove(csv_file)




        window = []         # Need to materialize records for bulk_create
        total_count = 0
        for csv_file in csv_files:
            for record in records(self,csv_file):
                window.append(record)
                total_count = total_count + 1
                if len(window) > 999:
                    HMDARecord.objects.bulk_create(window,batch_size=200)
                    db.reset_queries()
                    window[:] = []

            if (len(window) > 0):
                log_info("window size (last records): " + str(len(window)))
                HMDARecord.objects.bulk_create(window,batch_size=100)
                db.reset_queries()
                window[:] = []


            log_info("All Files Total Records bulk inserted: " + str(total_count))
            log_info("All Lines Read from All Files: " + str(self.total_lines_read))
            log_info("All Files Total Skipped: " + str(self.total_skipped))
            log_info("All Files Total Skipped for GeoID=NA: " + str(self.na_skipped))
            log_info("All Files Total Skipped for other reason: " + str(self.other_skipped ))