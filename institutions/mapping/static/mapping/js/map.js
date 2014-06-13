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
    //  Some style info
    bubbleStyle: {fillColor: '#fff', fillOpacity: 0.9, weight: 2,
                  color: '#000'},
    //  fillColor will be assigned when rendering
    tractStyle: {fillOpacity: 0.7, weight: 2, color: '#babbbd'},

    initialize: function (map) {
        map.setView([41.88, -87.63], 12);
        Mapusaurus.map = map;
        Mapusaurus.addKey(map);
        Mapusaurus.layers.tract.minority = L.geoJson(
            {type: 'FeatureCollection', features: []},
            {onEachFeature: Mapusaurus.eachMinority,
             style: Mapusaurus.minorityContinuousStyle}
        );
        Mapusaurus.layers.tract.minority.addTo(map);
        if (Mapusaurus.urlParam('lender')) {
            Mapusaurus.layers.tract.loanVolume = L.layerGroup([]);
            Mapusaurus.layers.tract.loanVolume.addTo(map);
            Mapusaurus.dataWithoutGeo.tract.loanVolume = {};
        }
        //  @todo: really, we only care about the part of the viewport which
        //  is new
        map.on('moveend', Mapusaurus.reloadGeo);
        //  @todo: really, we only care on zoom-out + part which is new
        map.on('zoomend', Mapusaurus.reloadGeo);
        //  Connect style selector
        $('#style-selector').on('change', function() {
            Mapusaurus.layers.tract.minority.setStyle(
                Mapusaurus[$('#style-selector').val()]);
        });
        //  Kick it off
        Mapusaurus.reloadGeo();
    },

    /* Indicates what the colors mean */
    addKey: function(map) {
        var key = L.control();
        key.onAdd = function() {
            return L.DomUtil.get('key');
        };
        key.addTo(map);
    },

    /* Naive url parameter parser */
    urlParam: function(field) {
        var url = window.location.search.replace('?', ''),
            keyValueStrs = url.split('&'),
            pairs = _.map(keyValueStrs, function(keyValueStr) {
                return keyValueStr.split('=');
            }),
            params = _.reduce(pairs, function(soFar, pair) {
                if (pair.length === 2) {
                    soFar[pair[0]] = pair[1];
                }
                return soFar;
            }, {});
        return params[field];
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
        var toDraw = {},  // geoids by layer
            undrawnData = Mapusaurus.dataWithoutGeo.tract;
        //  For each layer
        _.each(_.keys(undrawnData), function (layerName) {
            toDraw[layerName] = [];

            //  For each shape
            _.each(newTracts, function(geoid) {
                var geoProps = Mapusaurus.dataStore.tract[geoid].properties;
                //  Check if the data can now be drawn
                if (_.has(undrawnData[layerName], geoid)) {
                    geoProps['layer_' + layerName] = 
                        undrawnData[layerName][geoid];
                    toDraw[layerName].push(geoid);
                    delete undrawnData[layerName][geoid];
                }
            });
        });
        Mapusaurus.draw(toDraw);
    },

    /* We have geos without their associated stats - kick off the load */
    fetchMissingStats: function(newTracts) {
        //  For each layer
        _.each(_.keys(Mapusaurus.layers.tract), function(layerName) {
            //  We only care about unseen stat data
            var missingData = _.filter(newTracts, function(geoid) {
              return !_.has(Mapusaurus.dataStore.tract[geoid].properties,
                            'layer_' + layerName);
            });
            //  convert to state + county strings
            missingData = _.map(missingData, function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid];
                return geo.properties.statefp + geo.properties.countyfp;
            });
            //  remove any duplicates; we end with what state/counties need to
            //  be retrieved
            missingData = _.uniq(missingData);

            //  start loading the data for each county
            /*
            _.each(missingData, function(stateCounty) {
                var state = stateCounty.substr(0, 2),
                    county = stateCounty.substr(2);
                Mapusaurus.loadLayerData(layerName, state, county);
            });
            */
            missingData = _.map(missingData, function(stateCounty) {
                return {'state_fips': stateCounty.substr(0, 2),
                        'county_fips': stateCounty.substr(2)};
            });
            Mapusaurus.loadLayerData(layerName, missingData);
        });
    },



    /* Each layer has a different end point associated with it. Use that to 
     * load (and eventually, draw) the layer stats */
    loadLayerData: function(layerName, stateCounties) {
        $.ajax({
            type: 'POST',
            url: '/batch',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                requests: _.map(stateCounties, function(stateCounty) {
                    return {endpoint: 'race-summary',
                            params: stateCounty};
                })
            }),
            success: function(data) {
                var toDraw = {};
                toDraw[layerName] = [];
                _.each(data.responses, function(response) {
                    _.each(_.keys(response), function(geoid) {
                        var geo = Mapusaurus.dataStore.tract[geoid];
                        //  Have not loaded the geo data yet
                        if (!geo) {
                            Mapusaurus.dataWithoutGeo.tract[layerName][geoid] =
                                response[geoid];
                        //  Have the geo data, but haven't drawn the stats yet
                        } else if (!geo.properties['layer_' + layerName]) {
                            geo.properties['layer_' + layerName] = response[geoid];
                            toDraw[layerName].push(geoid);
                        }
                    });
                });
                Mapusaurus.draw(toDraw);
            }
        });
    },
    /* Each layer has a different end point associated with it. Use that to 
     * load (and eventually, draw) the layer stats */
    loadLayerData2: function(layerName, state, county) {
        var url = null;
        switch(layerName) {
            case 'minority':
                url = ('/census/race-summary?state_fips=' + state +
                       '&county_fips=' + county);
                break;
            case 'loanVolume':
                url = ('/hmda/volume?state_fips=' + state + 
                       '&county_fips=' + county +
                       '&lender=' + Mapusaurus.urlParam('lender'));
                break;
            default:
                window.alert('Unknown layer to load');
        }

        //  Now kick off the load for that layer
        $.getJSON(url, function(data) {
            var toDraw = {};
            toDraw[layerName] = [];
            _.each(_.keys(data), function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid];
                //  Have not loaded the geo data yet
                if (!geo) {
                    Mapusaurus.dataWithoutGeo.tract[layerName][geoid] =
                        data[geoid];
                //  Have the geo data, but haven't drawn the stats yet
                } else if (!geo.properties['layer_' + layerName]) {
                    geo.properties['layer_' + layerName] = data[geoid];
                    toDraw[layerName].push(geoid);
                }
            });
            Mapusaurus.draw(toDraw);
        });
    },

    /* Given a list of geo ids, segmented by layer name, add them to the
     * leaflet layer. */
    draw: function(layerToGeoids) {
        // For each layer
        _.each(_.keys(layerToGeoids), function(layerName) {
            var geoData = _.map(layerToGeoids[layerName], function(geoid) {
              return Mapusaurus.dataStore.tract[geoid];
            });
            switch(layerName) {
                case 'minority':
                    // Filter out geos with no people; don't want to draw them
                    geoData = _.filter(geoData, function(geo) {
                        return geo.properties['layer_minority'][
                            'total_pop'] > 0;
                    });
                    Mapusaurus.layers.tract.minority.addData(geoData);
                    Mapusaurus.layers.tract.minority.bringToBack();
                    break;
                case 'loanVolume':
                    _.each(geoData, function(geo) {
                        Mapusaurus.layers.tract.loanVolume.addLayer(
                            Mapusaurus.makeBubble(geo.properties)
                        );
                    });
                    break;
            }
        });
    },

    /* Styles/extras for originations layer */
    makeBubble: function(geoProps) {
        var data = geoProps['layer_loanVolume'],
            circle = L.circle([geoProps.intptlat, geoProps.intptlon],
                              100 * data['volume_per_100_households'],
                              Mapusaurus.bubbleStyle);
        //  keep expected functionality with double clicking
        circle.on('dblclick', function(ev) {
            Mapusaurus.map.setZoomAround(
                ev.latlng, Mapusaurus.map.getZoom() + 1);
        });
        circle.on('mouseover', function() {
            var div = $('<div></div>', {
                id: 'household-popup-' + geoProps.geoid,
                class: 'hover-box'
            });
            div.html(data['volume'] + ' loans<br />' +
                     data['num_households'] + ' households');
            div.appendTo('#map');
        });
        circle.on('mouseout', function() {
            $('#household-popup-' +
              geoProps.geoid).remove();
        });
        return circle;
    },

    //  Used to determine color within a gradient
    minorityContinuousStyle: function(feature) {
        return Mapusaurus.minorityStyle(
            feature, 
            function(minorityPercent, bucket) {
                return (minorityPercent - bucket.lowerBound) / bucket.span;
            }
        );
    },
    //  Determines colors via distinct buckets
    minorityBucketedStyle: function(feature) {
        return Mapusaurus.minorityStyle(feature, function() { return 0.5; });
    },
    //  Shared function for minority styling; called by the two previous fns
    minorityStyle: function(feature, percentFn) {
        var minorityPercent = 1 - feature.properties['layer_minority'][
                                'non_hisp_white_only_perc'],
            bucket = Mapusaurus.toBucket(minorityPercent),
            // convert given percentage to percents within bucket's bounds
            bucketPercent = percentFn(minorityPercent, bucket);
        return $.extend({}, Mapusaurus.tractStyle, {
            fillColor: Mapusaurus.colorFromPercent(bucketPercent,
                                                   bucket.colors)
        });
    },

    /* Style/extras for each census tract in the minorities layer */
    eachMinority: function(feature, layer) {
      var nonMinorityPercent = feature.properties['layer_minority'][
          'non_hisp_white_only_perc'];
      //  keep expected functionality with double clicking
      layer.on('dblclick', function(ev) {
        Mapusaurus.map.setZoomAround(ev.latlng, Mapusaurus.map.getZoom() + 1);
      });
      layer.on('mouseover', function() {
        $('<div></div>', {
          id: 'perc-popup-' + feature.properties.geoid,
          text: (nonMinorityPercent * 100).toFixed() + 
                 '% Non-hispanic White-Only',
          class: 'hover-box'
        }).appendTo('#map');
      });
      layer.on('mouseout', function() {
        $('#perc-popup-' + feature.properties.geoid).remove();
      });
    },

    colorRanges: [
        {
            span: 0.5,
            lowerBound: 0,
            colors: {
                lowR: 255,
                lowG: 255,
                lowB: 217,
                highR: 198,
                highG: 234,
                highB: 178
            }
        },
        {
            span: 0.3,
            lowerBound: 0.5,
            colors: {
                lowR: 198,
                lowG: 234,
                lowB: 178,
                highR: 14,
                highG: 144,
                highB: 194
            }
        },
        {
            span: 0.2,
            lowerBound: 0.8,
            colors: {
                lowR: 14,
                lowG: 144,
                lowB: 194,
                highR: 29,
                highG: 92,
                highB: 170
            }
        }
    ],

    toBucket: function(percent) {
        var i,
            len = Mapusaurus.colorRanges.length;
        for (i = 0; i < len - 1; i++) {
            //  Next bucket is too far
            if (Mapusaurus.colorRanges[i + 1].lowerBound > percent) {
                return Mapusaurus.colorRanges[i];
            }
        } 
        return Mapusaurus.colorRanges[len - 1];  //  last color
    },

    /* Given low and high colors and a percent, figure out the RGB of said
     * percent in that scale */
    colorFromPercent: function(percent, c) {
        var diffR = (c.highR - c.lowR) * percent,
            diffG = (c.highG - c.lowG) * percent,
            diffB = (c.highB - c.lowB) * percent;
        return 'rgb(' + (c.lowR + diffR).toFixed() + ', ' +
               (c.lowG + diffG).toFixed() + ', ' +
               (c.lowB + diffB).toFixed() + ')';
    }
};
