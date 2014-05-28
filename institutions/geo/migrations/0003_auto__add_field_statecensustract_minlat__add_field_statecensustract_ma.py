# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'StateCensusTract.minlat'
        db.add_column(u'geo_statecensustract', 'minlat',
                      self.gf('django.db.models.fields.FloatField')(null=True, db_index=True),
                      keep_default=False)

        # Adding field 'StateCensusTract.maxlat'
        db.add_column(u'geo_statecensustract', 'maxlat',
                      self.gf('django.db.models.fields.FloatField')(null=True, db_index=True),
                      keep_default=False)

        # Adding field 'StateCensusTract.minlon'
        db.add_column(u'geo_statecensustract', 'minlon',
                      self.gf('django.db.models.fields.FloatField')(null=True, db_index=True),
                      keep_default=False)

        # Adding field 'StateCensusTract.maxlon'
        db.add_column(u'geo_statecensustract', 'maxlon',
                      self.gf('django.db.models.fields.FloatField')(null=True, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'StateCensusTract.minlat'
        db.delete_column(u'geo_statecensustract', 'minlat')

        # Deleting field 'StateCensusTract.maxlat'
        db.delete_column(u'geo_statecensustract', 'maxlat')

        # Deleting field 'StateCensusTract.minlon'
        db.delete_column(u'geo_statecensustract', 'minlon')

        # Deleting field 'StateCensusTract.maxlon'
        db.delete_column(u'geo_statecensustract', 'maxlon')


    models = {
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract'},
            'aland': ('django.db.models.fields.FloatField', [], {}),
            'awater': ('django.db.models.fields.FloatField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'funcstat': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'geoid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '11'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intptlat': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'intptlon': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'maxlon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'minlat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'minlon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'mtfcc': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'namelsad': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['geo']
