# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ZipcodeCityStateYear'
        db.create_table(u'respondents_zipcodecitystateyear', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.IntegerField')()),
            ('plus_four', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'respondents', ['ZipcodeCityStateYear'])

        # Adding unique constraint on 'ZipcodeCityStateYear', fields ['zip_code', 'city']
        db.create_unique(u'respondents_zipcodecitystateyear', ['zip_code', 'city', 'year'])

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
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('respondent_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondents.Agency'])),
            ('institution_id', self.gf('django.db.models.fields.CharField')(max_length=11, primary_key=True)),
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

        # Adding unique constraint on 'Institution', fields ['institution_id', 'year']
        db.create_unique(u'respondents_institution', ['institution_id', 'year'])

        # Adding index on 'Institution', fields ['institution_id', 'year']
        db.create_index(u'respondents_institution', ['institution_id', 'year'])

        # Adding model 'LenderHierarchy'
        db.create_table(u'respondents_lenderhierarchy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondents.Institution'])),
            ('organization_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'respondents', ['LenderHierarchy'])

        # Adding model 'Branch'
        db.create_table(u'respondents_branch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondents.Institution'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2)),
            ('zipcode', self.gf('django.db.models.fields.IntegerField')()),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('lon', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'respondents', ['Branch'])


    def backwards(self, orm):
        # Removing index on 'Institution', fields ['institution_id', 'year']
        db.delete_index(u'respondents_institution', ['institution_id', 'year'])

        # Removing unique constraint on 'Institution', fields ['institution_id', 'year']
        db.delete_unique(u'respondents_institution', ['institution_id', 'year'])

        # Removing unique constraint on 'ZipcodeCityState', fields ['zip_code', 'city']
        db.delete_unique(u'respondents_zipcodecitystateyear', ['zip_code', 'city','year'])

        # Deleting model 'ZipcodeCityState'
        db.delete_table(u'respondents_zipcodecitystateyear')

        # Deleting model 'Agency'
        db.delete_table(u'respondents_agency')

        # Deleting model 'ParentInstitution'
        db.delete_table(u'respondents_parentinstitution')

        # Deleting model 'Institution'
        db.delete_table(u'respondents_institution')

        # Deleting model 'LenderHierarchy'
        db.delete_table(u'respondents_lenderhierarchy')

        # Deleting model 'Branch'
        db.delete_table(u'respondents_branch')


    models = {
        u'respondents.agency': {
            'Meta': {'object_name': 'Agency'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hmda_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'respondents.branch': {
            'Meta': {'object_name': 'Branch'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.Institution']"}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {}),
            'zipcode': ('django.db.models.fields.IntegerField', [], {})
        },
        u'respondents.institution': {
            'Meta': {'unique_together': "(('institution_id', 'year'),)", 'object_name': 'Institution', 'index_together': "[['institution_id', 'year']]"},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.Agency']"}),
            'assets': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'institution_id': ('django.db.models.fields.CharField', [], {'max_length': '11', 'primary_key': 'True'}),
            'mailing_address': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'non_reporting_parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['respondents.ParentInstitution']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['respondents.Institution']"}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'top_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descendants'", 'null': 'True', 'to': u"orm['respondents.ParentInstitution']"}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {}),
            'zip_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.ZipcodeCityState']"})
        },
        u'respondents.lenderhierarchy': {
            'Meta': {'object_name': 'LenderHierarchy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.Institution']"}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {})
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
        u'respondents.zipcodecitystateyear': {
            'Meta': {'unique_together': "(('zip_code', 'city'),)", 'object_name': 'ZipcodeCityState'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plus_four': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.SmallIntegerField', [],{})
        }
    }

    complete_apps = ['respondents']