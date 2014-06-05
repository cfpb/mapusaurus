# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Census2010Households'
        db.create_table(u'censusdata_census2010households', (
            ('geoid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.StateCensusTract'], to_field='geoid', unique=True, primary_key=True)),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
            ('total_family', self.gf('django.db.models.fields.IntegerField')()),
            ('husband_wife', self.gf('django.db.models.fields.IntegerField')()),
            ('total_family_other', self.gf('django.db.models.fields.IntegerField')()),
            ('male_no_wife', self.gf('django.db.models.fields.IntegerField')()),
            ('female_no_husband', self.gf('django.db.models.fields.IntegerField')()),
            ('total_nondamily', self.gf('django.db.models.fields.IntegerField')()),
            ('living_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('not_living_alone', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010Households'])


    def backwards(self, orm):
        # Deleting model 'Census2010Households'
        db.delete_table(u'censusdata_census2010households')


    models = {
        u'censusdata.census2010age': {
            'Meta': {'object_name': 'Census2010Age'},
            'eighteen_nineteen': ('django.db.models.fields.IntegerField', [], {}),
            'eighty_eightyfour': ('django.db.models.fields.IntegerField', [], {}),
            'eightyfive_up': ('django.db.models.fields.IntegerField', [], {}),
            'fifteen_seventeen': ('django.db.models.fields.IntegerField', [], {}),
            'fifty_fiftyfour': ('django.db.models.fields.IntegerField', [], {}),
            'fiftyfive_fiftynine': ('django.db.models.fields.IntegerField', [], {}),
            'five_nine': ('django.db.models.fields.IntegerField', [], {}),
            'forty_fortyfour': ('django.db.models.fields.IntegerField', [], {}),
            'fortyfive_fortynine': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'seventy_seventyfour': ('django.db.models.fields.IntegerField', [], {}),
            'seventyfive_seventynine': ('django.db.models.fields.IntegerField', [], {}),
            'sixty_sixtyone': ('django.db.models.fields.IntegerField', [], {}),
            'sixtyfive_sixtysix': ('django.db.models.fields.IntegerField', [], {}),
            'sixtyseven_sixynine': ('django.db.models.fields.IntegerField', [], {}),
            'sixtytwo_sixtyfour': ('django.db.models.fields.IntegerField', [], {}),
            'ten_fourteen': ('django.db.models.fields.IntegerField', [], {}),
            'thirty_thirtyfour': ('django.db.models.fields.IntegerField', [], {}),
            'thirtyfive_thirtynine': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {}),
            'twenty': ('django.db.models.fields.IntegerField', [], {}),
            'twentyfive_twentynine': ('django.db.models.fields.IntegerField', [], {}),
            'twentyone': ('django.db.models.fields.IntegerField', [], {}),
            'twentytwo_twentyfour': ('django.db.models.fields.IntegerField', [], {}),
            'under_five': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010hispanicorigin': {
            'Meta': {'object_name': 'Census2010HispanicOrigin'},
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'hispanic': ('django.db.models.fields.IntegerField', [], {}),
            'non_hispanic': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010households': {
            'Meta': {'object_name': 'Census2010Households'},
            'female_no_husband': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'husband_wife': ('django.db.models.fields.IntegerField', [], {}),
            'living_alone': ('django.db.models.fields.IntegerField', [], {}),
            'male_no_wife': ('django.db.models.fields.IntegerField', [], {}),
            'not_living_alone': ('django.db.models.fields.IntegerField', [], {}),
            'total': ('django.db.models.fields.IntegerField', [], {}),
            'total_family': ('django.db.models.fields.IntegerField', [], {}),
            'total_family_other': ('django.db.models.fields.IntegerField', [], {}),
            'total_nondamily': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010race': {
            'Meta': {'object_name': 'Census2010Race'},
            'amind_alone': ('django.db.models.fields.IntegerField', [], {}),
            'asian_alone': ('django.db.models.fields.IntegerField', [], {}),
            'black_alone': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'other_alone': ('django.db.models.fields.IntegerField', [], {}),
            'pacis_alone': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {}),
            'two_or_more': ('django.db.models.fields.IntegerField', [], {}),
            'white_alone': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010racestats': {
            'Meta': {'object_name': 'Census2010RaceStats'},
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'hispanic': ('django.db.models.fields.IntegerField', [], {}),
            'hispanic_perc': ('django.db.models.fields.FloatField', [], {}),
            'non_hisp_asian_only': ('django.db.models.fields.IntegerField', [], {}),
            'non_hisp_asian_only_perc': ('django.db.models.fields.FloatField', [], {}),
            'non_hisp_black_only': ('django.db.models.fields.IntegerField', [], {}),
            'non_hisp_black_only_perc': ('django.db.models.fields.FloatField', [], {}),
            'non_hisp_white_only': ('django.db.models.fields.IntegerField', [], {}),
            'non_hisp_white_only_perc': ('django.db.models.fields.FloatField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010sex': {
            'Meta': {'object_name': 'Census2010Sex'},
            'female': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCensusTract']", 'to_field': "'geoid'", 'unique': 'True', 'primary_key': 'True'}),
            'male': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {})
        },
        u'geo.statecensustract': {
            'Meta': {'object_name': 'StateCensusTract'},
            'aland': ('django.db.models.fields.FloatField', [], {}),
            'awater': ('django.db.models.fields.FloatField', [], {}),
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'funcstat': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'geoid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '11'}),
            'geojson': ('django.db.models.fields.TextField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intptlat': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'intptlon': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'maxlat': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'maxlon': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'minlat': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'minlon': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'mtfcc': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'namelsad': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tractce': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['censusdata']