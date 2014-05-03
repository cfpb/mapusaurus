# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Institution', fields ['ffiec_id']
        db.delete_unique('respondants_institution', ['ffiec_id'])

        # Adding unique constraint on 'Institution', fields ['ffiec_id', 'agency']
        db.create_unique('respondants_institution', ['ffiec_id', 'agency_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Institution', fields ['ffiec_id', 'agency']
        db.delete_unique('respondants_institution', ['ffiec_id', 'agency_id'])

        # Adding unique constraint on 'Institution', fields ['ffiec_id']
        db.create_unique('respondants_institution', ['ffiec_id'])


    models = {
        'respondants.agency': {
            'Meta': {'object_name': 'Agency'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hmda_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'respondants.institution': {
            'Meta': {'unique_together': "(('ffiec_id', 'agency'),)", 'object_name': 'Institution'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['respondants.Agency']"}),
            'ffiec_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_address': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['respondants.Institution']"}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'top_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descendants'", 'null': 'True', 'to': "orm['respondants.Institution']"}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {}),
            'zip_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['respondants.ZipcodeCityState']"})
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