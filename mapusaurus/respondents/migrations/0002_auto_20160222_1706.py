# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('respondents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentinstitution',
            name='year',
            field=models.SmallIntegerField(db_index=True),
        ),
    ]
