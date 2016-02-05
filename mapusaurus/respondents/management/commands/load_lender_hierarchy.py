import csv
from django.core.management.base import BaseCommand
from respondents.models import LenderHierarchy, Institution

class Command(BaseCommand):
    args = "<year> <filename>"

    def handle(self, *args, **options):
        year = args[0]
        hierarchy_filename = args[1]

        with open(hierarchy_filename) as hierarchycsv:
            hierarchy_reader = csv.reader(hierarchycsv, delimiter=',')
            hierarchy = []
            for hierarchy_line in hierarchy_reader:
                record = LenderHierarchy(
                    organization_id=int(hierarchy_line[2]),
                )
                record.institution_id = year+hierarchy_line[0]+hierarchy_line[1].replace("'", "")
                hierarchy.append(record)
            LenderHierarchy.objects.bulk_create(hierarchy)
