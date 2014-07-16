import json

from django.contrib.gis.db import models


class Geo(models.Model):
    STATE_TYPE, COUNTY_TYPE, TRACT_TYPE = range(1, 4)
    TYPES = [(STATE_TYPE, 'State'), (COUNTY_TYPE, 'County'),
             (TRACT_TYPE, 'Census Tract')]

    geoid = models.CharField(max_length=20, primary_key=True)
    geo_type = models.PositiveIntegerField(choices=TYPES)
    name = models.CharField(max_length=50)

    state = models.CharField(max_length=2)
    county = models.CharField(max_length=3, null=True)
    tract = models.CharField(max_length=6, null=True)

    geom = models.MultiPolygonField(srid=4269)

    minlat = models.FloatField()
    maxlat = models.FloatField()
    minlon = models.FloatField()
    maxlon = models.FloatField()
    centlat = models.FloatField()
    centlon = models.FloatField()

    objects = models.GeoManager()

    def as_geojson(self):
        # geometry is a placeholder, as we'll be inserting a pre-serialized
        # json string
        geojson = {"type": "Feature", "geometry": "$_$"}
        geojson['properties'] = {
            'geoid': self.geoid,
            'geoType': Geo.TYPES[self.geo_type - 1],    # 1-indexed
            'name': self.name,
            'state': self.state,
            'county': self.county,
            'tract': self.tract,
            'minlat': self.minlat,
            'maxlat': self.maxlat,
            'minlon': self.minlon,
            'maxlon': self.maxlon,
            'centlat': self.centlat,
            'centlon': self.centlon
        }
        geojson = json.dumps(geojson)
        geojson = geojson.replace(
            '"$_$"',
            self.geom.simplify(preserve_topology=True).geojson)
        return geojson
