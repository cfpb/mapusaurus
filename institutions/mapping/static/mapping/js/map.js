'use strict';

var Mapusaurus = {
    map: null,
    slowLayer: null,
    initialize: function (map, options) {
        Mapusaurus.map = map;
        var tractsJsonUrl = '/shapes/tracts/?state_fips=17&county_fips=031',
            censusDataJsonUrl= 'census/race-summary?county_fips=031&state_fips=17';

        // TODO: delay rendering until census data comes back, too
        Mapusaurus.loadCensusData(censusDataJsonUrl);

        $.getJSON(tractsJsonUrl, function(data) {
            var lat = data.features[0].properties.intptlat,
                lon = data.features[0].properties.intptlon;

            map.setView([lat, lon], 12);
            L.geoJson(data, {onEachFeature: Mapusaurus.eachFeature}).addTo(map);
        });

        Mapusaurus.slowLayer = L.geoJson({type: 'FeatureCollection', features: []},
                                         {style: function() {
                                            return {weight: 3, color: '#66f'}
                                         }});
        Mapusaurus.slowLayer.addTo(map);
    },

    loadTractData: function(page) {
        var bounds = Mapusaurus.map.getBounds();
        //  Sorry, but this is north-western hemisphere-centric for now
        $.getJSON('/shapes/tracts-in/?minlat=' + bounds.getSouth().toString()
                  + '&maxlat=' + bounds.getNorth().toString()
                  + '&minlon=' + bounds.getWest().toString()
                  + '&maxlon=' + bounds.getEast().toString()
                  + '&page_num=' + page.toString(), function(data) {
          Mapusaurus.slowLayer.addData(data);
          if (data.features.length > 0) {
            Mapusaurus.loadTractData(page + 1)
          }
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
            color: '#babbbd'
        };
    },

    colorFromPercent: function(percent, lowR, lowG, lowB, highR, highG, highB) {
        var diffR = (highR - lowR) * percent,
            diffG = (highG - lowG) * percent,
            diffB = (highB - lowB) * percent;
        return 'rgb(' + (lowR + diffR).toFixed() + ', ' + (lowG + diffG).toFixed() + ', ' + (lowB + diffB).toFixed() + ')';
    },

    eachFeature: function(feature, layer) {
      layer.setStyle(Mapusaurus.polygonStyle(feature));

      //  keep expected functionality with double clicking
      layer.on('dblclick', function() {
        Mapusaurus.map.zoomIn();
      });
      var nonHispanicWhite = Mapusaurus.censusData[feature.properties.geoid].non_hisp_white_only_perc;
      layer.on('mouseover', function() {
        $('<div></div>', {
          id: 'perc-popup-' + feature.properties.geoid,
          text: (nonHispanicWhite * 100).toFixed() + '% Non-hispanic White-Only',
          css: {
            position: 'absolute',
            bottom: '85px',
            left: '50px',
            zIndex: 1002,
            backgroundColor: 'white',
            padding: '8px',
            border: '1px solid #ccc'
          }
        }).appendTo('#map');
      });
      layer.on('mouseout', function() {
        $('#perc-popup-' + feature.properties.geoid).remove();
      });
    }
};
