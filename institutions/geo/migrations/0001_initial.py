# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StateCensusTract'
        db.create_table(u'geo_statecensustract', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('statefp', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('countyfp', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('tractce', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('geoid', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('namelsad', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('mtfcc', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('funcstat', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('aland', self.gf('django.db.models.fields.FloatField')()),
            ('awater', self.gf('django.db.models.fields.FloatField')()),
            ('intptlat', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('intptlon', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=4269)),
        ))
        db.send_create_signal(u'geo', ['StateCensusTract'])


    def backwards(self, orm):
        # Deleting model 'StateCensusTract'
        db.delete_table(u'geo_statecensustract')


    models = {
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract'},
            'aland': ('django.db.models.fields.FloatField', [], {}),
            'awater': ('django.db.models.fields.FloatField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'funcstat': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'geoid': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intptlat': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'intptlon': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'mtfcc': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'namelsad': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['geo']