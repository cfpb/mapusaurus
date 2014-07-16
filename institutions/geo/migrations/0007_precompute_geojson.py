# -*- coding: utf-8 -*-
import json

from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for geo in orm.StateCensusTract.objects.iterator():
            geojson = {"type": "Feature", "geometry": "$_$"}
            geojson['properties'] = {
                'statefp': geo.statefp,
                'countyfp': geo.countyfp,
                'tractce': geo.tractce,
                'geoid': geo.geoid,
                'name': geo.name,
                'namelsad': geo.namelsad,
                'aland': geo.aland,
                'awater': geo.awater,
                'intptlat': geo.intptlat,
                'intptlon': geo.intptlon,
                'minlat': geo.minlat,
                'maxlat': geo.maxlat,
                'minlon': geo.minlon,
                'maxlon': geo.maxlon
            }
            geojson = json.dumps(geojson)
            geojson = geojson.replace(
                '"$_$"',
                geo.geom.simplify(preserve_topology=True).geojson)
            geo.geojson = geojson
            geo.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract'},
            'aland': ('django.db.models.fields.FloatField', [], {}),
            'awater': ('django.db.models.fields.FloatField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'funcstat': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'geoid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '11'}),
            'geojson': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intptlat': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'intptlon': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'maxlon': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'minlat': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'minlon': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'mtfcc': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'namelsad': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['geo']
    symmetrical = True
