import csv
from django.core.management.base import BaseCommand
from respondents.models import LenderHierarchy, Agency


class Command(BaseCommand):
    args = "<filename>"
    help = "Loads the data from Vahan's csv mapping."

    def handle(self, *args, **options):
        hierarchy_filename = args[0]

        agencies = Agency.objects.get_all_by_code()

        with open(hierarchy_filename) as hierarchycsv:
            hierarchy_reader = csv.reader(hierarchycsv, delimiter=',')
            hierarchy = []
            for hierarchy_line in hierarchy_reader:
                agency = agencies[int(hierarchy_line[0])]
                record = LenderHierarchy(
                    agency=agency,
                    respondent_id=hierarchy_line[1].replace("'", ""),
                    organization_id=int(hierarchy_line[2]),
                )
                hierarchy.append(record)
            LenderHierarchy.objects.bulk_create(hierarchy)
