# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LenderHierarchy'
        db.create_table(u'respondents_lenderhierarchy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondents.Agency'])),
            ('respondent_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('organization_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'respondents', ['LenderHierarchy'])


    def backwards(self, orm):
        # Deleting model 'LenderHierarchy'
        db.delete_table(u'respondents_lenderhierarchy')


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
        u'respondents.lenderhierarchy': {
            'Meta': {'object_name': 'LenderHierarchy'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['respondents.Agency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_id': ('django.db.models.fields.IntegerField', [], {}),
            'respondent_id': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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