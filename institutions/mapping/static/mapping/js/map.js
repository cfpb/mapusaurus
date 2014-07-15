'use strict';

/* We want to be able to trigger a callback whenever a JSON tile loads, so we
 * create a custom GeoJSON tile layer */
L.TileLayer.HookableGeoJSON = L.TileLayer.GeoJSON.extend({
    _tileLoaded: function() {
        //  "super"
        L.TileLayer.GeoJSON.prototype._tileLoaded.apply(this, arguments);

        if (this.options.afterTileLoaded) {
            this.options.afterTileLoaded.apply(this, arguments);
        }
    }
});

var Mapusaurus = {
    //  Leaflet map
    map: null,
    //  Leaflet layers
    layers: {tract: {minority: null}},
    //  Tracks layer data/stats
    dataStore: {tract: {}},
    //  Tracks which tracts have been drawn. Gets cleared when zooming
    drawn: {},
    //  Stores stat data when the associated geos aren't loaded
    dataWithoutGeo: {tract: {minority: {}}},
    //  Keep track of which stateXcounties we've loaded
    statsLoaded: {minority: {}},

    //  Some style info
    bubbleStyle: {fillColor: '#fff', fillOpacity: 0.9, weight: 2,
                  color: '#000'},
    //  fillColor will be assigned when rendering
    tractStyle: {stroke: true, fillOpacity: 0.7, weight: 2, color: '#babbbd',
                 fill: true},
    //  used when loading census tracts
    loadingStyle: {stroke: true, weight: 2, color: '#babbbd', fill: false},
    //  population-less tracts
    noStyle: {stroke: false, fill: false},

    initialize: function (map) {
        map.setView([41.88, -87.63], 12);
        Mapusaurus.map = map;
        Mapusaurus.addKey(map);
        Mapusaurus.layers.tract.minority = new L.TileLayer.HookableGeoJSON(
            '/shapes/tiles/tracts/{z}/{x}/{y}', {
                afterTileLoaded: Mapusaurus.loadedCensusTile
            }, {
                onEachFeature: Mapusaurus.eachTract,
                style: Mapusaurus.minorityContinousStyle,
                // Don't redraw any tracts
                filter: function(feature) {
                    return !_.has(Mapusaurus.drawn, feature.properties.geoid);
                }
        });
        Mapusaurus.layers.tract.minority.addTo(map);
        if (Mapusaurus.urlParam('lender')) {
            Mapusaurus.layers.tract.loanVolume = L.layerGroup([]);
            Mapusaurus.layers.tract.loanVolume.addTo(map);
            Mapusaurus.dataWithoutGeo.tract.loanVolume = {};
            Mapusaurus.statsLoaded.loanVolume = {};
        }
        //  Census tracts get cleared whenever zooming in/out (analogous to
        //  other tile layers)
        map.on('zoomstart', function() { Mapusaurus.drawn = {}; });
        //  Turn off the census tract layer if too zoomed out
        map.on('zoomend', function() {
            if (map.getZoom() > 10 &&
                !map.hasLayer(Mapusaurus.layers.tract.minority)) {
                Mapusaurus.layers.tract.minority.addTo(map);
            } else if (map.getZoom() <= 10 &&
                       map.hasLayer(Mapusaurus.layers.tract.minority)) {
                map.removeLayer(Mapusaurus.layers.tract.minority);
            }
        });

        //  Selector to change bucket/continuous shading
        $('#style-selector').on('change', function() {
            Mapusaurus.layers.tract.minority.setStyle(
                Mapusaurus[$('#style-selector').val()]);
        });
    },

    /* Called after each tile of census tract geojson data loads */
    loadedCensusTile: function(tile) {
        var geoids = _.map(tile.datum.features, function(feature) {
            return feature.properties.geoid;
        });

        Mapusaurus.updateDataWithoutGeos(geoids);
        Mapusaurus.fetchMissingStats(geoids);

        Mapusaurus.layers.tract.minority.geojsonLayer.bringToBack();
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

    /* Style/handling function for each census tract loaded from the geoJson
     * tile layer. Adds interactions */
    eachTract: function(feature, layer) {
        var geoid = feature.properties.geoid;
        Mapusaurus.drawn[geoid] = true;
        if (!_.has(Mapusaurus.dataStore.tract, geoid)) {
            Mapusaurus.dataStore.tract[geoid] = feature.properties;
        }
        //  keep expected functionality with double clicking
        layer.on('dblclick', function(ev) {
            Mapusaurus.map.setZoomAround(ev.latlng,
                                         Mapusaurus.map.getZoom() + 1);
        });
        //  hover bubble
        layer.on('mouseover mousemove', function(e){
            var marker = new L.Rrose({
                offset: new L.Point(0, -10),
                closeButton: false, 
                autoPan: false
            });
            Mapusaurus.dataStore.tract[geoid].marker = marker;
            marker.setContent(Mapusaurus.tractHoverText(geoid))
                  .setLatLng(e.latlng)
                  .openOn(Mapusaurus.map);
        });
        layer.on('mouseout', function(){
            Mapusaurus.map.closePopup();
        });
        layer.setStyle(Mapusaurus.minorityContinuousStyle(feature));
    },

    /* Depending on whether or not stats have been loaded, the hover text may
     * be different */
    tractHoverText: function(geoid) {
        var tract = Mapusaurus.dataStore.tract[geoid];
        if (_.has(tract, 'layer_minority')) {
            return (
                (1 - tract['layer_minority']['non_hisp_white_only_perc']) *
                100).toFixed() + '% "Minority"';
        } else {
            return 'Loading...';
        }
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
                var geoProps = Mapusaurus.dataStore.tract[geoid];
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
        //  This is a list of triples: [[layer name, state, county]]
        var missingStats = [];
        _.each(_.keys(Mapusaurus.layers.tract), function(layerName) {
            //  We only care about unseen stat data
            var missingData = _.filter(newTracts, function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid],
                    stateCounty = geo.statefp +
                                  geo.countyfp;
                return !Mapusaurus.statsLoaded[layerName][stateCounty];
            });
            //  convert to state + county strings
            missingData = _.map(missingData, function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid];
                return geo.statefp + geo.countyfp;
            });
            //  remove any duplicates; we end with what state/counties need to
            //  be retrieved
            missingData = _.uniq(missingData);

            //  Keep track of what we will be loading
            _.each(missingData, function(stateCounty) {
                //  Add to the list of data to load
                missingStats.push([layerName, stateCounty.substr(0, 2),
                                   stateCounty.substr(2)]);
                //  Signify that we are loading it...
                Mapusaurus.statsLoaded[layerName][stateCounty] = 'loading';
            });
        });
        if (missingStats.length > 0) {
            Mapusaurus.batchLoadStats(missingStats);
        }
    },

    /* We load stats data in one batch request. We need to provide the
     * endpoint/layer we care about, the data it needs (state, county, etc.),
     * and then we need to process the result. */
    batchLoadStats: function(missingStats) {
        var requests = _.map(missingStats, function(triple) {
            var params = {'state_fips': triple[1],
                          'county_fips': triple[2]};
            if (Mapusaurus.urlParam('lender')) {
                params['lender'] = Mapusaurus.urlParam('lender');
            }
            return {endpoint: triple[0], params: params};
        });

        $.ajax({
            type: 'POST',
            url: '/batch',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({requests: requests}),
            success: Mapusaurus.makeBatchSuccessFn(requests)
        });
    },

    /*  As the success function for making a batch request relies on the
     *  requests made, this returns a closure to handle the results of a batch
     *  load */
    makeBatchSuccessFn: function(requests) {
        return function(data) {
            var toDraw = {};
            _.each(_.keys(Mapusaurus.layers.tract), function(layerName) {
                toDraw[layerName] = [];
            });
            _.each(requests, function(request, idx) {
                var layerName = request['endpoint'],
                    llName = 'layer_' + layerName,
                    response = data['responses'][idx],
                    stateCounty = request.params['state_fips'] +
                                  request.params['county_fips'];
                _.each(_.keys(response), function(geoid) {
                    var geo = Mapusaurus.dataStore.tract[geoid];
                    //  Have not loaded the geo data yet
                    if (!geo) {
                        Mapusaurus.dataWithoutGeo.tract[layerName][geoid] =
                            response[geoid];
                    //  Have the geo data, but haven't drawn the stats yet
                    } else if (!geo[llName]) {
                        geo[llName] = response[geoid];
                        toDraw[layerName].push(geoid);
                    }
                });
                Mapusaurus.statsLoaded[layerName][stateCounty] = true;
            });
            Mapusaurus.draw(toDraw);
        };
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
                    Mapusaurus.layers.tract.minority.geojsonLayer.setStyle(
                        Mapusaurus.minorityContinuousStyle);
                    break;
                case 'loanVolume':
                    _.each(geoData, function(geo) {
                        Mapusaurus.layers.tract.loanVolume.addLayer(
                            Mapusaurus.makeBubble(geo)
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
        circle.on('mouseover mousemove', function(e){
            new L.Rrose({ offset: new L.Point(0,-10), closeButton: false, autoPan: false })
              .setContent(data['volume'] + ' loans<br />' + data['num_households'] + ' households')
              .setLatLng(e.latlng)
              .openOn(Mapusaurus.map);
        });
        circle.on('mouseout', function(){ 
            Mapusaurus.map.closePopup();
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
        var geoid = feature.properties.geoid,
            tract = Mapusaurus.dataStore.tract[geoid];
        // Different styles for when we are loading, the tract has zero pop, or
        // we have percentages
        if (!_.has(tract, 'layer_minority')) {
            return Mapusaurus.loadingStyle;
        } else if (tract['layer_minority']['total_pop'] === 0) {
            return Mapusaurus.noStyle;
        } else {
            var minorityPercent = 1 - tract['layer_minority'][
                                'non_hisp_white_only_perc'],
                bucket = Mapusaurus.toBucket(minorityPercent),
                // convert given percentage to percents within bucket's bounds
                bucketPercent = percentFn(minorityPercent, bucket);
            return $.extend({}, Mapusaurus.tractStyle, {
                fillColor: Mapusaurus.colorFromPercent(bucketPercent,
                                                       bucket.colors)
            });
        }
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
