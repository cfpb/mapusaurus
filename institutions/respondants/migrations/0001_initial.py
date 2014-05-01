# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ZipcodeCityState'
        db.create_table('respondants_zipcodecitystate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.IntegerField')()),
            ('plus_four', self.gf('django.db.models.fields.IntegerField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2)),
        ))
        db.send_create_signal('respondants', ['ZipcodeCityState'])

        # Adding model 'Agency'
        db.create_table('respondants_agency', (
            ('hmda_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('acronym', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('respondants', ['Agency'])

        # Adding model 'Institution'
        db.create_table('respondants_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('ffiec_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondants.Agency'])),
            ('tax_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('mailing_address', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('zip_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['respondants.ZipcodeCityState'])),
            ('rssd_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['respondants.Institution'])),
            ('top_holder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descendants', null=True, to=orm['respondants.Institution'])),
        ))
        db.send_create_signal('respondants', ['Institution'])


    def backwards(self, orm):
        # Deleting model 'ZipcodeCityState'
        db.delete_table('respondants_zipcodecitystate')

        # Deleting model 'Agency'
        db.delete_table('respondants_agency')

        # Deleting model 'Institution'
        db.delete_table('respondants_institution')


    models = {
        'respondants.agency': {
            'Meta': {'object_name': 'Agency'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hmda_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'respondants.institution': {
            'Meta': {'object_name': 'Institution'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['respondants.Agency']"}),
            'ffiec_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
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
            'Meta': {'object_name': 'ZipcodeCityState'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plus_four': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['respondants']