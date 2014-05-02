import csv
from django.core.management.base import BaseCommand, CommandError
from respondants.models import Institution, ZipcodeCityState

class Command(BaseCommand):
    args = "<filename>"
    help = "Loads the data from a HMDA Transmittal Sheet."

    def create_zipcode(zip_code, state, city):

        zipcode_city = ZipcodeCityState(
            city = city,
            state = state,
        )
        
        if '-' in zip_code:
            zip_code, plus_four = zip_code.split('-')

        zipcode_city.zip_code = 
        
        

    def handle(self, *args, **options):
        transmittal_filename = args[0]
        with open(transmittal_filename, encoding='utf-8') as institutioncsv:
            transmittal_reader = csv.reader(institutioncsv, delimiter='\t')
            for inst_line in transmittal_reader:
                zip_code = inst_line[8]
                state = inst_line[7]
                city = inst_line[6]
                zipcode_city = create_zipcode(zip_code, state, city)

                #inst = Institution(
                #    year = inst_line[0]
                #    ffiec_id = inst_line[1]
                #    agency = inst_line[2]
                #    tax_id = inst_line[3]
                #    name = inst_line[4]
                #    mailing_address = inst_line[5]
                #)
                
                #year = inst_line[0]
                #respondant_id = inst_line[1]
                self.stdout.write('%s|%s|%s' % (zip_code, city, state))
