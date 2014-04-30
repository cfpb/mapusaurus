from django.db import models
from localflavor.us.models.USStateField

class ZipcodeCityState(models.Model):
    """ For each zipcode, maintain the city, state information. """
    zip_code = models.IntegerField()
    plus_four = models.IntegerField()
    city = models.CharField(max_length=25)
    state = USStateField()

class Agency(models.Model):
    """ Agencies of the government that are referenced in the HMDA dataset. """

    hmda_id = models.IntegerField(primary_key=True)
    acronym = models.CharField(max_length=10)
    full_name = models.CharField(max_length=50)

class Institution(models.Model):
    """ An institution's (aka respondant) details. These can change per year.
    """

    year = models.SmallIntegerField()
    FFIEC_id = models.CharField(max_length=10)
    agency = models.ForeignKey('Agency')
    tax_id = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    mailing_address = models.CharField(max_length=40)
    zip_code = models.ForeignKey('ZipCodeCityState')
    rssd_id = models.CharField(max_length=10)
    parent = models.ForeignKey('self')
    top_holder = models.ForeignKey('self')
