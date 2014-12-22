import csv
from django.core.management.base import BaseCommand
from respondents.models import Branch, Institution

class Command(BaseCommand):
    args = "<filename>"

    def handle(self, *args, **options):
        branch_location_filename = args[0]
        count = 0; 
        with open(branch_location_filename, 'rU') as branch_location_txt:
            branch_location_reader = csv.reader(branch_location_txt, delimiter='\t')
            branch_location = []
            for branch_location_line in branch_location_reader:
                record = Branch(
                    year = branch_location_line[0].replace("'", ""),
                    name = branch_location_line[6],
                    street = branch_location_line[7] if branch_location_line[7] != '0' else '', 
                    city = branch_location_line[8],
                    state = branch_location_line[10],
                    zipcode = branch_location_line[11],
                    lat = branch_location_line[13], 
                    lon = branch_location_line[12],
                )
                record.institution_id = (branch_location_line[1]+branch_location_line[2]).replace("'", "")
                if Institution.objects.filter(institution_id=record.institution_id).count() > 0:
                    branch_location.append(record)
                if len(branch_location) > 9999:
                    count += len(branch_location)
                    Branch.objects.bulk_create(branch_location, batch_size=1000)
                    print "Record count: " + str(count)
                    branch_location[:] = []
                
