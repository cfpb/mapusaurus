from django.db import models

AGENCY_CHOICES = ( 
    (1, 'Office of the Comptroller of the Currency (OCC)'),
    (2, 'Federal Reserve System (FRS)'),
    (3, 'Federal Deposit Insurance Corporation (FDIC)'),
    (5, 'National Credit Union Administration (NCUA)'),
    (7, 'Department of Housing and Urban Development (HUD)'),
    (9, 'Consumer Financial Protection Bureau (CFPB)'),
)

EDIT_STATUS_CHOICES = (
    ('', 'No edit failures'),
    (5, 'Validity edit failure only'),
    (6, 'Quality edit failure only'),
    (7, 'Validity and quality edit failures'),
)

LOAN_TYPE_CHOICES = ( 
    (1, 'Conventional (any loan other than FHA, VA, FSA, or RHS loans)'),
    (2, 'FHA-insured (Federal Housing Administration)'),
    (3, 'VA-guaranteed (Veterans Administration)'),
    (4, 'FSA/RHS (Farm Service Agency or Rural Housing Service)'),
)

PROPERTY_TYPE_CHOICES = (
    (1, 'One to four-family (other than manufactured housing)'),
    (2, 'Manufactured housing'),
    (3, 'Multifamily'),
)

LOAN_PURPOSE_CHOICES = (
    (1, 'Home purchase'),
    (2, 'Home improvement'),
    (3, 'Refinancing'),
)
 
OWNER_OCCUPANCY_CHOICES = (
    (1, 'Owner-occupied as a principal dwelling'),
    (2, 'Not owner-occupied'),
    (3, 'Not applicable'),
)
 
PREAPROVAL_CHOICES = (
    (1, 'Preapproval was requested'),
    (2, 'Preapproval was not requested'),
    (3, 'Not applicable'),
)
ACTION_TAKEN_CHOICES = (
    (1, 'Loan originated'),
    (2, 'Application approved but not accepted'),
    (3, 'Application denied by financial institution'),
    (4, 'Application withdrawn by applicant'),
    (5, 'File closed for incompleteness'),
    (6, 'Loan purchased by the institution'),
    (7, 'Preapproval request denied by financial institution'),
    (8, 'Preapproval request approved but not accepted (optional reporting)'),
)

ETHNICITY_CHOICES = (
    (1, 'Hispanic or Latino'),
    (2, 'Not Hispanic or Latino'),
    (3, 'Information not provided by applicant in mail, Internet, or telephone application'),
    (4, 'Not applicable'),
    (5, 'No co-applicant'),
)

RACE_CHOICES = (
    (1, 'American Indian or Alaska Native  2 -- Asian'),
    (3, 'Black or African American'),
    (4, 'Native Hawaiian or Other Pacific Islander '),
    (5, 'White'),
    (6, 'Information not provided by applicant in mail, Internet, or telephone application'),
    (7, 'Not applicable'),
    (8, 'No co-applicant'),
)

SEX_CHOICES = (
    (1, 'Male'),
    (2, 'Female'),
    (3, 'Information not provided by applicant in mail, Internet, or telephone application'),
    (4, 'Not applicable'),
    (5, 'No co-applicant'),
)


TYPE_OF_PURCHASER_CHOICES = (
    (0, 'Loan was not originated or was not sold in calendar year covered by register'),
    (1, 'Fannie Mae (FNMA)'),
    (2, 'Ginnie Mae (GNMA)'),
    (3, 'Freddie Mac (FHLMC)'),
    (4, 'Farmer Mac (FAMC)'),
    (5, 'Private securitization'),
    (6, 'Commercial bank, savings bank or savings association'),
    (7, 'Life insurance company, credit union, mortgage bank, or finance company'),
    (8, 'Affiliate institution'),
    (9, 'Other type of purchaser'),
)

REASONS_FOR_DENIAL_CHOICES = (
    (1, 'Debt-to-income ratio'),
    (2, 'Employment history'),
    (3, 'Credit history'),
    (4, 'Collateral'),
    (5, 'Insufficient cash (downpayment, closing costs)'),
    (6, 'Unverifiable information'),
    (7, 'Credit application incomplete'),
    (8, 'Mortgage insurance denied'),
    (9, 'Other'),
)

HOEPA_STATUS_CHOICES = (
    (1, 'HOEPA loan'),
    (2, 'Not a HOEPA loan'),
)

LIEN_STATUS_CHOICES = (
    (1, 'Secured by a first lien'),
    (2, 'Secured by a subordinate lien'),
    (3, 'Not secured by a lien'),
    (4, 'Not applicable (purchased loans)'),
)

