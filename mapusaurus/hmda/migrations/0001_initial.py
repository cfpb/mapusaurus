# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('respondents', '__first__'),
        ('geo', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='HMDARecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('as_of_year', models.PositiveIntegerField(help_text=b'The reporting year of the HMDA record.')),
                ('respondent_id', models.CharField(help_text=b'A code representing the bank or other financial institution that is reporting the loan or application.', max_length=10)),
                ('agency_code', models.CharField(help_text=b'A code representing the federal agency to which the HMDA-reporting institution submits its HMDA data.', max_length=1, choices=[(1, b'Office of the Comptroller of the Currency (OCC)'), (2, b'Federal Reserve System (FRS)'), (3, b'Federal Deposit Insurance Corporation (FDIC)'), (5, b'National Credit Union Administration (NCUA)'), (7, b'Department of Housing and Urban Development (HUD)'), (9, b'Consumer Financial Protection Bureau (CFPB)')])),
                ('loan_type', models.PositiveIntegerField(help_text=b"A code representing the type of loan applied for. Many loans are insured or guaranteed by government programs offered by Federal Housing Administration (FHA), the Department of Veterans Affairs (VA), or the Department of Agriculture's Rural Housing Service (RHS) or Farm Service Agency (FSA). All other loans are classified as conventional.", choices=[(1, b'Conventional (any loan other than FHA, VA, FSA, or RHS loans)'), (2, b'FHA-insured (Federal Housing Administration)'), (3, b'VA-guaranteed (Veterans Administration)'), (4, b'FSA/RHS (Farm Service Agency or Rural Housing Service)')])),
                ('property_type', models.CharField(help_text=b'A code representing the type of the property.', max_length=1, choices=[(1, b'One to four-family (other than manufactured housing)'), (2, b'Manufactured housing'), (3, b'Multifamily')])),
                ('loan_purpose', models.PositiveIntegerField(help_text=b'A code representing the purpose of the loan (home purchase, refinance, or home improvement).', choices=[(1, b'Home purchase'), (2, b'Home improvement'), (3, b'Refinancing')])),
                ('owner_occupancy', models.PositiveIntegerField(help_text=b"A code representing the owner-occupancy status of the property. Second homes, vacation homes, and rental properties are classified as 'not owner-occupied as a principal dwelling'.", choices=[(1, b'Owner-occupied as a principal dwelling'), (2, b'Not owner-occupied'), (3, b'Not applicable')])),
                ('loan_amount_000s', models.PositiveIntegerField(help_text=b'The amount of the loan applied for, in thousands of dollars.')),
                ('preapproval', models.CharField(help_text=b'A code representing the pre-approval status of the application.', max_length=1, choices=[(1, b'Preapproval was requested'), (2, b'Preapproval was not requested'), (3, b'Not applicable')])),
                ('action_taken', models.PositiveIntegerField(help_text=b'A code representing the action taken on the loan or application, such as whether an application was approved or denied. Loan originated means the application resulted in a mortgage. Loan purchased means that the lender bought the loan on the secondary market.', db_index=True, choices=[(1, b'Loan originated'), (2, b'Application approved but not accepted'), (3, b'Application denied by financial institution'), (4, b'Application withdrawn by applicant'), (5, b'File closed for incompleteness'), (6, b'Loan purchased by the institution'), (7, b'Preapproval request denied by financial institution'), (8, b'Preapproval request approved but not accepted (optional reporting)')])),
                ('msamd', models.CharField(help_text=b'A code representing the Metropolitan Statistical Area/Metropolitian Division (MSA/MD) the property is located in. An MSA is a region with relatively high population density at its core (usually a single large city) and close economic ties throughout. Larger MSAs are divided into MDs.', max_length=5)),
                ('statefp', models.CharField(help_text=b'A two-digit code representing the state the property is located in.', max_length=2, db_index=True)),
                ('countyfp', models.CharField(help_text=b'A three-digit code representing the county of the property. This code is only unique when combined with the state code.', max_length=3)),
                ('census_tract_number', models.CharField(help_text=b'The number of the census tract for the property. This code is only unique when combined with the state and county codes.', max_length=7)),
                ('applicant_ethnicity', models.CharField(help_text=b'A code representing the ethnicity of the primary applicant.', max_length=1, choices=[(1, b'Hispanic or Latino'), (2, b'Not Hispanic or Latino'), (3, b'Information not provided by applicant in mail, Internet, or telephone application'), (4, b'Not applicable'), (5, b'No co-applicant')])),
                ('co_applicant_ethnicity', models.CharField(help_text=b'A code representing the ethnicity of the co-applicant.', max_length=1, choices=[(1, b'Hispanic or Latino'), (2, b'Not Hispanic or Latino'), (3, b'Information not provided by applicant in mail, Internet, or telephone application'), (4, b'Not applicable'), (5, b'No co-applicant')])),
                ('applicant_race_1', models.CharField(help_text=b'A code representing the first listed race for the primary applicant. The applicant can list up to five races.', max_length=1, choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('applicant_race_2', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the second listed race for the primary applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('applicant_race_3', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the third listed race for the primary applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('applicant_race_4', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the fourth listed race for the primary applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('applicant_race_5', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the fifth listed race for the primary applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('co_applicant_race_1', models.CharField(help_text=b'A code representing the first listed race for the co-applicant. The co-applicant can list up to five races.', max_length=1, choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('co_applicant_race_2', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the second listed race for the co-applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('co_applicant_race_3', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the third listed race for the co-applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('co_applicant_race_4', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the fourth listed race for the co-applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('co_applicant_race_5', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the fifth listed race for the co-applicant.', choices=[(1, b'American Indian or Alaska Native  2 -- Asian'), (3, b'Black or African American'), (4, b'Native Hawaiian or Other Pacific Islander '), (5, b'White'), (6, b'Information not provided by applicant in mail, Internet, or telephone application'), (7, b'Not applicable'), (8, b'No co-applicant')])),
                ('applicant_sex', models.PositiveIntegerField(help_text=b'A code representing the sex of the primary applicant.', choices=[(1, b'Male'), (2, b'Female'), (3, b'Information not provided by applicant in mail, Internet, or telephone application'), (4, b'Not applicable'), (5, b'No co-applicant')])),
                ('co_applicant_sex', models.PositiveIntegerField(help_text=b'A code representing the sex of the co-applicant.', choices=[(1, b'Male'), (2, b'Female'), (3, b'Information not provided by applicant in mail, Internet, or telephone application'), (4, b'Not applicable'), (5, b'No co-applicant')])),
                ('applicant_income_000s', models.CharField(help_text=b'The gross annual income that the lender relied on when evaluating the creditworthiness of the applicant, rounded to the nearest thousand.', max_length=4)),
                ('purchaser_type', models.CharField(help_text=b'A code representing the type of institution purchasing the loan.', max_length=1, choices=[(0, b'Loan was not originated or was not sold in calendar year covered by register'), (1, b'Fannie Mae (FNMA)'), (2, b'Ginnie Mae (GNMA)'), (3, b'Freddie Mac (FHLMC)'), (4, b'Farmer Mac (FAMC)'), (5, b'Private securitization'), (6, b'Commercial bank, savings bank or savings association'), (7, b'Life insurance company, credit union, mortgage bank, or finance company'), (8, b'Affiliate institution'), (9, b'Other type of purchaser')])),
                ('denial_reason_1', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the first reason for denial of the application. Lenders may report up to three denial reasons, but such reporting is optional.', choices=[(1, b'Debt-to-income ratio'), (2, b'Employment history'), (3, b'Credit history'), (4, b'Collateral'), (5, b'Insufficient cash (downpayment, closing costs)'), (6, b'Unverifiable information'), (7, b'Credit application incomplete'), (8, b'Mortgage insurance denied'), (9, b'Other')])),
                ('denial_reason_2', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the second reason for denial of the application.', choices=[(1, b'Debt-to-income ratio'), (2, b'Employment history'), (3, b'Credit history'), (4, b'Collateral'), (5, b'Insufficient cash (downpayment, closing costs)'), (6, b'Unverifiable information'), (7, b'Credit application incomplete'), (8, b'Mortgage insurance denied'), (9, b'Other')])),
                ('denial_reason_3', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the third reason for denial of the application.', choices=[(1, b'Debt-to-income ratio'), (2, b'Employment history'), (3, b'Credit history'), (4, b'Collateral'), (5, b'Insufficient cash (downpayment, closing costs)'), (6, b'Unverifiable information'), (7, b'Credit application incomplete'), (8, b'Mortgage insurance denied'), (9, b'Other')])),
                ('rate_spread', models.CharField(help_text=b"The rate spread for the loan, which is the difference between the loan's annual percentage rate (APR) and the average prime offer rate (APOR).", max_length=5)),
                ('hoepa_status', models.CharField(help_text=b'A code representing whether a loan is subject to the Home Ownership and Equity Protection Act of 1994 (HOEPA).', max_length=1, choices=[(1, b'HOEPA loan'), (2, b'Not a HOEPA loan')])),
                ('lien_status', models.CharField(help_text=b'A code representing the lien status. Most mortgages are secured by a lien against the property. In the event of a forced liquidation, first lien holders will generally get paid before subordinate lien holders.', max_length=1, choices=[(1, b'Secured by a first lien'), (2, b'Secured by a subordinate lien'), (3, b'Not secured by a lien'), (4, b'Not applicable (purchased loans)')])),
                ('edit_status', models.CharField(blank=True, max_length=1, null=True, help_text=b'A code representing the edit failure status of the application.', choices=[(b'', b'No edit failures'), (5, b'Validity edit failure only'), (6, b'Quality edit failure only'), (7, b'Validity and quality edit failures')])),
                ('sequence_number', models.CharField(help_text=b'A one-up number scheme for each respondent to make each loan unique.', max_length=7)),
                ('population', models.CharField(help_text=b'The total population in the tract.', max_length=8)),
                ('minority_population', models.CharField(help_text=b'The percentage of minority population to total population for the census tract, carried to two decimal places.', max_length=6)),
                ('ffieic_median_family_income', models.CharField(help_text=b'The median family income in dollars for the MSA/MD in which the tract is located. (Note: The HMDA API names this col hud_median_family_income.)', max_length=8)),
                ('tract_to_msamd_income', models.CharField(help_text=b'The percentage of the median family income for the tract compared to the median family income for the MSA/MD, rounded to two decimal places.', max_length=6)),
                ('number_of_owner_occupied_units', models.CharField(help_text=b'The number of dwellings in the tract that are lived in by the owner.', max_length=8)),
                ('number_of_1_to_4_family_units', models.CharField(help_text=b'The number of dwellings in the tract that are built to house fewer than 5 families.', max_length=8)),
                ('application_date_indicator', models.PositiveIntegerField(help_text=b"A code representing the date of the application. '0' means the application was made on or after 1/1/2004; '1' means the application was made before 1/1/2004; '2' means the application date is not available.", choices=[(0, b'Application Date >= 01-01-2004'), (1, b'Application Date < 01-01-2004'), (2, b'Application Date = NA (Not Available)')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LendingStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lar_median', models.PositiveIntegerField(help_text=b'HMDA LAR median')),
                ('lar_count', models.PositiveIntegerField(help_text=b'Total HMDA LAR count')),
                ('fha_count', models.PositiveIntegerField(help_text=b'Total HMDA LAR count where loan_type=2(FHA)')),
                ('fha_bucket', models.PositiveIntegerField(help_text=b'Predetermined buckets calculated by find fha % of total lar count')),
                ('geo', models.ForeignKey(to='geo.Geo')),
                ('institution', models.ForeignKey(to='respondents.Institution')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('hmda_year', models.PositiveIntegerField(help_text=b'The reporting year of the HMDA record.', serialize=False, primary_key=True)),
                ('census_year', models.PositiveIntegerField(help_text=b'Year of census data.')),
                ('geo_year', models.PositiveIntegerField(help_text=b'Year that geographic boundaries were recorded.')),
            ],
            options={
                'get_latest_by': 'hmda_year',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='lendingstats',
            unique_together=set([('institution', 'geo')]),
        ),
        migrations.AlterIndexTogether(
            name='lendingstats',
            index_together=set([('institution', 'geo')]),
        ),
        migrations.AddField(
            model_name='hmdarecord',
            name='geo',
            field=models.ForeignKey(to='geo.Geo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hmdarecord',
            name='institution',
            field=models.ForeignKey(to='respondents.Institution'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='hmdarecord',
            index_together=set([('institution', 'geo')]),
        ),
    ]
