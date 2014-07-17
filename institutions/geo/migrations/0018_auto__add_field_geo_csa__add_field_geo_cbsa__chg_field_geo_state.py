# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Geo.csa'
        db.add_column(u'geo_geo', 'csa',
                      self.gf('django.db.models.fields.CharField')(max_length=3, null=True),
                      keep_default=False)

        # Adding field 'Geo.cbsa'
        db.add_column(u'geo_geo', 'cbsa',
                      self.gf('django.db.models.fields.CharField')(max_length=5, null=True),
                      keep_default=False)


        # Changing field 'Geo.state'
        db.alter_column(u'geo_geo', 'state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True))

    def backwards(self, orm):
        # Deleting field 'Geo.csa'
        db.delete_column(u'geo_geo', 'csa')

        # Deleting field 'Geo.cbsa'
        db.delete_column(u'geo_geo', 'cbsa')


        # Changing field 'Geo.state'
        db.alter_column(u'geo_geo', 'state', self.gf('django.db.models.fields.CharField')(default='NA', max_length=2))

    models = {
        u'geo.geo': {
            'Meta': {'object_name': 'Geo', 'index_together': "[('geo_type', 'minlat', 'minlon'), ('geo_type', 'minlat', 'maxlon'), ('geo_type', 'maxlat', 'minlon'), ('geo_type', 'maxlat', 'maxlon'), ('geo_type', 'centlat', 'centlon')]"},
            'cbsa': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'centlat': ('django.db.models.fields.FloatField', [], {}),
            'centlon': ('django.db.models.fields.FloatField', [], {}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'csa': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'geo_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'geoid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {}),
            'maxlon': ('django.db.models.fields.FloatField', [], {}),
            'minlat': ('django.db.models.fields.FloatField', [], {}),
            'minlon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'tract': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'})
        }
    }

    complete_apps = ['geo']