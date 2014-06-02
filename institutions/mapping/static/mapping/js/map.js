'use strict';

var Mapusaurus = {
    //  Leaflet map
    map: null,
    //  Leaflet layers
    layers: {tract: {minority: null}},
    //  Stores geo data, along with fields for layers
    dataStore: {tract: {}},
    //  Stores stat data when the associated geos aren't loaded
    dataWithoutGeo: {tract: {minority: {}}},

    initialize: function (map) {
        map.setView([41.88, -87.63], 12);
        Mapusaurus.map = map;
        Mapusaurus.layers.tract.minority = L.geoJson(
            {type: 'FeatureCollection', features: []},
            {onEachFeature: Mapusaurus.eachMinority}
        );
        Mapusaurus.layers.tract.minority.addTo(map);
        //  @todo: really, we only care about the part of the viewport which
        //  is new
        map.on('moveend', Mapusaurus.reloadGeo);
        //  @todo: really, we only care on zoom-out + part which is new
        map.on('zoomend', Mapusaurus.reloadGeo);
        //  Kick it off
        Mapusaurus.reloadGeo();
    },

    /* Whenever the map is shifted/zoomed, reload geo data */
    reloadGeo: function() {
        var bounds = Mapusaurus.map.getBounds(),
            halfWidth = Math.abs(bounds.getEast() - bounds.getWest()) / 2,
            halfHeight = Math.abs(bounds.getNorth() - bounds.getSouth()) / 2,
            //  NW-hemisphere centric
            expandedN = bounds.getNorth() + halfHeight,
            expandedS = bounds.getSouth() - halfHeight,
            expandedW = bounds.getWest() - halfWidth,
            expandedE = bounds.getEast() + halfWidth;

        /* To be responsive, only load census tract data at zoom-level 10
         * or above */
        if (Mapusaurus.map.getZoom() >= 10) {
            Mapusaurus.loadTractData(
                1, 
                L.latLngBounds(L.latLng(expandedS, expandedW),
                               L.latLng(expandedN, expandedE)));
        }
    },

    /* Load census tract geo data (by pages) into dataStore. Bounds should
     * remain consistent between pages of results */
    loadTractData: function(page, bounds) {
        //  This is north-western-hemisphere-centric for now
        $.getJSON('/shapes/tracts-in/?minlat=' + bounds.getSouth().toString() +
                  '&maxlat=' + bounds.getNorth().toString() +
                  '&minlon=' + bounds.getWest().toString() +
                  '&maxlon=' + bounds.getEast().toString() +
                  '&page_num=' + page.toString(),
                  function(data) {
            var newTracts = [];   //  geos we've never seen

            //  Collect new tracts, add them to dataStore
            _.each(data.features, function(feature) {
                var geoid = feature.properties.geoid;
                if (!_.has(Mapusaurus.dataStore.tract, geoid)) {
                    Mapusaurus.dataStore.tract[geoid] = feature;
                    newTracts.push(geoid);
                }
            });

            //  Check if there's anything new to draw, load stats data
            if (newTracts.length > 0) {
                Mapusaurus.updateDataWithoutGeos(newTracts);
                Mapusaurus.fetchMissingStats(newTracts);
            }

            //  Continue with next page of geo results
            if (data.features.length > 0) {
                Mapusaurus.loadTractData(page + 1, bounds);
            }
        });
    },

    /*  We may have previously loaded stats data without the geos. Run through
     *  that data and see if the new geo data matches */
    updateDataWithoutGeos: function(newTracts) {
        var toDraw = [];  // geoids
        _.each(newTracts, function(geoid) {
            //  Stats data is present
            if (_.has(Mapusaurus.dataWithoutGeo.tract.minority, geoid)) {
                Mapusaurus.dataStore.tract[geoid].properties.layer_minority =
                    Mapusaurus.dataWithoutGeo.tract.minority[geoid];
                toDraw.push(geoid);
                delete Mapusaurus.dataWithoutGeo.tract.minority[geoid];
            }
        });
        Mapusaurus.draw(toDraw);
    },

    /* We have geos without their associated stats - kick off the load */
    fetchMissingStats: function(newTracts) {
        var missingData = null,   //  state + county strings
            afterLoad = null;     //  fn to be called after each data load
        //  We only care about unseen stat data
        missingData = _.filter(newTracts, function(geoid) {
            return !_.has(Mapusaurus.dataStore.tract[geoid].properties,
                          'layer_minority');
        });
        //  convert to state + county strings
        missingData = _.map(missingData, function(geoid) {
            var geo = Mapusaurus.dataStore.tract[geoid];
            return geo.properties.statefp + geo.properties.countyfp;
        });
        missingData = _.uniq(missingData);
        
        afterLoad = function(data) {
            var toDraw = [];
            _.each(_.keys(data), function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid];
                //  Have not loaded the geo data yet
                if (!geo) {
                    Mapusaurus.dataWithoutGeo.tract.minority[geoid] =
                        data[geoid].non_hisp_white_only_perc;
                //  Have the geo data, but haven't drawn the stats yet
                } else if (!geo.properties.layer_minority) {
                    geo.properties.layer_minority =
                        data[geoid].non_hisp_white_only_perc;
                    toDraw.push(geoid);
                }
            });
            Mapusaurus.draw(toDraw);
        };
        //  start loading the stat data
        _.each(missingData, function(stateCounty) {
            var state = stateCounty.substr(0, 2),
                county = stateCounty.substr(2);
            $.getJSON('/census/race-summary?state_fips=' + state +
                      '&county_fips=' + county, afterLoad);
        });
    },

    /* Given a list of geo ids, add them to the minority layer */
    draw: function(geoids) {
        var geoData = _.map(geoids, function(geoid) {
            return Mapusaurus.dataStore.tract[geoid];
        });
        Mapusaurus.layers.tract.minority.addData(geoData);
    },

    /* Style/extras for each census tract in the minorities layer */
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
      layer.on('dblclick', function(ev) {
        Mapusaurus.map.setZoomAround(ev.latlng, Mapusaurus.map.getZoom() + 1);
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

    /* Given low and high colors and a percent, figure out the RGB of said
     * percent in that scale */
    colorFromPercent: function(percent, lowR, lowG, lowB, highR, highG, highB) {
        var diffR = (highR - lowR) * percent,
            diffG = (highG - lowG) * percent,
            diffB = (highB - lowB) * percent;
        return 'rgb(' + (lowR + diffR).toFixed() + ', ' +
               (lowG + diffG).toFixed() + ', ' +
               (lowB + diffB).toFixed() + ')';
    }
};
