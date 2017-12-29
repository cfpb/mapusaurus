import csv
from django.core.management.base import BaseCommand
from respondents.models import Institution, Agency
from respondents.zipcode_utils import create_zipcode


class Command(BaseCommand):
    args = "<filename>"
    help = "Loads the data from a HMDA Transmittal Sheet."

    def handle(self, *args, **options):
        transmittal_filename = args[0]

        agencies = Agency.objects.get_all_by_code()

        with open(transmittal_filename) as institutioncsv:
            transmittal_reader = csv.reader(institutioncsv, delimiter='\t')
            institutions = []
            # count = 1 # use if want to see which item failed, see comment below where we create institution individually
            for inst_line in transmittal_reader:
                year = inst_line[0]
                zip_code = inst_line[8]
                state = inst_line[7]
                city = inst_line[6]
                zipcode_city = create_zipcode(zip_code, city, state, year)

                agency = agencies[int(inst_line[2])]

                inst = Institution(
                    year=year,
                    respondent_id=inst_line[1],
                    agency=agency,
                    institution_id=year+inst_line[2]+inst_line[1],
                    tax_id=inst_line[3],
                    name=inst_line[4],
                    mailing_address=inst_line[5],
                    zip_code=zipcode_city,
                    assets=int(inst_line[17]),
                )

                # This can be used to figure out which exact item was failing, will need to disable bulk create below to use this
                # Institution.objects.create(inst)
                # inst.save()
                # count += 1
                institutions.append(inst)
            Institution.objects.bulk_create(institutions)
