# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Census2010Age',
            fields=[
                ('geoid', models.OneToOneField(primary_key=True, serialize=False, to='geo.Geo')),
                ('total_pop', models.IntegerField()),
                ('under_five', models.IntegerField()),
                ('five_nine', models.IntegerField()),
                ('ten_fourteen', models.IntegerField()),
                ('fifteen_seventeen', models.IntegerField()),
                ('eighteen_nineteen', models.IntegerField()),
                ('twenty', models.IntegerField()),
                ('twentyone', models.IntegerField()),
                ('twentytwo_twentyfour', models.IntegerField()),
                ('twentyfive_twentynine', models.IntegerField()),
                ('thirty_thirtyfour', models.IntegerField()),
                ('thirtyfive_thirtynine', models.IntegerField()),
                ('forty_fortyfour', models.IntegerField()),
                ('fortyfive_fortynine', models.IntegerField()),
                ('fifty_fiftyfour', models.IntegerField()),
                ('fiftyfive_fiftynine', models.IntegerField()),
                ('sixty_sixtyone', models.IntegerField()),
                ('sixtytwo_sixtyfour', models.IntegerField()),
                ('sixtyfive_sixtysix', models.IntegerField()),
                ('sixtyseven_sixynine', models.IntegerField()),
                ('seventy_seventyfour', models.IntegerField()),
                ('seventyfive_seventynine', models.IntegerField()),
                ('eighty_eightyfour', models.IntegerField()),
                ('eightyfive_up', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Census2010HispanicOrigin',
            fields=[
                ('geoid', models.OneToOneField(primary_key=True, serialize=False, to='geo.Geo')),
                ('total_pop', models.IntegerField()),
                ('non_hispanic', models.IntegerField()),
                ('hispanic', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Census2010Households',
            fields=[
                ('geoid', models.OneToOneField(primary_key=True, serialize=False, to='geo.Geo')),
                ('total', models.IntegerField(help_text=b'Total number of households in census tract. P0180001')),
                ('total_family', models.IntegerField(help_text=b'Total number of family households. Combined with total_nonfamily to check total. P0180002')),
                ('husband_wife', models.IntegerField(help_text=b'Husband-wife family households. Combine with total_family_other to check total_family. P0180003')),
                ('total_family_other', models.IntegerField(help_text=b"'Other' family households. Combine with husband_wife to check total_family. P0180004")),
                ('male_no_wife', models.IntegerField(help_text=b'Male householder, no wife present. Combine with female_no_husband to check total_family_other. P0180005')),
                ('female_no_husband', models.IntegerField(help_text=b'Female householder, no husband present. Combine with male_no_wife to check total_family_other. P0180006')),
                ('total_nonfamily', models.IntegerField(help_text=b'Total number of nonfamily households. Combine with total_family to check total. P0180007')),
                ('living_alone', models.IntegerField(help_text=b'Householder living alone. Combine with not_living_alone to check total_nonfamily. P0180008')),
                ('not_living_alone', models.IntegerField(help_text=b'Householder not living alone. Combine with living_alone to check total_nonfamily. P0180009')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Census2010Race',
            fields=[
                ('geoid', models.OneToOneField(primary_key=True, serialize=False, to='geo.Geo')),
                ('total_pop', models.IntegerField()),
                ('white_alone', models.IntegerField()),
                ('black_alone', models.IntegerField()),
                ('amind_alone', models.IntegerField()),
                ('asian_alone', models.IntegerField()),
                ('pacis_alone', models.IntegerField()),
                ('other_alone', models.IntegerField()),
                ('two_or_more', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Census2010RaceStats',
            fields=[
                ('geoid', models.OneToOneField(primary_key=True, serialize=False, to='geo.Geo')),
                ('total_pop', models.IntegerField()),
                ('hispanic', models.IntegerField()),
                ('non_hisp_white_only', models.IntegerField()),
                ('non_hisp_black_only', models.IntegerField()),
                ('non_hisp_asian_only', models.IntegerField()),
                ('hispanic_perc', models.FloatField()),
                ('non_hisp_white_only_perc', models.FloatField()),
                ('non_hisp_black_only_perc', models.FloatField()),
                ('non_hisp_asian_only_perc', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Census2010Sex',
            fields=[
                ('geoid', models.OneToOneField(primary_key=True, serialize=False, to='geo.Geo')),
                ('total_pop', models.IntegerField()),
                ('male', models.IntegerField()),
                ('female', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
