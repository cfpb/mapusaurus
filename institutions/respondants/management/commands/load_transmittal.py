import csv
from django.core.management.base import BaseCommand, CommandError
from respondants.models import Institution, ZipcodeCityState
from respondants.zipcode_utils import create_zipcode

class Command(BaseCommand):
    args = "<filename>"
    help = "Loads the data from a HMDA Transmittal Sheet."

    def handle(self, *args, **options):
        transmittal_filename = args[0]
        with open(transmittal_filename, encoding='utf-8') as institutioncsv:
            transmittal_reader = csv.reader(institutioncsv, delimiter='\t')
            institutions = []
            for inst_line in transmittal_reader:
                zip_code = inst_line[8]
                state = inst_line[7]
                city = inst_line[6]
                zipcode_city = create_zipcode(zip_code, state, city)

                inst = Institution(
                    year = inst_line[0]
                    ffiec_id = inst_line[1]
                    agency = inst_line[2]
                    tax_id = inst_line[3]
                    name = inst_line[4]
                    mailing_address = inst_line[5]
                    zip_code = zipcode_city
                )

                institutions.append(inst)
           bulk_create(institutions) 
