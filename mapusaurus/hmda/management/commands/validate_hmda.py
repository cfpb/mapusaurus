from django.core.management.base import BaseCommand
from hmda.models import HMDARecord

class Command(BaseCommand):
    args = "None"
    help = """ Validate HMDA Data in FairLending DB is Correct"""

    def handle(self, *args, **options):
        print "Begin Validation"
        '''
        #  To test this go to https://api.consumerfinance.gov/data/hmda/slice/hmda_lar.html?
        #  filter by where clasue:  as_of_year=2013
        #                           and census_tract_number != ''
        #                           and state_code=<insert_state_num_here>
        '''

        states_with_Q_Counts = {"12":944260,"17":635804,"18":341612,"55":303365,"06":2158015,"13":534125}
        for key,value in states_with_Q_Counts.items():
            db_count = HMDARecord.objects.filter(as_of_year=2013,statefp=key).count()
            print str(value) + " total for  State " + key
            assert self.test_records(db_count,value)

        ethnicity_na  = {"06":175823,"12":74871,"13":55797,"17":58629,"18":28680,"55":17851}
        for key,value in ethnicity_na.items():
            db_count = HMDARecord.objects.filter(as_of_year=2013,statefp=key, applicant_ethnicity='4').count()
            print str(value) +" Applicants who did not report ethnicity for State " + key
            assert self.test_records(db_count,value)

        applicant_females = {"06":501109,"12":254857,"13":142849,"17":157410,"18":82801,"55":72931}
        for key,value in applicant_females.items():
            db_count = HMDARecord.objects.filter(as_of_year=2013,statefp=key, applicant_sex=2).count()
            print str(value) +" Female applicants for State " + key
            assert self.test_records(db_count,value)

        #list should be updated with next years import
        #currently using the 2009 standard for HMDA 2013 data. Next year, HMDA will use 2013 standard.
        msacode_ids = [ '14460', '16980', '19100', '19820', '31100', '33100', '35620', '37980',
                               '41860', '42660','47900' ]
        db_count = HMDARecord.objects.filter(as_of_year=2013, msamd__in=msacode_ids).count()
        print "MSA Code count should be zero"
        assert self.test_records(db_count,0)

        print "Congrats! All HMDA Record Counts Passed"


    def test_records(self,db_count, Q_count):
        if db_count == Q_count:
            print "Passed"
            return True

        print "Failed " + str(db_count), str(Q_count)
        return False