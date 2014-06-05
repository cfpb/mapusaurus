# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'HMDARecord.census_tract'
        db.delete_column(u'hmda_hmdarecord', 'census_tract')

        # Renaming field 'HMDARecord.county_code'
        db.rename_column(u'hmda_hmdarecord', 'county_code', 'countyfp')

        # Renaming field 'HMDARecord.state_code'
        db.rename_column(u'hmda_hmdarecord', 'state_code', 'statefp')

    def backwards(self, orm):
        # Renaming field 'HMDARecord.countyfp'
        db.rename_column(u'hmda_hmdarecord', 'countyfp', 'county_code')

        # Renaming field 'HMDARecord.statefp'
        db.rename_column(u'hmda_hmdarecord', 'statefp', 'state_code')

        # Adding field 'HMDARecord.census_tract'
        db.add_column(u'hmda_hmdarecord', 'census_tract',
                      self.gf('django.db.models.fields.CharField')(default='000000', max_length=6),
                      keep_default=False)

    models = {
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract'},
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
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        u'hmda.hmdarecord': {
            'Meta': {'object_name': 'HMDARecord'},
            'action_taken': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'agency_code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'as_of_year': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lender': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'loan_amount_000s': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'})
        }
    }

    complete_apps = ['hmda']
