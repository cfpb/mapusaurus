# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('hmda_id', models.IntegerField(serialize=False, primary_key=True)),
                ('acronym', models.CharField(max_length=10)),
                ('full_name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.SmallIntegerField()),
                ('name', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=25)),
                ('state', localflavor.us.models.USStateField(max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('zipcode', models.IntegerField()),
                ('lat', models.FloatField(help_text=b'y')),
                ('lon', models.FloatField(help_text=b'x')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('year', models.SmallIntegerField()),
                ('respondent_id', models.CharField(max_length=10)),
                ('institution_id', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('tax_id', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=30)),
                ('mailing_address', models.CharField(max_length=40)),
                ('assets', models.PositiveIntegerField(default=0, help_text=b'Prior year reported assets in thousands of dollars')),
                ('rssd_id', models.CharField(help_text=b'From Reporter Panel. Id on the National Information Center repository', max_length=10, null=True)),
                ('agency', models.ForeignKey(to='respondents.Agency')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LenderHierarchy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organization_id', models.IntegerField()),
                ('institution', models.ForeignKey(to='respondents.Institution')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParentInstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.SmallIntegerField()),
                ('name', models.CharField(max_length=30)),
                ('city', models.CharField(max_length=25)),
                ('state', models.CharField(max_length=2, null=True)),
                ('country', models.CharField(max_length=40, null=True)),
                ('rssd_id', models.CharField(help_text=b'Id on the National Information Center repository', max_length=10, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ZipcodeCityStateYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zip_code', models.IntegerField()),
                ('plus_four', models.IntegerField(null=True)),
                ('city', models.CharField(max_length=25)),
                ('state', localflavor.us.models.USStateField(max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('year', models.SmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='zipcodecitystateyear',
            unique_together=set([('zip_code', 'city', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='parentinstitution',
            unique_together=set([('rssd_id', 'year')]),
        ),
        migrations.AddField(
            model_name='institution',
            name='non_reporting_parent',
            field=models.ForeignKey(related_name=b'children', to='respondents.ParentInstitution', help_text=b'Non-HMDA reporting parent', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='parent',
            field=models.ForeignKey(related_name=b'children', to='respondents.Institution', help_text=b'The parent institution', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='top_holder',
            field=models.ForeignKey(related_name=b'descendants', to='respondents.ParentInstitution', help_text=b'The company at the top of the ownership chain.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='zip_code',
            field=models.ForeignKey(to='respondents.ZipcodeCityStateYear'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='institution',
            unique_together=set([('institution_id', 'year')]),
        ),
        migrations.AlterIndexTogether(
            name='institution',
            index_together=set([('institution_id', 'year')]),
        ),
        migrations.AddField(
            model_name='branch',
            name='institution',
            field=models.ForeignKey(to='respondents.Institution'),
            preserve_default=True,
        ),
    ]
