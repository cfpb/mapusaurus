import collections
from django.core.management.base import BaseCommand, CommandError

#Let's try out named tuples. 
ReporterRow = collections.namedtuple(
    "ReporterRow", 
    [
        'year',
        'respondant_id',
        'agency_code',
        'parent_id',
        'parent_name',
        'parent_city',
        'parent_state', 
        'region',
        'assets', 
        'lender_code', 
        'respondant_name', 
        'filler_1',
        'respondant_city', 
        'respondant_state',
        'filler_2', 
        'filler_3',
        'top_holder_rssd_id',
        'top_holder_name', 
        'top_holder_city',
        'top_holder_state',
        'top_holder_country',
        'respondant_rssd_id',
        'parent_rssd_id',
        'respondant_fips_state'
    ]
)

def parse_line(line):
    """ Parse a reporter panel line into a dictionary.  """
    reporter = ReporterRow(
        year=line[0:4],
        respondant_id=line[4:14],
        agency_code=line[14:15],
        parent_id=line[15:25],
        parent_name=line[25:55],
        parent_city=line[55:80],
        parent_state=line[80:82], 
        region=line[82:84],
        assets=line[84:94], 
        lender_code=line[94:95], 
        respondant_name=line[95:125], 
        filler_1=line[125:165],
        respondant_city=line[165:190], 
        respondant_state=line[190:192],
        filler_2=line[192:202], 
        filler_3=line[202:212],
        top_holder_rssd_id=line[212:222],
        top_holder_name=line[222:252], 
        top_holder_city=line[252:277],
        top_holder_state=line[277:279],
        top_holder_country=line[279:319],
        respondant_rssd_id=line[319:329],
        parent_rssd_id=line[329:339],
        respondant_fips_state=line[339:341],
    )
    return reporter


def parse_file(filename):
    """ Parse the FFIEC HMDA reporterpanel.dat file. The format of this file is
    pre-determined by the FFIEC. """

    with open(filename, encoding='utf-8') as panelcsv:
        for line in panelcsv:
            reporter_row = parse_line(line)
            print('--------')
            print(line)
            print(reporter_row)
            print('>-----------')
             

class Command(BaseCommand):
    args = "<filename>"
    help = "Reporter panel contains parent information. Loads that."

    def handle(self, *args, **options):
        reporter_filename = args[0]
        parse_file(reporter_filename)
