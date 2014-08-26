# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LendingStats'
        db.create_table(u'hmda_lendingstats', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lender', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('geoid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Geo'])),
            ('median_per_tract', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'hmda', ['LendingStats'])

        # Adding unique constraint on 'LendingStats', fields ['lender', 'geoid']
        db.create_unique(u'hmda_lendingstats', ['lender', 'geoid_id'])

        # Adding index on 'LendingStats', fields ['lender', 'geoid']
        db.create_index(u'hmda_lendingstats', ['lender', 'geoid_id'])


    def backwards(self, orm):
        # Removing index on 'LendingStats', fields ['lender', 'geoid']
        db.delete_index(u'hmda_lendingstats', ['lender', 'geoid_id'])

        # Removing unique constraint on 'LendingStats', fields ['lender', 'geoid']
        db.delete_unique(u'hmda_lendingstats', ['lender', 'geoid_id'])

        # Deleting model 'LendingStats'
        db.delete_table(u'hmda_lendingstats')


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
        },
        u'hmda.hmdarecord': {
            'Meta': {'object_name': 'HMDARecord', 'index_together': "[('statefp', 'countyfp'), ('statefp', 'countyfp', 'lender'), ('statefp', 'countyfp', 'action_taken', 'lender'), ('geoid', 'lender')]"},
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
        },
        u'hmda.lendingstats': {
            'Meta': {'unique_together': "[('lender', 'geoid')]", 'object_name': 'LendingStats', 'index_together': "[('lender', 'geoid')]"},
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Geo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lender': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'median_per_tract': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['hmda']