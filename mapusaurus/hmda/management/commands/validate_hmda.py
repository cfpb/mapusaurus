from django.core.management.base import BaseCommand, CommandError
from hmda.models import HMDARecord
from django.test import SimpleTestCase
from django.db.models import Q



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
        states_with_Q_Counts = {"12":944260,
                                "17":635804,
                                "18":341612,
                                "55":303365
                               }

        for key,value in states_with_Q_Counts.items():
            db_count = HMDARecord.objects.filter(statefp=key).count()
            print "Testing State " + key
            assert self.test_records(db_count,value)

        print "Congrats! All HMDA Record Counts Passed"



    def test_records(self,db_count, Q_count):
        if db_count == Q_count:
            print "Passed"
            return True

        print "Failed " + str(db_count), str(Q_count)
        return False