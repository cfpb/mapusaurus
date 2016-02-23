# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Geo',
            fields=[
                ('geoid', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('geo_type', models.PositiveIntegerField(db_index=True, choices=[(1, b'State'), (2, b'County'), (3, b'Census Tract'), (4, b'Metropolitan'), (5, b'Micropolitan'), (6, b'Metropolitan Division')])),
                ('name', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=2, null=True)),
                ('county', models.CharField(max_length=3, null=True)),
                ('tract', models.CharField(max_length=6, null=True)),
                ('csa', models.CharField(help_text=b'Combined Statistical Area', max_length=3, null=True)),
                ('cbsa', models.CharField(help_text=b'Core Based Statistical Area', max_length=5, null=True)),
                ('metdiv', models.CharField(help_text=b'Metro Division', max_length=5, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4269)),
                ('year', models.SmallIntegerField()),
                ('minlat', models.FloatField()),
                ('maxlat', models.FloatField()),
                ('minlon', models.FloatField()),
                ('maxlon', models.FloatField()),
                ('centlat', models.FloatField()),
                ('centlon', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='geo',
            index_together=set([('geo_type', 'minlat', 'maxlon', 'year'), ('geo_type', 'centlat', 'centlon', 'year'), ('geo_type', 'maxlat', 'minlon', 'year'), ('geo_type', 'minlat', 'minlon', 'year'), ('geo_type', 'cbsa', 'year'), ('geo_type', 'maxlat', 'maxlon', 'year')]),
        ),
    ]
