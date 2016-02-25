# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hmda', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hmdarecord',
            name='as_of_year',
            field=models.PositiveIntegerField(help_text=b'The reporting year of the HMDA record.', db_index=True),
        ),
    ]
