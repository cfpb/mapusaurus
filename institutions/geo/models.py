import json

from django.contrib.gis.db import models


class Geo(models.Model):
    STATE_TYPE, COUNTY_TYPE, TRACT_TYPE, METRO_TYPE, MICRO_TYPE = range(1, 6)
    METDIV_TYPE, = range(6, 7)
    TYPES = [(STATE_TYPE, 'State'), (COUNTY_TYPE, 'County'),
             (TRACT_TYPE, 'Census Tract'), (METRO_TYPE, 'Metropolitan'),
             (MICRO_TYPE, 'Micropolitan'),
             (METDIV_TYPE, 'Metropolitan Division')]

    geoid = models.CharField(max_length=20, primary_key=True)
    geo_type = models.PositiveIntegerField(choices=TYPES)
    name = models.CharField(max_length=50)

    state = models.CharField(max_length=2, null=True)
    county = models.CharField(max_length=3, null=True)
    tract = models.CharField(max_length=6, null=True)
    csa = models.CharField(max_length=3, null=True,
                           help_text='Combined Statistical Area')
    cbsa = models.CharField(max_length=5, null=True,
                            help_text='Core Based Statistical Area')
    metdiv = models.CharField(max_length=5, null=True,
                              help_text='Metro Division')

    geom = models.MultiPolygonField(srid=4269)

    minlat = models.FloatField()
    maxlat = models.FloatField()
    minlon = models.FloatField()
    maxlon = models.FloatField()
    centlat = models.FloatField()
    centlon = models.FloatField()

    objects = models.GeoManager()

    class Meta:
        index_together = [("geo_type", "minlat", "minlon"),
                          ("geo_type", "minlat", "maxlon"),
                          ("geo_type", "maxlat", "minlon"),
                          ("geo_type", "maxlat", "maxlon"),
                          ("geo_type", "centlat", "centlon")]

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
            'cbsa': self.cbsa,
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
