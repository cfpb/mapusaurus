from django.db import IntegrityError

from respondants.models import ZipcodeCityState

def create_zipcode(zip_code, city, state):

    zipcode_city = ZipcodeCityState(
        city = city,
        state = state,
    )
    
    if '-' in zip_code:
        zip_code, plus_four = zip_code.split('-')
        zipcode_city.plus_four = plus_four

    zipcode_city.zip_code = zip_code
    try: 
        zipcode_city.save()
    except IntegrityError:
        results = ZipCodeCityState.objects.filter(
            zip_code=zip_code, 
            state=state, 
            city=city)
        if len(results) > 0:
            return results[0]
        else:
            raise
    return zipcode_city

