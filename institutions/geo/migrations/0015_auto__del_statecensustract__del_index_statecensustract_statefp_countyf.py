# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing index on 'StateCensusTract', fields ['statefp', 'countyfp']
        db.delete_index(u'geo_statecensustract', ['statefp', 'countyfp'])

        # Removing index on 'StateCensusTract', fields ['minlat', 'minlon']
        db.delete_index(u'geo_statecensustract', ['minlat', 'minlon'])

        # Removing index on 'StateCensusTract', fields ['minlat', 'maxlon']
        db.delete_index(u'geo_statecensustract', ['minlat', 'maxlon'])

        # Removing index on 'StateCensusTract', fields ['maxlat', 'minlon']
        db.delete_index(u'geo_statecensustract', ['maxlat', 'minlon'])

        # Removing index on 'StateCensusTract', fields ['maxlat', 'maxlon']
        db.delete_index(u'geo_statecensustract', ['maxlat', 'maxlon'])

        # Deleting model 'StateCensusTract'
        db.delete_table(u'geo_statecensustract')


    def backwards(self, orm):
        # Adding model 'StateCensusTract'
        db.create_table(u'geo_statecensustract', (
            ('intptlat', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('maxlon', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('minlon', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('intptlon', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('funcstat', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('namelsad', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('geojson', self.gf('django.db.models.fields.TextField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('awater', self.gf('django.db.models.fields.FloatField')()),
            ('minlat', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('countyfp', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('maxlat', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('tractce', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=4269)),
            ('mtfcc', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('geoid', self.gf('django.db.models.fields.CharField')(max_length=11, unique=True)),
            ('statefp', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
            ('aland', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'geo', ['StateCensusTract'])

        # Adding index on 'StateCensusTract', fields ['maxlat', 'maxlon']
        db.create_index(u'geo_statecensustract', ['maxlat', 'maxlon'])

        # Adding index on 'StateCensusTract', fields ['maxlat', 'minlon']
        db.create_index(u'geo_statecensustract', ['maxlat', 'minlon'])

        # Adding index on 'StateCensusTract', fields ['minlat', 'maxlon']
        db.create_index(u'geo_statecensustract', ['minlat', 'maxlon'])

        # Adding index on 'StateCensusTract', fields ['minlat', 'minlon']
        db.create_index(u'geo_statecensustract', ['minlat', 'minlon'])

        # Adding index on 'StateCensusTract', fields ['statefp', 'countyfp']
        db.create_index(u'geo_statecensustract', ['statefp', 'countyfp'])


    models = {
        u'geo.geo': {
            'Meta': {'object_name': 'Geo'},
            'centlat': ('django.db.models.fields.FloatField', [], {}),
            'centlon': ('django.db.models.fields.FloatField', [], {}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'geo_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'geoid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {}),
            'maxlon': ('django.db.models.fields.FloatField', [], {}),
            'minlat': ('django.db.models.fields.FloatField', [], {}),
            'minlon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tract': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'})
        }
    }

    complete_apps = ['geo']
