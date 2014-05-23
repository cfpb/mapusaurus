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
            fillColor: Mapusaurus.colorFromPercent(1 - nonMinorityPercent),
            fillOpacity: 0.7,
            color: '#babbbd'
        }
    },

    colorFromPercent: function(percent) {
        if (percent < 0.5) {
            if (percent < 0.25) {
                // red orange 20%
                return '#f6d9d3';
            }
            else {
                // red orange 50%
                return '#e8a091';
            }
        }
        else {
            if (percent > 0.75) {
                // red orange 80%
                return '#da6750';
            }
            else {
                // red orange 100%
                return '#d12124';
            }
        }
    }
};
