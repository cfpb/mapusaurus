# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Census2010Race'
        db.create_table(u'censusdata_census2010race', (
            ('geoid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.StateCensusTract'], to_field='geoid', unique=True, primary_key=True)),
            ('total_pop', self.gf('django.db.models.fields.IntegerField')()),
            ('white_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('black_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('amind_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('asian_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('pacis_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('other_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('two_or_more', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010Race'])


    def backwards(self, orm):
        # Deleting model 'Census2010Race'
        db.delete_table(u'censusdata_census2010race')


    models = {
        u'censusdata.census2010race': {
            'Meta': {'object_name': 'Census2010Race'},
            'amind_alone': ('django.db.models.fields.IntegerField', [], {}),
            'asian_alone': ('django.db.models.fields.IntegerField', [], {}),
            'black_alone': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'other_alone': ('django.db.models.fields.IntegerField', [], {}),
            'pacis_alone': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {}),
            'two_or_more': ('django.db.models.fields.IntegerField', [], {}),
            'white_alone': ('django.db.models.fields.IntegerField', [], {})
        },
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
            'mtfcc': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'namelsad': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['censusdata']