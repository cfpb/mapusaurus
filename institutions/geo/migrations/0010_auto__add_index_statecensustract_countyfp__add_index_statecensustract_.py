# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'StateCensusTract', fields ['countyfp']
        db.create_index(u'geo_statecensustract', ['countyfp'])

        # Adding index on 'StateCensusTract', fields ['statefp']
        db.create_index(u'geo_statecensustract', ['statefp'])

        # Adding index on 'StateCensusTract', fields ['statefp', 'countyfp']
        db.create_index(u'geo_statecensustract', ['statefp', 'countyfp'])


    def backwards(self, orm):
        # Removing index on 'StateCensusTract', fields ['statefp', 'countyfp']
        db.delete_index(u'geo_statecensustract', ['statefp', 'countyfp'])

        # Removing index on 'StateCensusTract', fields ['statefp']
        db.delete_index(u'geo_statecensustract', ['statefp'])

        # Removing index on 'StateCensusTract', fields ['countyfp']
        db.delete_index(u'geo_statecensustract', ['countyfp'])


    models = {
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract', 'index_together': "[('statefp', 'countyfp')]"},
            'aland': ('django.db.models.fields.FloatField', [], {}),
            'awater': ('django.db.models.fields.FloatField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'funcstat': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'geoid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '11'}),
            'geojson': ('django.db.models.fields.TextField', [], {}),
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
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['geo']