var Mapusaurus = {
    initialize: function (map, options) {
        //Use Leaflet API here. 
        var tractsJsonUrl = '/shapes/tracts/?state_fips=17&county_fips=031',
            censusDataJsonUrl= 'census/race-summary?county_fips=031&state_fips=17';

        // TODO: delay rendering until census data comes back, too
        Mapusaurus.loadCensusData(censusDataJsonUrl);

        $.getJSON(tractsJsonUrl, function(data) {
            var lat = data.features[0].properties.intptlat,
                lon = data.features[0].properties.intptlon;

            map.setView([lat, lon], 12);
            L.geoJson(data, {style: Mapusaurus.polygonStyle}).addTo(map);
        });
    },

    loadCensusData: function(url) {
        $.getJSON(url, function(data) {
            Mapusaurus.censusData = data;
        });
    },

    polygonStyle: function(feature) {
        var nonMinorityPercent = Mapusaurus.censusData[feature.properties.geoid].non_hisp_white_only_perc;
        return {
            fillColor: Mapusaurus.colorFromPercent(1 - nonMinorityPercent,
                                                   246, 217, 211, 209, 65, 36),
            fillOpacity: 0.7,
            weight: 2,
            clickable: false,
            color: '#babbbd'
        }
    },

    colorFromPercent: function(percent, lowR, lowG, lowB, highR, highG, highB) {
        var diffR = (highR - lowR) * percent,
            diffG = (highG - lowG) * percent,
            diffB = (highB - lowB) * percent;
        return 'rgb(' + (lowR + diffR).toFixed() + ', '
                      + (lowG + diffG).toFixed() + ', '
                      + (lowB + diffB).toFixed() + ')';
    }
};
