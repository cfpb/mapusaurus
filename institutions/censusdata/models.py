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