APPLICATION_DATE_INDICATOR_CHOICES = (
    (0, 'Application Date >= 01-01-2004'),
    (1, 'Application Date < 01-01-2004'),
    (2, 'Application Date = NA (Not Available)'),
)


class HMDARecord(models.Model):
    """  
       HMDA Loan Application Register Format
       https://www.ffiec.gov/hmdarawdata/FORMATS/2013HMDALARRecordFormat.pdf
    """
    as_of_year = models.PositiveIntegerField(db_index=True, help_text="The reporting year of the HMDA record.")
    respondent_id = models.CharField(max_length=10, help_text="A code representing the bank or other financial institution that is reporting the loan or application.")
    agency_code = models.CharField(max_length=1, choices=AGENCY_CHOICES, help_text="A code representing the federal agency to which the HMDA-reporting institution submits its HMDA data.")
    loan_type = models.PositiveIntegerField(choices=LOAN_TYPE_CHOICES, help_text="A code representing the type of loan applied for. Many loans are insured or guaranteed by government programs offered by Federal Housing Administration (FHA), the Department of Veterans Affairs (VA), or the Department of Agriculture's Rural Housing Service (RHS) or Farm Service Agency (FSA). All other loans are classified as conventional.")
    property_type = models.CharField(choices=PROPERTY_TYPE_CHOICES, max_length=1, help_text="A code representing the type of the property.")
    loan_purpose = models.PositiveIntegerField(choices=LOAN_PURPOSE_CHOICES, help_text="A code representing the purpose of the loan (home purchase, refinance, or home improvement).")
    owner_occupancy = models.PositiveIntegerField(choices=OWNER_OCCUPANCY_CHOICES, help_text="A code representing the owner-occupancy status of the property. Second homes, vacation homes, and rental properties are classified as 'not owner-occupied as a principal dwelling'.")
    loan_amount_000s = models.PositiveIntegerField(help_text="The amount of the loan applied for, in thousands of dollars.")
    preapproval = models.CharField(choices=PREAPROVAL_CHOICES, max_length=1, help_text="A code representing the pre-approval status of the application.")
    action_taken = models.PositiveIntegerField(choices=ACTION_TAKEN_CHOICES, db_index=True, help_text="A code representing the action taken on the loan or application, such as whether an application was approved or denied. Loan originated means the application resulted in a mortgage. Loan purchased means that the lender bought the loan on the secondary market.")
    msamd = models.CharField(max_length=5, help_text="A code representing the Metropolitan Statistical Area/Metropolitian Division (MSA/MD) the property is located in. An MSA is a region with relatively high population density at its core (usually a single large city) and close economic ties throughout. Larger MSAs are divided into MDs.")
    statefp = models.CharField(max_length=2, db_index=True, help_text="A two-digit code representing the state the property is located in.")
    countyfp = models.CharField(max_length=3, help_text="A three-digit code representing the county of the property. This code is only unique when combined with the state code.")
    census_tract_number = models.CharField(max_length=7, help_text="The number of the census tract for the property. This code is only unique when combined with the state and county codes.")
    applicant_ethnicity = models.CharField(choices=ETHNICITY_CHOICES, max_length=1, help_text="A code representing the ethnicity of the primary applicant.")
    co_applicant_ethnicity = models.CharField(choices=ETHNICITY_CHOICES, max_length=1, help_text="A code representing the ethnicity of the co-applicant.")
    applicant_race_1 = models.CharField(choices=RACE_CHOICES, max_length=1, help_text="A code representing the first listed race for the primary applicant. The applicant can list up to five races.")
    applicant_race_2 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the second listed race for the primary applicant.")
    applicant_race_3 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the third listed race for the primary applicant.")
    applicant_race_4 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the fourth listed race for the primary applicant.")
    applicant_race_5 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the fifth listed race for the primary applicant.")
    co_applicant_race_1 = models.CharField(choices=RACE_CHOICES, max_length=1, help_text="A code representing the first listed race for the co-applicant. The co-applicant can list up to five races.")
    co_applicant_race_2 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the second listed race for the co-applicant.")
    co_applicant_race_3 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the third listed race for the co-applicant.")
    co_applicant_race_4 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the fourth listed race for the co-applicant.")
    co_applicant_race_5 = models.CharField(choices=RACE_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the fifth listed race for the co-applicant.")
    applicant_sex = models.PositiveIntegerField(choices=SEX_CHOICES, help_text="A code representing the sex of the primary applicant.")
    co_applicant_sex = models.PositiveIntegerField(choices=SEX_CHOICES, help_text="A code representing the sex of the co-applicant.")
    applicant_income_000s = models.CharField(max_length=4, help_text="The gross annual income that the lender relied on when evaluating the creditworthiness of the applicant, rounded to the nearest thousand.")
    purchaser_type = models.CharField(choices=TYPE_OF_PURCHASER_CHOICES, max_length=1, help_text="A code representing the type of institution purchasing the loan.")
    denial_reason_1 = models.CharField(choices=REASONS_FOR_DENIAL_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the first reason for denial of the application. Lenders may report up to three denial reasons, but such reporting is optional.")
    denial_reason_2 = models.CharField(choices=REASONS_FOR_DENIAL_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the second reason for denial of the application.")
    denial_reason_3 = models.CharField(choices=REASONS_FOR_DENIAL_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the third reason for denial of the application.")
    rate_spread = models.CharField(max_length=5, help_text="The rate spread for the loan, which is the difference between the loan's annual percentage rate (APR) and the average prime offer rate (APOR).")
    hoepa_status = models.CharField(choices=HOEPA_STATUS_CHOICES, max_length=1, help_text="A code representing whether a loan is subject to the Home Ownership and Equity Protection Act of 1994 (HOEPA).")
    lien_status = models.CharField(choices=LIEN_STATUS_CHOICES, max_length=1, help_text="A code representing the lien status. Most mortgages are secured by a lien against the property. In the event of a forced liquidation, first lien holders will generally get paid before subordinate lien holders.")
    edit_status = models.CharField(choices=EDIT_STATUS_CHOICES, max_length=1, null=True, blank=True, help_text="A code representing the edit failure status of the application.")
    sequence_number = models.CharField(max_length=7, help_text="A one-up number scheme for each respondent to make each loan unique.")
    population = models.CharField(max_length=8, help_text="The total population in the tract.")
    minority_population = models.CharField(max_length=6, help_text="The percentage of minority population to total population for the census tract, carried to two decimal places.")
    ffieic_median_family_income = models.CharField(max_length=8, help_text="The median family income in dollars for the MSA/MD in which the tract is located. (Note: The HMDA API names this col hud_median_family_income.)")
    tract_to_msamd_income = models.CharField(max_length=6, help_text="The percentage of the median family income for the tract compared to the median family income for the MSA/MD, rounded to two decimal places.")
    number_of_owner_occupied_units = models.CharField(max_length=8, help_text="The number of dwellings in the tract that are lived in by the owner.")
    number_of_1_to_4_family_units = models.CharField(max_length=8, help_text="The number of dwellings in the tract that are built to house fewer than 5 families.")
    application_date_indicator = models.PositiveIntegerField(choices=APPLICATION_DATE_INDICATOR_CHOICES, help_text="A code representing the date of the application. '0' means the application was made on or after 1/1/2004; '1' means the application was made before 1/1/2004; '2' means the application date is not available.")
   
    institution = models.ForeignKey('respondents.Institution', to_field='institution_id')
    geo = models.ForeignKey('geo.Geo', to_field='geoid',
                              db_index=True)

    class Meta:
        index_together = [("institution", "geo")]

    def save(self, *args, **kwargs):
        super(HMDARecord, self).save(*args, **kwargs)

class Year(models.Model):
    """Various year fields in the app data"""
    YEAR_CHOICES = zip( range(1970,2050), range(1970,2050) )
    hmda_year = models.PositiveIntegerField(primary_key=True, choices=YEAR_CHOICES, help_text="The reporting year of the HMDA record.")
    census_year = models.PositiveIntegerField(choices=YEAR_CHOICES, help_text="Year of census data.", null=False)
    geo_year = models.PositiveIntegerField(choices=YEAR_CHOICES, help_text="Year that geographic boundaries were recorded.", null=False)

    class Meta:
        get_latest_by = 'hmda_year'


class LendingStats(models.Model):
    """For certain lender x geo combinations, we have pre-computed
    hmda lar aggregations to speed up query time."""

    institution = models.ForeignKey('respondents.Institution', to_field='institution_id')
    geo = models.ForeignKey('geo.Geo', to_field='geoid')
    lar_median = models.PositiveIntegerField(help_text="HMDA LAR median")
    lar_count = models.PositiveIntegerField(help_text="Total HMDA LAR count")
    fha_count = models.PositiveIntegerField(help_text="Total HMDA LAR count where loan_type=2(FHA)")
    fha_bucket = models.PositiveIntegerField(help_text="Predetermined buckets calculated by find fha % of total lar count")
    
    class Meta:
        index_together = [("institution", "geo")]
        unique_together = [("institution", "geo")]
