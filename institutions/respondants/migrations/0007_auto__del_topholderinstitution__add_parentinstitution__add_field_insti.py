# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TopHolderInstitution'
        db.delete_table('respondants_topholderinstitution')

        # Adding model 'ParentInstitution'
        db.create_table('respondants_parentinstitution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('rssd_id', self.gf('django.db.models.fields.CharField')(max_length=10, unique=True, null=True)),
        ))
        db.send_create_signal('respondants', ['ParentInstitution'])

        # Adding field 'Institution.non_reporting_parent'
        db.add_column('respondants_institution', 'non_reporting_parent',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['respondants.Institution']),
                      keep_default=False)


        # Changing field 'Institution.parent'
        db.alter_column('respondants_institution', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.ParentInstitution']))

        # Changing field 'Institution.top_holder'
        db.alter_column('respondants_institution', 'top_holder_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.ParentInstitution']))

    def backwards(self, orm):
        # Adding model 'TopHolderInstitution'
        db.create_table('respondants_topholderinstitution', (
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('year', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rssd_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10, null=True)),
        ))
        db.send_create_signal('respondants', ['TopHolderInstitution'])

        # Deleting model 'ParentInstitution'
        db.delete_table('respondants_parentinstitution')

        # Deleting field 'Institution.non_reporting_parent'
        db.delete_column('respondants_institution', 'non_reporting_parent_id')


        # Changing field 'Institution.parent'
        db.alter_column('respondants_institution', 'parent_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.Institution']))

        # Changing field 'Institution.top_holder'
        db.alter_column('respondants_institution', 'top_holder_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['respondants.TopHolderInstitution']))

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
            'non_reporting_parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['respondants.Institution']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['respondants.ParentInstitution']"}),
            'rssd_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'top_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descendants'", 'null': 'True', 'to': "orm['respondants.ParentInstitution']"}),
            'year': ('django.db.models.fields.SmallIntegerField', [], {}),
            'zip_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['respondants.ZipcodeCityState']"})
        },
        'respondants.parentinstitution': {
            'Meta': {'object_name': 'ParentInstitution'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
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