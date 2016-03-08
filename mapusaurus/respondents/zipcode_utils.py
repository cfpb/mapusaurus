from django.db.utils import IntegrityError
from respondents.models import ZipcodeCityStateYear

def create_zipcode(zip_code, city, state, year):

    zipcode_city_year = ZipcodeCityStateYear(
        city = city,
        state = state,
        year = year
    )
    
    if '-' in zip_code:
        zip_code, plus_four = zip_code.split('-')
        zipcode_city_year.plus_four = plus_four

    zipcode_city_year.zip_code = zip_code
    try: 
        zipcode_city_year.save()
    except IntegrityError:
        results = ZipcodeCityStateYear.objects.filter(
            zip_code=zip_code, 
            city=city,
            year=year)
        if len(results) > 0:
            return results[0]
        else:
            raise
    return zipcode_city_year

