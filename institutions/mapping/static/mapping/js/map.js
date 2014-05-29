'use strict';

var Mapusaurus = {
    map: null,
    dataStore: {tract: {}},
    layers: {tract: {minority: null}},
    dataWithoutGeo: {tract: {minority: {}}},

    initialize: function (map) {
        map.setView([41.88, -87.63], 12);
        Mapusaurus.map = map;
        Mapusaurus.layers.tract.minority = L.geoJson(
            {type: 'FeatureCollection', features: []},
            {onEachFeature: Mapusaurus.eachMinority}
        );
        Mapusaurus.layers.tract.minority.addTo(map);
        map.on('moveend', Mapusaurus.reloadGeo);
        map.on('zoomend', Mapusaurus.reloadGeo);
        Mapusaurus.reloadGeo();
    },

    /* Whenever the map is shifted/zoomed, reload geo data */
    reloadGeo: function() {
        /* To be responsive, only load census tract data at zoom-level 10
         * or above */
        if (Mapusaurus.map.getZoom() >= 10) {
            var bounds = Mapusaurus.map.getBounds();
            //  This is north-western-hemisphere-centric for now
            Mapusaurus.loadTractData(1, bounds.getSouth(), bounds.getNorth(),
                                     bounds.getWest(), bounds.getEast());
        }
    },

    contTract: function(feature, layer) {
        layer.setStyle({weight: 1, color: '#000'});
    },

    /* Recursively load census tract geo data into Mapusaurus.geos */
    loadTractData: function(page, minlat, maxlat, minlon, maxlon) {
        $.getJSON('/shapes/tracts-in/?minlat=' + minlat.toString() +
                  '&maxlat=' + maxlat.toString() +
                  '&minlon=' + minlon.toString() +
                  '&maxlon=' + maxlon.toString() +
                  '&page_num=' + page.toString(),
                  function(data) {
            var newTracts = [];
            for (var idx = 0; idx < data.features.length; idx++) {
                var feature = data.features[idx],
                    geoid = feature.properties.geoid;
                if (!Mapusaurus.dataStore.tract[geoid]) {
                    Mapusaurus.dataStore.tract[geoid] = feature;
                    newTracts.push(geoid);
                }
            }
            if (newTracts.length > 0) {
                Mapusaurus.updateDataWithoutGeos(newTracts);
                Mapusaurus.fetchMissingData(newTracts);
            }
            if (data.features.length > 0) {
                // continue with next page
                Mapusaurus.loadTractData(page + 1, minlat, maxlat, minlon,
                                         maxlon);
            }
        });
    },

    updateDataWithoutGeos: function(newTracts) {
        var toDraw = [];
        for (var idx = 0; idx < newTracts.length; idx++) {
            var geoid = newTracts[idx];
            if (Mapusaurus.dataWithoutGeo.tract.minority[geoid]) {
                Mapusaurus.dataStore.tract[geoid].properties.layer_minority =
                    Mapusaurus.dataWithoutGeo.tract.minority[geoid];
                toDraw.push(geoid);
                delete Mapusaurus.dataWithoutGeo.tract.minority[geoid];
            }
        }
        Mapusaurus.draw(toDraw);
    },

    fetchMissingData: function(newTracts) {
        var missingData = {},
            afterLoad = null;
        for (var idx = 0; idx < newTracts.length; idx++) {
            var geoid = newTracts[idx],
                geo = Mapusaurus.dataStore.tract[geoid];
            if (!geo.properties.layer_minority) {
                var state = geo.properties.statefp,
                    county = geo.properties.countyfp;
                if (!missingData[state]) {
                    missingData[state] = {};
                }
                if (!missingData[state][county]) {
                    missingData[state][county] = true;
                }
            }
        }
        // function to be called after each data load
        afterLoad = function(data) {
            var toRedraw = [];
            for (var geoid in data) {
                var geo = Mapusaurus.dataStore.tract[geoid];
                if (!geo) {
                    Mapusaurus.dataWithoutGeo.tract.minority[geoid] =
                        data[geoid].non_hisp_white_only_perc;
                } else if (!geo.properties.layer_minority) {
                    geo.properties.layer_minority =
                        data[geoid].non_hisp_white_only_perc;
                    toRedraw.push(geoid);
                }
            }
            Mapusaurus.draw(toRedraw);
        };
        for (var state in missingData) {
            for (var county in missingData[state]) {
                $.getJSON('/census/race-summary?state_fips=' +
                          state + '&county_fips=' + county, afterLoad);
            }
        }
    },

    eachMinority: function(feature, layer) {
      var nonMinorityPercent = feature.properties.layer_minority;
      layer.setStyle({
          fillColor: Mapusaurus.colorFromPercent(1 - nonMinorityPercent,
                                                 246, 217, 211, 209, 65, 36),
          fillOpacity: 0.7,
          weight: 2,
          color: '#babbbd'
      });
      //  keep expected functionality with double clicking
      layer.on('dblclick', function() {
        Mapusaurus.map.zoomIn();
      });
      layer.on('mouseover', function() {
        $('<div></div>', {
          id: 'perc-popup-' + feature.properties.geoid,
          text: (nonMinorityPercent * 100).toFixed() + 
                 '% Non-hispanic White-Only',
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
    },

    draw: function(geoids) {
        var toDraw = [];
        for (var idx = 0; idx < geoids.length; idx++) {
          toDraw.push(Mapusaurus.dataStore.tract[geoids[idx]]);
        }
        Mapusaurus.layers.tract.minority.addData(toDraw);
    },

    colorFromPercent: function(percent, lowR, lowG, lowB, highR, highG, highB) {
        var diffR = (highR - lowR) * percent,
            diffG = (highG - lowG) * percent,
            diffB = (highB - lowB) * percent;
        return 'rgb(' + (lowR + diffR).toFixed() + ', ' + (lowG + diffG).toFixed() + ', ' + (lowB + diffB).toFixed() + ')';
    }
};
