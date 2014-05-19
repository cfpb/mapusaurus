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
