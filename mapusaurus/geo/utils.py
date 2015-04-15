#Checks to see if bounds are floats. 
def check_bounds(northEastLat, northEastLon, southWestLat, southWestLon):
    try: 
        maxlat, minlon, minlat, maxlon = float(northEastLat), float(southWestLon), float(southWestLat), float(northEastLon)
        bounds = (maxlat, minlon, minlat, maxlon) 
        return bounds
    except:
        return None 