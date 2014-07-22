# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'HMDARecord.geoid'
        db.alter_column(u'hmda_hmdarecord', 'geoid_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Geo']))

    def backwards(self, orm):

        # Changing field 'HMDARecord.geoid'
        db.alter_column(u'hmda_hmdarecord', 'geoid_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.StateCensusTract'], to_field='geoid'))

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
        },
        u'hmda.hmdarecord': {
            'Meta': {'object_name': 'HMDARecord', 'index_together': "[('statefp', 'countyfp'), ('statefp', 'countyfp', 'lender'), ('statefp', 'countyfp', 'action_taken', 'lender')]"},
            'action_taken': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'agency_code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'as_of_year': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Geo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lender': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'loan_amount_000s': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'})
        }
    }

    complete_apps = ['hmda']