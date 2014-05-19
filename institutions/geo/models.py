# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class StateCensusTract(models.Model):
    """
        This model represents the shapefile for census tracts per state. This
        model is auto-generated using the ogrinspect Django command.
    """

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)
    geoid = models.CharField(max_length=11)
    name = models.CharField(max_length=7)
    namelsad = models.CharField(max_length=20)
    mtfcc = models.CharField(max_length=5)
    funcstat = models.CharField(max_length=1)
    aland = models.FloatField()
    awater = models.FloatField()
    intptlat = models.CharField(max_length=11)
    intptlon = models.CharField(max_length=12)
    geom = models.MultiPolygonField(srid=4269)
    objects = models.GeoManager()

    def __str__(self):
        return '%s (county: %s, state: %s)' % (
            self.namelsad, self.countyfp, self.statefp)

# Auto-generated `LayerMapping` dictionary for CensusTract model
censustract_mapping = {
    'statefp': 'STATEFP',
    'countyfp': 'COUNTYFP',
    'tractce': 'TRACTCE',
    'geoid': 'GEOID',
    'name': 'NAME',
    'namelsad': 'NAMELSAD',
    'mtfcc': 'MTFCC',
    'funcstat': 'FUNCSTAT',
    'aland': 'ALAND',
    'awater': 'AWATER',
    'intptlat': 'INTPTLAT',
    'intptlon': 'INTPTLON',
    'geom': 'MULTIPOLYGON',
}
