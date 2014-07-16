"""Note that we use field names corresponding to those found in the census
data. This does not represent the authors' endorsement of those distinctions
nor categories."""
from django.db import models


class Census2010Race(models.Model):
    """Race population fields, pulled from Summary1, file 3"""
    geoid = models.OneToOneField('geo.Geo', primary_key=True)

    total_pop = models.IntegerField()
    white_alone = models.IntegerField()
    black_alone = models.IntegerField()
    amind_alone = models.IntegerField()
    asian_alone = models.IntegerField()
    pacis_alone = models.IntegerField()
    other_alone = models.IntegerField()
    two_or_more = models.IntegerField()


class Census2010HispanicOrigin(models.Model):
    """Hispanic/Latino population fields, pulled from Summary1, file 3"""
    geoid = models.OneToOneField('geo.Geo', primary_key=True)

    total_pop = models.IntegerField()
    non_hispanic = models.IntegerField()
    hispanic = models.IntegerField()


class Census2010Sex(models.Model):
    """Sex/Gender population fields, pulled from Summary1, file 4"""
    geoid = models.OneToOneField('geo.Geo', primary_key=True)

    total_pop = models.IntegerField()
    male = models.IntegerField()
    female = models.IntegerField()


class Census2010Age(models.Model):
    """Population grouped by age, pulled from Summary1, file 4. We use the
    exact breakdown as in the census"""
    geoid = models.OneToOneField('geo.Geo', primary_key=True)

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
    """These fields and calculated fields give a slightly more nuanced view of
    the above data, particularly segmenting out minority groups by race and
    hispanic/latino"""
    geoid = models.OneToOneField('geo.Geo', primary_key=True)

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

    def save(self, *args, **kwargs):
        self.auto_fields()
        super(Census2010RaceStats, self).save(*args, **kwargs)


class Census2010Households(models.Model):
    """Number of households per census tract, pulled from Summary1, file 5"""
    geoid = models.OneToOneField('geo.Geo', primary_key=True)

    total = models.IntegerField(
        help_text="Total number of households in census tract. P0180001")

    total_family = models.IntegerField(
        help_text=("Total number of family households. Combined with "
                   + "total_nonfamily to check total. P0180002"))
    husband_wife = models.IntegerField(
        help_text=("Husband-wife family households. Combine with "
                   + "total_family_other to check total_family. P0180003"))
    total_family_other = models.IntegerField(
        help_text=("'Other' family households. Combine with husband_wife "
                   "to check total_family. P0180004"))
    male_no_wife = models.IntegerField(
        help_text=("Male householder, no wife present. Combine with "
                   + "female_no_husband to check total_family_other. "
                   + "P0180005"))
    female_no_husband = models.IntegerField(
        help_text=("Female householder, no husband present. Combine with "
                   + "male_no_wife to check total_family_other. P0180006"))

    total_nonfamily = models.IntegerField(
        help_text=("Total number of nonfamily households. Combine with "
                   + "total_family to check total. P0180007"))
    living_alone = models.IntegerField(
        help_text=("Householder living alone. Combine with not_living_alone "
                   + "to check total_nonfamily. P0180008"))
    not_living_alone = models.IntegerField(
        help_text=("Householder not living alone. Combine with living_alone "
                   + "to check total_nonfamily. P0180009"))
