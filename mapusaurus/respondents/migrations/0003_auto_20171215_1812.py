# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('respondents', '0002_auto_20160222_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='assets',
            field=models.BigIntegerField(default=0, help_text=b'Prior year reported assets in thousands of dollars'),
        ),
    ]