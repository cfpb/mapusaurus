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
    layers: {tract: null, county: null},
    //  Tracks layer data/stats
    dataStore: {tract: {}},
    //  Tracks which tracts have been drawn. Gets cleared when zooming
    drawn: {},
    notDrawn: function(feature) {
        return !_.has(Mapusaurus.drawn, feature.properties.geoid);
    },
    //  Stores stat data when the associated geos aren't loaded
    dataWithoutGeo: {minority: {}},
    //  Keep track of which stateXcounties we've loaded; also works as a list
    //  of data layers
    statsLoaded: {minority: {}},

    //  Some style info
    bubbleStyle: {fillColor: '#fff', fillOpacity: 0.9, weight: 2,
                  color: '#000'},
    //  fillColor and color will be assigned when rendering
    tractStyle: {stroke: false, fillOpacity: 0.7, weight: 2, fill: true, smoothFactor: 0.1},
    //  used when loading census tracts
    loadingStyle: {stroke: true, weight: 2, color: '#babbbd', fill: false, smoothFactor: 0.1},
    //  population-less tracts
    noStyle: {stroke: false, fill: false},
    //  used when census tracts are visible
    zoomedCountyStyle: {stroke: true, color: '#fff', weight: 2, fill: false,
                        opacity: 1.0},
    zoomedMetroStyle: {stroke: true, color: '#646464', weight: 4, fill: false,
                       opacity: 1.0, dashArray: '20,10'},
    //  used when census tracts are not visible
    biggerMetroStyle: {stroke: true, color: '#646464', weight: 4, fill: true,
                       opacity: 1.0, dashArray: '20,10', fillColor: '#646464',
                       fillOpacity: 0.5},

    initialize: function (map) {
        var mainEl = $('main'),
            centLat = parseFloat(mainEl.data('cent-lat')) || 41.88,
            centLon = parseFloat(mainEl.data('cent-lon')) || -87.63,
            $enforceBoundsEl = $('#enforce-bounds-selector');
        map.setView([centLat, centLon], 12);
        Mapusaurus.map = map;
        Mapusaurus.addKey(map);
        Mapusaurus.layers.shapes = new L.TileLayer.HookableGeoJSON(
            '/shapes/tiles/{z}/{x}/{y}', {
                afterTileLoaded: Mapusaurus.afterShapeTile
            }, {
                // Don't redraw any tracts
                filter: Mapusaurus.notDrawn,
                style: Mapusaurus.pickStyle,
                onEachFeature: Mapusaurus.eachShapeTile
        });
        Mapusaurus.layers.shapes.addTo(map);

        if (Mapusaurus.urlParam('lender')) {
            Mapusaurus.layers.loanVolume = L.layerGroup([]);
            Mapusaurus.layers.loanVolume.addTo(map);
            Mapusaurus.dataWithoutGeo.loanVolume = {};
            Mapusaurus.statsLoaded.loanVolume = {};
            $('#bubble-selector').removeClass('hidden').on('change',
                Mapusaurus.redrawBubbles);
        }
        //  Census tracts get cleared whenever zooming in/out (analogous to
        //  other tile layers)
        map.on('zoomstart', function() { Mapusaurus.drawn = {}; });
        //  Selector to change bucket/continuous shading
        $('#style-selector').on('change', function() {
            Mapusaurus.layers.shapes.geojsonLayer.setStyle(
                Mapusaurus[$('#style-selector').val()]);
        });
        $('#category-selector').on('change', function() {
            Mapusaurus.layers.shapes.geojsonLayer.setStyle(
                Mapusaurus.pickStyle);
        });

        $enforceBoundsEl.on('change', function() {
            Mapusaurus[$enforceBoundsEl.val()]();
        });
        if ($enforceBoundsEl) {
            Mapusaurus.enforceBounds();
        }

        L.control.search({
            url: '/shapes/search/?auto=1&q={s}',
            autoCollapse: true,
            animateLocation: false,
            circleLocation: false,
            markerIcon: null,
            filterJSON: function(rawjson) {
                var results = {};
                _.each(rawjson.geos, function(geo) {
                    results[geo.name] = L.latLng(geo.centlat, geo.centlon);
                });
                return results;
            },
        }).addTo(map);
    },


    isCounty: function(feature) {
        return feature.properties.geoType[0] === 2;
    },
    isTract: function(feature) {
        return feature.properties.geoType[0] === 3;
    },
    isMetro: function(feature) {
        return feature.properties.geoType[0] === 4;
    },

    /* Called after each tile of geojson shape data loads */
    afterShapeTile: function(tile) {
        var features = [],
            tracts = [];

        //  If data failed to load, this field won't be present
        if (tile.datum) {
            features = tile.datum.features;
        }

        _.each(features, function(feature) {
            Mapusaurus.drawn[feature.properties.geoid] = true;
        });
        tracts = _.filter(features, Mapusaurus.isTract);
        //  convert to geoids
        tracts = _.map(tracts, function(feature) {
            return feature.properties.geoid;
        });
        if (tracts.length > 0) {
            Mapusaurus.updateDataWithoutGeos(tracts);
            Mapusaurus.fetchMissingStats(tracts);
        }
        
    },
    /* Set the style and interaction for each geojson shape */
    eachShapeTile: function(feature, layer) {
        //  keep expected functionality with double clicking
        layer.on('dblclick', function(ev) {
            Mapusaurus.map.setZoomAround(ev.latlng,
                                         Mapusaurus.map.getZoom() + 1);
        });
        if (Mapusaurus.isTract(feature)) {
            Mapusaurus.eachTract(feature, layer);
            layer.setStyle(Mapusaurus.minorityContinuousStyle(feature));
        }
    },
    /* As all "features" (shapes) come through a single source, we need to
     * separate them to know what style to apply */
    pickStyle: function(feature) {
      var zoomLevel = Mapusaurus.map.getZoom();
      if (Mapusaurus.isTract(feature)) {
          return Mapusaurus.minorityContinuousStyle(feature);
      //  Slightly different styles for metros at different zoom levels
      } else if (zoomLevel > 8) {
          if (Mapusaurus.isCounty(feature)) {
              return Mapusaurus.zoomedCountyStyle;
          } else if (Mapusaurus.isMetro(feature)) {
              return Mapusaurus.zoomedMetroStyle;
          }
      //  Only metros should be present at zoom levels <= 8, but this is a
      //  safety check
      } else if (Mapusaurus.isMetro(feature)) {
          return Mapusaurus.biggerMetroStyle;
      }
    },
    /* As there will be drawing order issues depending on tile order, shape
     * order, etc., we may need to re-order their z-index */
    reZIndex: function() {
        //  Put metros at the back
        Mapusaurus.layers.shapes.geojsonLayer.eachLayer(function(layer) {
          if (Mapusaurus.isMetro(layer.feature)) { layer.bringToBack(); }
        });
        //  Then put county at the back (hence metros will be on top)
        Mapusaurus.layers.shapes.geojsonLayer.eachLayer(function(layer) {
          if (Mapusaurus.isCounty(layer.feature)) { layer.bringToBack(); }
        });
        //  Finally put tracts at the back (so that tracts are behind counties
        //  are behind metros)
        Mapusaurus.layers.shapes.geojsonLayer.eachLayer(function(layer) {
          if (Mapusaurus.isTract(layer.feature)) { layer.bringToBack(); }
        });
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
    },

    /* Depending on whether or not stats have been loaded, the hover text may
     * be different */
    tractHoverText: function(geoid) {
        var tract = Mapusaurus.dataStore.tract[geoid];
        if (_.has(tract, 'layer_minority')) {
            return (
                (Mapusaurus.minorityPercent(tract['layer_minority']) *
                100).toFixed() + '% "Minority"<br />(' +
                $('#category-selector option:selected').text() + ')');
        } else {
            return 'Loading...';
        }
    },

    /*  We may have previously loaded stats data without the geos. Run through
     *  that data and see if the new geo data matches */
    updateDataWithoutGeos: function(newTracts) {
        var toDraw = {},  // geoids by layer
            undrawnData = Mapusaurus.dataWithoutGeo;
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
        _.each(_.keys(Mapusaurus.statsLoaded), function(layerName) {
            //  We only care about unseen stat data
            var missingData = _.filter(newTracts, function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid],
                    stateCounty = geo.state + geo.county;
                return !Mapusaurus.statsLoaded[layerName][stateCounty];
            });
            //  convert to state + county strings
            missingData = _.map(missingData, function(geoid) {
                var geo = Mapusaurus.dataStore.tract[geoid];
                return geo.state + geo.county;
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
            _.each(_.keys(Mapusaurus.statsLoaded), function(layerName) {
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
                        Mapusaurus.dataWithoutGeo[layerName][geoid] =
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
                    Mapusaurus.layers.shapes.geojsonLayer.setStyle(
                        Mapusaurus.pickStyle);
                    break;
                case 'loanVolume':
                    _.each(geoData, function(geo) {
                        Mapusaurus.layers.loanVolume.addLayer(
                            Mapusaurus.makeBubble(geo)
                        );
                    });
                    break;
            }
        });
        Mapusaurus.reZIndex();
    },

    //  Using the selector, determine which hmda statistic to display
    hmdaStat: function(tractData) {
        var fieldName = $('#bubble-selector').val(),
            splitAt = fieldName.indexOf('_'),
            scale = parseFloat(fieldName.substring(0, splitAt));
        return scale * tractData[fieldName.substr(splitAt + 1)];
    },

    redrawBubbles: function() {
        Mapusaurus.layers.loanVolume.eachLayer(function(layer) {
            var geoid = layer.geoid,
                tractData = Mapusaurus.dataStore.tract[geoid],
                stat = Mapusaurus.hmdaStat(tractData['layer_loanVolume']);
            layer.setRadius(stat);
        });
    },

    /* Styles/extras for originations layer */
    makeBubble: function(geoProps) {
        var data = geoProps['layer_loanVolume'],
            circle = L.circle([geoProps.centlat, geoProps.centlon],
                              Mapusaurus.hmdaStat(data),
                              Mapusaurus.bubbleStyle);
        //  We will use the geoid when redrawing
        circle.geoid = geoProps.geoid;
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
        if (!tract || !_.has(tract, 'layer_minority')) {
            return Mapusaurus.loadingStyle;
        } else if (tract['layer_minority']['total_pop'] === 0) {
            return Mapusaurus.noStyle;
        } else {
            var perc = Mapusaurus.minorityPercent(tract['layer_minority']),
                bucket = Mapusaurus.toBucket(perc),
                // convert given percentage to percents within bucket's bounds
                bucketPercent = percentFn(perc, bucket);
            return $.extend({}, Mapusaurus.tractStyle, {
                fillColor: Mapusaurus.colorFromPercent(bucketPercent,
                                                       bucket.colors)
            });
        }
    },

    //  Using the selector, determine which statistic to display.
    minorityPercent: function(tractData) {
        var fieldName = $('#category-selector').val();
        if (fieldName.substring(0, 4) === 'inv_') {
            return 1 - tractData[fieldName.substr(4)];
        } else {
            return tractData[fieldName];
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
    },

    /* Called when user selects to enforce the boundaries of an MSA. Assumes
     * an MSA is selected (lest the triggering selector would not be present)
     * */
    enforceBounds: function() {
        var selectEl = $('#enforce-bounds-selector'),
            minLat = parseFloat(selectEl.data('min-lat')),
            maxLat = parseFloat(selectEl.data('max-lat')),
            minLon = parseFloat(selectEl.data('min-lon')),
            maxLon = parseFloat(selectEl.data('max-lon'));
        //  Assumes northwest quadrisphere
        Mapusaurus.map.setMaxBounds([[minLat, minLon], [maxLat, maxLon]]);
    },
    /* Reverse of above */
    disableBounds: function() {
        Mapusaurus.map.setMaxBounds(null);
    }
};
