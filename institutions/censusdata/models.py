"""Note that we use field names corresponding to those found in the census
data. This does not represent the authors' endorsement of those distinctions
nor categories."""
from django.db import models


class Census2010Race(models.Model):
    geoid = models.ForeignKey('geo.StateCensusTract', to_field='geoid',
                              unique=True, db_index=True, primary_key=True)

    total_pop = models.IntegerField()
    white_alone = models.IntegerField()
    black_alone = models.IntegerField()
    amind_alone = models.IntegerField()
    asian_alone = models.IntegerField()
    pacis_alone = models.IntegerField()
    other_alone = models.IntegerField()
    two_or_more = models.IntegerField()


class Census2010HispanicOrigin(models.Model):
    geoid = models.ForeignKey('geo.StateCensusTract', to_field='geoid',
                              unique=True, db_index=True, primary_key=True)

    total_pop = models.IntegerField()
    non_hispanic = models.IntegerField()
    hispanic = models.IntegerField()


class Census2010Sex(models.Model):
    geoid = models.ForeignKey('geo.StateCensusTract', to_field='geoid',
                              unique=True, db_index=True, primary_key=True)

    total_pop = models.IntegerField()
    male = models.IntegerField()
    female = models.IntegerField()


class Census2010Age(models.Model):
    geoid = models.ForeignKey('geo.StateCensusTract', to_field='geoid',
                              unique=True, db_index=True, primary_key=True)

    total_pop = models.IntegerField()
    under_five = models.IntegerField()
    five_nine = models.IntegerField()
    ten_fourteen = models.IntegerField()
    fifteen_seventeen = models.IntegerField()
    eighteen_nineteen = models.IntegerField()
    twenty = models.IntegerField()
    twentyone = models.IntegerField()
    twentytwo_twentyfour = models.IntegerField()
    twentyfive_twentynine = models.IntegerField()
    thirty_thirtyfour = models.IntegerField()
    thirtyfive_thirtynine = models.IntegerField()
    forty_fortyfour = models.IntegerField()
    fortyfive_fortynine = models.IntegerField()
    fifty_fiftyfour = models.IntegerField()
    fiftyfive_fiftynine = models.IntegerField()
    sixty_sixtyone = models.IntegerField()
    sixtytwo_sixtyfour = models.IntegerField()
    sixtyfive_sixtysix = models.IntegerField()
    sixtyseven_sixynine = models.IntegerField()
    seventy_seventyfour = models.IntegerField()
    seventyfive_seventynine = models.IntegerField()
    eighty_eightyfour = models.IntegerField()
    eightyfive_up = models.IntegerField()


class Census2010RaceStats(models.Model):
    geoid = models.ForeignKey('geo.StateCensusTract', to_field='geoid',
                              unique=True, db_index=True, primary_key=True)

    total_pop = models.IntegerField()
    hispanic = models.IntegerField()
    non_hisp_white_only = models.IntegerField()
    non_hisp_black_only = models.IntegerField()
    non_hisp_asian_only = models.IntegerField()

    hispanic_perc = models.FloatField()
    non_hisp_white_only_perc = models.FloatField()
    non_hisp_black_only_perc = models.FloatField()
    non_hisp_asian_only_perc = models.FloatField()

    def auto_fields(self):
        if self.total_pop:
            self.hispanic_perc = 1.0 * self.hispanic / self.total_pop
            self.non_hisp_white_only_perc = (1.0 * self.non_hisp_white_only
                                             / self.total_pop)
            self.non_hisp_black_only_perc = (1.0 * self.non_hisp_black_only
                                             / self.total_pop)
            self.non_hisp_asian_only_perc = (1.0 * self.non_hisp_asian_only
                                             / self.total_pop)
        else:
            self.hispanic_perc = 1.00
            self.non_hisp_white_only_perc = 1.00
            self.non_hisp_black_only_perc = 1.00
            self.non_hisp_asian_only_perc = 1.00

    def save(self):
        self.auto_fields()
        super(Census2010RaceStats, self).save()
