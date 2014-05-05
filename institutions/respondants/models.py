from django.db import models
from localflavor.us.models import USStateField
from respondants.managers import AgencyManager

class ZipcodeCityState(models.Model):
    """ For each zipcode, maintain the city, state information. """
    zip_code = models.IntegerField()
    plus_four = models.IntegerField(null=True)
    city = models.CharField(max_length=25)
    state = USStateField()

    class Meta:
        unique_together = ('zip_code', 'city')

class Agency(models.Model):
    """ Agencies of the government that are referenced in the HMDA dataset. """

    hmda_id = models.IntegerField(primary_key=True)
    acronym = models.CharField(max_length=10)
    full_name = models.CharField(max_length=50)

    objects = AgencyManager()

class TopHolderInstitution(models.Model):
    """ Top holder institutions can be international, so we store 
    them differently. """
    year = models.SmallIntegerField()
    name = models.CharField(max_length=30)
    city = models.CharField(max_length=25)
    state = models.CharField(max_length=2, null=True)
    country = models.CharField(max_length=40)
    rssd_id = models.CharField(
        max_length=10,
        unique=True,
        help_text='Id on the National Information Center repository', 
        null=True)


class Institution(models.Model):
    """ An institution's (aka respondant) details. These can change per year.
    """

    year = models.SmallIntegerField()
    ffiec_id = models.CharField(max_length=10)
    agency = models.ForeignKey('Agency')
    tax_id = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    mailing_address = models.CharField(max_length=40)
    zip_code = models.ForeignKey('ZipCodeCityState', null=False)
    rssd_id = models.CharField(
        max_length=10,
        null=True,
        help_text='Id on the National Information Center repository')
    parent = models.ForeignKey(
        'self',
        null=True,
        related_name='children',
        help_text='The parent institution')
    top_holder = models.ForeignKey(
        'TopHolderInstitution',
        related_name='descendants',
        null=True,
        help_text='The company at the top of the ownership chain.')

    class Meta:
        unique_together = ('ffiec_id', 'agency')
