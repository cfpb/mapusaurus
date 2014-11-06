# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Census2010Race'
        db.create_table(u'censusdata_census2010race', (
            ('geoid', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Geo'], unique=True, primary_key=True)),
            ('total_pop', self.gf('django.db.models.fields.IntegerField')()),
            ('white_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('black_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('amind_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('asian_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('pacis_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('other_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('two_or_more', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010Race'])

        # Adding model 'Census2010HispanicOrigin'
        db.create_table(u'censusdata_census2010hispanicorigin', (
            ('geoid', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Geo'], unique=True, primary_key=True)),
            ('total_pop', self.gf('django.db.models.fields.IntegerField')()),
            ('non_hispanic', self.gf('django.db.models.fields.IntegerField')()),
            ('hispanic', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010HispanicOrigin'])

        # Adding model 'Census2010Sex'
        db.create_table(u'censusdata_census2010sex', (
            ('geoid', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Geo'], unique=True, primary_key=True)),
            ('total_pop', self.gf('django.db.models.fields.IntegerField')()),
            ('male', self.gf('django.db.models.fields.IntegerField')()),
            ('female', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010Sex'])

        # Adding model 'Census2010Age'
        db.create_table(u'censusdata_census2010age', (
            ('geoid', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Geo'], unique=True, primary_key=True)),
            ('total_pop', self.gf('django.db.models.fields.IntegerField')()),
            ('under_five', self.gf('django.db.models.fields.IntegerField')()),
            ('five_nine', self.gf('django.db.models.fields.IntegerField')()),
            ('ten_fourteen', self.gf('django.db.models.fields.IntegerField')()),
            ('fifteen_seventeen', self.gf('django.db.models.fields.IntegerField')()),
            ('eighteen_nineteen', self.gf('django.db.models.fields.IntegerField')()),
            ('twenty', self.gf('django.db.models.fields.IntegerField')()),
            ('twentyone', self.gf('django.db.models.fields.IntegerField')()),
            ('twentytwo_twentyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('twentyfive_twentynine', self.gf('django.db.models.fields.IntegerField')()),
            ('thirty_thirtyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('thirtyfive_thirtynine', self.gf('django.db.models.fields.IntegerField')()),
            ('forty_fortyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('fortyfive_fortynine', self.gf('django.db.models.fields.IntegerField')()),
            ('fifty_fiftyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('fiftyfive_fiftynine', self.gf('django.db.models.fields.IntegerField')()),
            ('sixty_sixtyone', self.gf('django.db.models.fields.IntegerField')()),
            ('sixtytwo_sixtyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('sixtyfive_sixtysix', self.gf('django.db.models.fields.IntegerField')()),
            ('sixtyseven_sixynine', self.gf('django.db.models.fields.IntegerField')()),
            ('seventy_seventyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('seventyfive_seventynine', self.gf('django.db.models.fields.IntegerField')()),
            ('eighty_eightyfour', self.gf('django.db.models.fields.IntegerField')()),
            ('eightyfive_up', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010Age'])

        # Adding model 'Census2010RaceStats'
        db.create_table(u'censusdata_census2010racestats', (
            ('geoid', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Geo'], unique=True, primary_key=True)),
            ('total_pop', self.gf('django.db.models.fields.IntegerField')()),
            ('hispanic', self.gf('django.db.models.fields.IntegerField')()),
            ('non_hisp_white_only', self.gf('django.db.models.fields.IntegerField')()),
            ('non_hisp_black_only', self.gf('django.db.models.fields.IntegerField')()),
            ('non_hisp_asian_only', self.gf('django.db.models.fields.IntegerField')()),
            ('hispanic_perc', self.gf('django.db.models.fields.FloatField')()),
            ('non_hisp_white_only_perc', self.gf('django.db.models.fields.FloatField')()),
            ('non_hisp_black_only_perc', self.gf('django.db.models.fields.FloatField')()),
            ('non_hisp_asian_only_perc', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010RaceStats'])

        # Adding model 'Census2010Households'
        db.create_table(u'censusdata_census2010households', (
            ('geoid', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Geo'], unique=True, primary_key=True)),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
            ('total_family', self.gf('django.db.models.fields.IntegerField')()),
            ('husband_wife', self.gf('django.db.models.fields.IntegerField')()),
            ('total_family_other', self.gf('django.db.models.fields.IntegerField')()),
            ('male_no_wife', self.gf('django.db.models.fields.IntegerField')()),
            ('female_no_husband', self.gf('django.db.models.fields.IntegerField')()),
            ('total_nonfamily', self.gf('django.db.models.fields.IntegerField')()),
            ('living_alone', self.gf('django.db.models.fields.IntegerField')()),
            ('not_living_alone', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'censusdata', ['Census2010Households'])


    def backwards(self, orm):
        # Deleting model 'Census2010Race'
        db.delete_table(u'censusdata_census2010race')

        # Deleting model 'Census2010HispanicOrigin'
        db.delete_table(u'censusdata_census2010hispanicorigin')

        # Deleting model 'Census2010Sex'
        db.delete_table(u'censusdata_census2010sex')

        # Deleting model 'Census2010Age'
        db.delete_table(u'censusdata_census2010age')

        # Deleting model 'Census2010RaceStats'
        db.delete_table(u'censusdata_census2010racestats')

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
            'geoid': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['geo.Geo']", 'unique': 'True', 'primary_key': 'True'}),
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
            'geoid': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['geo.Geo']", 'unique': 'True', 'primary_key': 'True'}),
            'hispanic': ('django.db.models.fields.IntegerField', [], {}),
            'non_hispanic': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010households': {
            'Meta': {'object_name': 'Census2010Households'},
            'female_no_husband': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['geo.Geo']", 'unique': 'True', 'primary_key': 'True'}),
            'husband_wife': ('django.db.models.fields.IntegerField', [], {}),
            'living_alone': ('django.db.models.fields.IntegerField', [], {}),
            'male_no_wife': ('django.db.models.fields.IntegerField', [], {}),
            'not_living_alone': ('django.db.models.fields.IntegerField', [], {}),
            'total': ('django.db.models.fields.IntegerField', [], {}),
            'total_family': ('django.db.models.fields.IntegerField', [], {}),
            'total_family_other': ('django.db.models.fields.IntegerField', [], {}),
            'total_nonfamily': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010race': {
            'Meta': {'object_name': 'Census2010Race'},
            'amind_alone': ('django.db.models.fields.IntegerField', [], {}),
            'asian_alone': ('django.db.models.fields.IntegerField', [], {}),
            'black_alone': ('django.db.models.fields.IntegerField', [], {}),
            'geoid': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['geo.Geo']", 'unique': 'True', 'primary_key': 'True'}),
            'other_alone': ('django.db.models.fields.IntegerField', [], {}),
            'pacis_alone': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {}),
            'two_or_more': ('django.db.models.fields.IntegerField', [], {}),
            'white_alone': ('django.db.models.fields.IntegerField', [], {})
        },
        u'censusdata.census2010racestats': {
            'Meta': {'object_name': 'Census2010RaceStats'},
            'geoid': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['geo.Geo']", 'unique': 'True', 'primary_key': 'True'}),
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
            'geoid': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['geo.Geo']", 'unique': 'True', 'primary_key': 'True'}),
            'male': ('django.db.models.fields.IntegerField', [], {}),
            'total_pop': ('django.db.models.fields.IntegerField', [], {})
        },
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
        }
    }

    complete_apps = ['censusdata']