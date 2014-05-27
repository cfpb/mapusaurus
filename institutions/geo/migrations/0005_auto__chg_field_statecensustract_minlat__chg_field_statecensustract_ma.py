# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'StateCensusTract.minlat'
        db.alter_column(u'geo_statecensustract', 'minlat', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'StateCensusTract.manlon'
        db.alter_column(u'geo_statecensustract', 'manlon', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'StateCensusTract.maxlat'
        db.alter_column(u'geo_statecensustract', 'maxlat', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'StateCensusTract.minlon'
        db.alter_column(u'geo_statecensustract', 'minlon', self.gf('django.db.models.fields.FloatField')(default=0))

    def backwards(self, orm):

        # Changing field 'StateCensusTract.minlat'
        db.alter_column(u'geo_statecensustract', 'minlat', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'StateCensusTract.manlon'
        db.alter_column(u'geo_statecensustract', 'manlon', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'StateCensusTract.maxlat'
        db.alter_column(u'geo_statecensustract', 'maxlat', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'StateCensusTract.minlon'
        db.alter_column(u'geo_statecensustract', 'minlon', self.gf('django.db.models.fields.FloatField')(null=True))

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
            'manlon': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
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