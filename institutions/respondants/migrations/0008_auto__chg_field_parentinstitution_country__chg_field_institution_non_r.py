# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ParentInstitution.country'
        db.alter_column('respondants_parentinstitution', 'country', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Institution.non_reporting_parent'
        db.alter_column('respondants_institution', 'non_reporting_parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.ParentInstitution']))

        # Changing field 'Institution.parent'
        db.alter_column('respondants_institution', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.Institution']))

    def backwards(self, orm):

        # Changing field 'ParentInstitution.country'
        db.alter_column('respondants_parentinstitution', 'country', self.gf('django.db.models.fields.CharField')(default='', max_length=40))

        # Changing field 'Institution.non_reporting_parent'
        db.alter_column('respondants_institution', 'non_reporting_parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.Institution']))

        # Changing field 'Institution.parent'
        db.alter_column('respondants_institution', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.ParentInstitution']))

    models = {
        'respondants.agency': {
            'Meta': {'object_name': 'Agency'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hmda_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'respondants.institution': {
            'Meta': {'unique_together': "(('ffiec_id', 'agency'),)", 'object_name': 'Institution', 'index_together': "[['ffiec_id', 'agency', 'year']]"},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['respondants.Agency']"}),
            'ffiec_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_address': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'non_reporting_parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['respondants.ParentInstitution']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['respondants.Institution']"}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'top_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descendants'", 'null': 'True', 'to': "orm['respondants.ParentInstitution']"}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {}),
            'zip_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['respondants.ZipcodeCityState']"})
        },
        'respondants.parentinstitution': {
            'Meta': {'object_name': 'ParentInstitution'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'respondants.zipcodecitystate': {
            'Meta': {'unique_together': "(('zip_code', 'city'),)", 'object_name': 'ZipcodeCityState'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plus_four': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['respondants']