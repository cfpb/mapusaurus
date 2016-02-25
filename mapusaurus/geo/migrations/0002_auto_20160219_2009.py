# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geo',
            name='year',
            field=models.SmallIntegerField(db_index=True),
        ),
        migrations.AlterIndexTogether(
            name='geo',
            index_together=set([('geo_type', 'minlat', 'maxlon', 'year'), ('geo_type', 'maxlat', 'maxlon', 'year'), ('geo_type', 'geoid'), ('geo_type', 'maxlat', 'minlon', 'year'), ('geo_type', 'centlat', 'centlon', 'year'), ('geo_type', 'cbsa', 'year'), ('geo_type', 'minlat', 'minlon', 'year')]),
        ),
    ]
