# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_auto_20160219_2009'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='geo',
            index_together=set([('geo_type', 'minlat', 'maxlon', 'year'), ('geo_type', 'centlat', 'centlon', 'year'), ('geo_type', 'maxlat', 'minlon', 'year'), ('geo_type', 'minlat', 'minlon', 'year'), ('geo_type', 'cbsa', 'year'), ('geo_type', 'maxlat', 'maxlon', 'year')]),
        ),
    ]
