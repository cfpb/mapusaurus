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
            ('loan_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('property_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('loan_purpose', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('owner_occupancy', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('loan_amount_000s', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('preapproval', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('action_taken', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('msamd', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('statefp', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
            ('countyfp', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('census_tract_number', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('applicant_ethnicity', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('co_applicant_ethnicity', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('applicant_race_1', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('applicant_race_2', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('applicant_race_3', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('applicant_race_4', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('applicant_race_5', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('co_applicant_race_1', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('co_applicant_race_2', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('co_applicant_race_3', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('co_applicant_race_4', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('co_applicant_race_5', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('applicant_sex', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('co_applicant_sex', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('applicant_income_000s', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('purchaser_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('denial_reason_1', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('denial_reason_2', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('denial_reason_3', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('rate_spread', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('hoepa_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('lien_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('edit_status', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('sequence_number', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('population', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('minority_population', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('ffieic_median_family_income', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('tract_to_msamd_income', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('number_of_owner_occupied_units', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('number_of_1_to_4_family_units', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('application_date_indicator', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('lender', self.gf('django.db.models.fields.CharField')(max_length=11, db_index=True)),
            ('geoid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Geo'])),
        ))
        db.send_create_signal(u'hmda', ['HMDARecord'])

        # Adding index on 'HMDARecord', fields ['statefp', 'countyfp']
        db.create_index(u'hmda_hmdarecord', ['statefp', 'countyfp'])

        # Adding index on 'HMDARecord', fields ['statefp', 'countyfp', 'lender']
        db.create_index(u'hmda_hmdarecord', ['statefp', 'countyfp', 'lender'])

        # Adding index on 'HMDARecord', fields ['geoid', 'lender']
        db.create_index(u'hmda_hmdarecord', ['geoid_id', 'lender'])

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

        # Removing index on 'HMDARecord', fields ['geoid', 'lender']
        db.delete_index(u'hmda_hmdarecord', ['geoid_id', 'lender'])

        # Removing index on 'HMDARecord', fields ['statefp', 'countyfp', 'lender']
        db.delete_index(u'hmda_hmdarecord', ['statefp', 'countyfp', 'lender'])

        # Removing index on 'HMDARecord', fields ['statefp', 'countyfp']
        db.delete_index(u'hmda_hmdarecord', ['statefp', 'countyfp'])

        # Deleting model 'HMDARecord'
        db.delete_table(u'hmda_hmdarecord')

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
            'Meta': {'object_name': 'HMDARecord', 'index_together': "[('statefp', 'countyfp'), ('statefp', 'countyfp', 'lender'), ('geoid', 'lender')]"},
            'action_taken': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'agency_code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'applicant_ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'applicant_income_000s': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'applicant_race_1': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'applicant_race_2': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'applicant_race_3': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'applicant_race_4': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'applicant_race_5': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'applicant_sex': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'application_date_indicator': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'as_of_year': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'census_tract_number': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'co_applicant_ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'co_applicant_race_1': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'co_applicant_race_2': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'co_applicant_race_3': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'co_applicant_race_4': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'co_applicant_race_5': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'co_applicant_sex': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'denial_reason_1': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'denial_reason_2': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'denial_reason_3': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'edit_status': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'ffieic_median_family_income': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Geo']"}),
            'hoepa_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lender': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'lien_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'loan_amount_000s': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'loan_purpose': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'loan_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'minority_population': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'msamd': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'number_of_1_to_4_family_units': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'number_of_owner_occupied_units': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'owner_occupancy': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'population': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'preapproval': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'property_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'purchaser_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'rate_spread': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'sequence_number': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'tract_to_msamd_income': ('django.db.models.fields.CharField', [], {'max_length': '6'})
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