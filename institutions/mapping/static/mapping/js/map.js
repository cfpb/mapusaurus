var Mapusaurus = {
    function mainMapInit(map, options) {
        //Use Leaflet API here. 
        var tractsJsonUrl = '{% url "tractsgeojson"%}?state_fips=17&county_fips=031';

        $.getJSON(tractsJsonUrl, function(data) {
            var lat = data.features[0].properties.intptlat,
                lon = data.features[0].properties.intptlon;

            map.setView([lat, lon], 12);
            L.geoJson(data).addTo(map);
        });
    }
}

