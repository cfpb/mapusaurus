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
            ('geo_type', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=3, null=True)),
            ('tract', self.gf('django.db.models.fields.CharField')(max_length=6, null=True)),
            ('csa', self.gf('django.db.models.fields.CharField')(max_length=3, null=True)),
            ('cbsa', self.gf('django.db.models.fields.CharField')(max_length=5, null=True)),
            ('metdiv', self.gf('django.db.models.fields.CharField')(max_length=5, null=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=4269)),
            ('minlat', self.gf('django.db.models.fields.FloatField')()),
            ('maxlat', self.gf('django.db.models.fields.FloatField')()),
            ('minlon', self.gf('django.db.models.fields.FloatField')()),
            ('maxlon', self.gf('django.db.models.fields.FloatField')()),
            ('centlat', self.gf('django.db.models.fields.FloatField')()),
            ('centlon', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'geo', ['Geo'])

        # Adding index on 'Geo', fields ['geo_type', 'minlat', 'minlon']
        db.create_index(u'geo_geo', ['geo_type', 'minlat', 'minlon'])

        # Adding index on 'Geo', fields ['geo_type', 'minlat', 'maxlon']
        db.create_index(u'geo_geo', ['geo_type', 'minlat', 'maxlon'])

        # Adding index on 'Geo', fields ['geo_type', 'maxlat', 'minlon']
        db.create_index(u'geo_geo', ['geo_type', 'maxlat', 'minlon'])

        # Adding index on 'Geo', fields ['geo_type', 'maxlat', 'maxlon']
        db.create_index(u'geo_geo', ['geo_type', 'maxlat', 'maxlon'])

        # Adding index on 'Geo', fields ['geo_type', 'centlat', 'centlon']
        db.create_index(u'geo_geo', ['geo_type', 'centlat', 'centlon'])

        # Adding index on 'Geo', fields ['geo_type', 'cbsa']
        db.create_index(u'geo_geo', ['geo_type', 'cbsa'])


    def backwards(self, orm):
        # Removing index on 'Geo', fields ['geo_type', 'cbsa']
        db.delete_index(u'geo_geo', ['geo_type', 'cbsa'])

        # Removing index on 'Geo', fields ['geo_type', 'centlat', 'centlon']
        db.delete_index(u'geo_geo', ['geo_type', 'centlat', 'centlon'])

        # Removing index on 'Geo', fields ['geo_type', 'maxlat', 'maxlon']
        db.delete_index(u'geo_geo', ['geo_type', 'maxlat', 'maxlon'])

        # Removing index on 'Geo', fields ['geo_type', 'maxlat', 'minlon']
        db.delete_index(u'geo_geo', ['geo_type', 'maxlat', 'minlon'])

        # Removing index on 'Geo', fields ['geo_type', 'minlat', 'maxlon']
        db.delete_index(u'geo_geo', ['geo_type', 'minlat', 'maxlon'])

        # Removing index on 'Geo', fields ['geo_type', 'minlat', 'minlon']
        db.delete_index(u'geo_geo', ['geo_type', 'minlat', 'minlon'])

        # Deleting model 'Geo'
        db.delete_table(u'geo_geo')


    models = {
        u'geo.geo': {
            'Meta': {'object_name': 'Geo', 'index_together': "[('geo_type', 'minlat', 'minlon'), ('geo_type', 'minlat', 'maxlon'), ('geo_type', 'maxlat', 'minlon'), ('geo_type', 'maxlat', 'maxlon'), ('geo_type', 'centlat', 'centlon'), ('geo_type', 'cbsa')]"},
            'cbsa': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'centlat': ('django.db.models.fields.FloatField', [], {}),
            'centlon': ('django.db.models.fields.FloatField', [], {}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'csa': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'geo_type': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'geoid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {}),
            'maxlon': ('django.db.models.fields.FloatField', [], {}),
            'metdiv': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'minlat': ('django.db.models.fields.FloatField', [], {}),
            'minlon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'tract': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'})
        }
    }

    complete_apps = ['geo']