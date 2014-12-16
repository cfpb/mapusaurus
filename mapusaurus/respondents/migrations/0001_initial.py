# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ZipcodeCityState'
        db.create_table(u'respondents_zipcodecitystate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.IntegerField')()),
            ('plus_four', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2)),
        ))
        db.send_create_signal(u'respondents', ['ZipcodeCityState'])

        # Adding unique constraint on 'ZipcodeCityState', fields ['zip_code', 'city']
        db.create_unique(u'respondents_zipcodecitystate', ['zip_code', 'city'])

        # Adding model 'Agency'
        db.create_table(u'respondents_agency', (
            ('hmda_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('acronym', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'respondents', ['Agency'])

        # Adding model 'ParentInstitution'
        db.create_table(u'respondents_parentinstitution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('rssd_id', self.gf('django.db.models.fields.CharField')(max_length=10, unique=True, null=True)),
        ))
        db.send_create_signal(u'respondents', ['ParentInstitution'])

        # Adding model 'Institution'
        db.create_table(u'respondents_institution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('respondent_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondents.Agency'])),
            ('tax_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('mailing_address', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('zip_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondents.ZipcodeCityState'])),
            ('assets', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('rssd_id', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['respondents.Institution'])),
            ('non_reporting_parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['respondents.ParentInstitution'])),
            ('top_holder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descendants', null=True, to=orm['respondents.ParentInstitution'])),
        ))
        db.send_create_signal(u'respondents', ['Institution'])

        # Adding unique constraint on 'Institution', fields ['respondent_id', 'agency', 'year']
        db.create_unique(u'respondents_institution', ['respondent_id', 'agency_id', 'year'])

        # Adding index on 'Institution', fields ['respondent_id', 'agency', 'year']
        db.create_index(u'respondents_institution', ['respondent_id', 'agency_id', 'year'])


    def backwards(self, orm):
        # Removing index on 'Institution', fields ['respondent_id', 'agency', 'year']
        db.delete_index(u'respondents_institution', ['respondent_id', 'agency_id', 'year'])

        # Removing unique constraint on 'Institution', fields ['respondent_id', 'agency', 'year']
        db.delete_unique(u'respondents_institution', ['respondent_id', 'agency_id', 'year'])

        # Removing unique constraint on 'ZipcodeCityState', fields ['zip_code', 'city']
        db.delete_unique(u'respondents_zipcodecitystate', ['zip_code', 'city'])

        # Deleting model 'ZipcodeCityState'
        db.delete_table(u'respondents_zipcodecitystate')

        # Deleting model 'Agency'
        db.delete_table(u'respondents_agency')

        # Deleting model 'ParentInstitution'
        db.delete_table(u'respondents_parentinstitution')

        # Deleting model 'Institution'
        db.delete_table(u'respondents_institution')


    models = {
        u'respondents.agency': {
            'Meta': {'object_name': 'Agency'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hmda_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'respondents.institution': {
            'Meta': {'unique_together': "(('respondent_id', 'agency', 'year'),)", 'object_name': 'Institution', 'index_together': "[['respondent_id', 'agency', 'year']]"},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.Agency']"}),
            'assets': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_address': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'non_reporting_parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['respondents.ParentInstitution']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['respondents.Institution']"}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'top_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descendants'", 'null': 'True', 'to': u"orm['respondents.ParentInstitution']"}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {}),
            'zip_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.ZipcodeCityState']"})
        },
        u'respondents.parentinstitution': {
            'Meta': {'object_name': 'ParentInstitution'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'respondents.zipcodecitystate': {
            'Meta': {'unique_together': "(('zip_code', 'city'),)", 'object_name': 'ZipcodeCityState'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plus_four': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['respondents']