from django.db import models


AGENCY_CHOICES = (
    (1, 'Office of the Comptroller of the Currency (OCC)'),
    (2, 'Federal Reserve System (FRS)'),
    (3, 'Federal Deposit Insurance Corporation (FDIC)'),
    (5, 'National Credit Union Administration (NCUA)'),
    (7, 'Department of Housing and Urban Development (HUD)'),
    (9, 'Consumer Financial Protection Bureau (CFPB)'),
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


class HMDARecord(models.Model):
    """Not a full record -- we only store the fields we know we'll need
       HMDA Loan Application Register Format
       https://www.ffiec.gov/hmdarawdata/FORMATS/2012HMDALARRecordFormat.pdf
    """
    as_of_year = models.PositiveIntegerField(
        help_text="The reporting year of the HMDA record.")
    respondent_id = models.CharField(
        max_length=10,
        help_text=("A code representing the bank or other financial "
                   + "institution that is reporting the loan or application."))
    agency_code = models.CharField(
        max_length=1, choices=AGENCY_CHOICES,
        help_text=("A code representing the federal agency to which the "
                   + "HMDA-reporting institution submits its HMDA data."))
    loan_amount_000s = models.PositiveIntegerField(
        help_text=("The amount of the loan applied for, in thousands of "
                   + "dollars."))
    action_taken = models.PositiveIntegerField(
        choices=ACTION_TAKEN_CHOICES, db_index=True,
        help_text=("A code representing the action taken on the loan or "
                   + "application, such as whether an application was "
                   + "approved or denied. Loan originated means the "
                   + "application resulted in a mortgage. Loan purchased "
                   + "means that the lender bought the loan on the "
                   + "secondary market."))
    statefp = models.CharField(
        max_length=2, db_index=True,
        help_text=("A two-digit code representing the state the property is "
                   + " located in."))
    countyfp = models.CharField(
        max_length=3,
        help_text=("A three-digit code representing the county of the "
                   + "property. This code is only unique when combined with "
                   + "the state code."))

    lender = models.CharField(max_length=11, db_index=True)
    geoid = models.ForeignKey('geo.StateCensusTract', to_field='geoid',
                              db_index=True)

    class Meta:
        index_together = [("statefp", "countyfp"),
                          ("statefp", "countyfp", "lender"),
                          ("statefp", "countyfp", "action_taken", "lender")]

    def auto_fields(self):
        self.lender = self.agency_code + self.respondent_id

    def save(self, *args, **kwargs):
        self.auto_fields()
        super(HMDARecord, self).save(*args, **kwargs)
