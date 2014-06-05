# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HMDARecord'
        db.create_table(u'hmda_hmdarecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('as_of_year', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('respondent_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('agency_code', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('loan_amount_000s', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('action_taken', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('state_code', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
            ('county_code', self.gf('django.db.models.fields.CharField')(max_length=3, db_index=True)),
            ('census_tract', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('lender', self.gf('django.db.models.fields.CharField')(max_length=11, db_index=True)),
            ('geoid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.StateCensusTract'], to_field='geoid')),
        ))
        db.send_create_signal(u'hmda', ['HMDARecord'])


    def backwards(self, orm):
        # Deleting model 'HMDARecord'
        db.delete_table(u'hmda_hmdarecord')


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
            'census_tract': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'county_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lender': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'loan_amount_000s': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'state_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'})
        }
    }

    complete_apps = ['hmda']