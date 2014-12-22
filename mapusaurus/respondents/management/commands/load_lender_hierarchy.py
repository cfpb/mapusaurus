import csv
from django.core.management.base import BaseCommand
from respondents.models import LenderHierarchy, Institution


class Command(BaseCommand):
    args = "<filename>"

    def handle(self, *args, **options):
        hierarchy_filename = args[0]

        with open(hierarchy_filename) as hierarchycsv:
            hierarchy_reader = csv.reader(hierarchycsv, delimiter=',')
            hierarchy = []
            for hierarchy_line in hierarchy_reader:
                record = LenderHierarchy(
                    organization_id=int(hierarchy_line[2]),
                )
                record.institution_id = hierarchy_line[0]+hierarchy_line[1].replace("'", "")
                hierarchy.append(record)
            LenderHierarchy.objects.bulk_create(hierarchy)
