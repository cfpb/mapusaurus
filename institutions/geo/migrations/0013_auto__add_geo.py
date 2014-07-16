# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Geo'
        db.create_table(u'geo_geo', (
            ('geoid', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('geo_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('county', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('tract', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=4269)),
            ('minlat', self.gf('django.db.models.fields.FloatField')()),
            ('maxlat', self.gf('django.db.models.fields.FloatField')()),
            ('minlon', self.gf('django.db.models.fields.FloatField')()),
            ('maxlon', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'geo', ['Geo'])


    def backwards(self, orm):
        # Deleting model 'Geo'
        db.delete_table(u'geo_geo')


    models = {
        u'geo.geo': {
            'Meta': {'object_name': 'Geo'},
            'county': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'geo_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'geoid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {}),
            'maxlon': ('django.db.models.fields.FloatField', [], {}),
            'minlat': ('django.db.models.fields.FloatField', [], {}),
            'minlon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tract': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract', 'index_together': "[('statefp', 'countyfp'), ('minlat', 'minlon'), ('minlat', 'maxlon'), ('maxlat', 'minlon'), ('maxlat', 'maxlon')]"},
            'aland': ('django.db.models.fields.FloatField', [], {}),
            'awater': ('django.db.models.fields.FloatField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
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