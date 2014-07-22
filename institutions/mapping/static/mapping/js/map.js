'use strict';

vex.defaultOptions.className = 'vex-theme-plain';

/* The GeoJSON tile layer is excellent, but makes assumptions that we don't
 * want (like refreshing whenever zooming, and that a single logic layer is
 * encoded in the ajaxed data). We instead extend a simpler primitive, and
 * insert hooks where needed. */
L.TileLayer.GeoJSONData = L.TileLayer.Ajax.extend({
    addTileData: function (features, tilePoint) {
        if (this.options.filter) {
            features = _.filter(features, this.options.filter);
        }
        if (this.options.perGeo) {
            _.each(features, this.options.perGeo);
        }
        if (this.options.postTileLoaded) {
            this.options.postTileLoaded(features, tilePoint);
        }
    },
    _tileLoaded: function (tile, tilePoint) {
        L.TileLayer.Ajax.prototype._tileLoaded.apply(this, arguments);
        if (tile.datum !== null && tile.datum.features !== null) {
            this.addTileData(tile.datum.features, tilePoint);
        }
    }
});


var Mapusaurus = {
    //  Leaflet map
    map: null,
    //  The map can be locked to a specific metro area
    lockState: {
        locked: false,
        geoid: null,
        //  Bubbles outside the locked region may need to be added/removed on
        //  the fly. Keep a reference to them
        outsideBubbles: []
    },
    //  Leaflet layers
    layers: {tract: null, county: null, metro: null},
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
    bubbleStyle: {stroke: false, fillOpacity: 0.9, weight: 2},
    //  fillColor and color will be assigned when rendering
    tractStyle: {stroke: false, fillOpacity: 0.4, weight: 2, fill: true,
                 smoothFactor: 0.1},
    //  used when loading census tracts
    loadingStyle: {stroke: true, weight: 2, color: '#babbbd', fill: false,
                   smoothFactor: 0.1},
    //  used when displayed outside metro area
    outsideStyle: {stroke: false, fill: false},
    //  population-less tracts
    noStyle: {stroke: false, fill: false},
    //  used when census tracts are visible
    zoomedCountyStyle: {stroke: true, color: '#fff', weight: 0.5, fill: false,
                        opacity: 1.0},
    zoomedMetroStyle: {stroke: true, color: '#fff', weight: 2, fill: false,
                       opacity: 1.0},
    //  used when census tracts are not visible
    biggerMetroStyle: {stroke: true, color: '#646464', weight: 4, fill: true,
                       opacity: 1.0, dashArray: '20,10', fillColor: '#646464',
                       fillOpacity: 0.5},

    initialize: function (map) {
        var mainEl = $('main'),
            centLat = parseFloat(mainEl.data('cent-lat')) || 41.88,
            centLon = parseFloat(mainEl.data('cent-lon')) || -87.63,
            $enforceBoundsEl = $('#enforce-bounds');
        map.setView([centLat, centLon], 12);
        Mapusaurus.map = map;
        Mapusaurus.addKey(map);
        //  We don't need to hold on to this layer as it is feeding others
        new L.TileLayer.GeoJSONData('/shapes/tiles/{z}/{x}/{y}', {
            //  don't redraw shapes
            filter: Mapusaurus.notDrawn,
            perGeo: Mapusaurus.handleGeo,
            postTileLoaded: Mapusaurus.afterShapeTile

        }).addTo(map);
        Mapusaurus.layers.tract = new L.GeoJSON(null, {
            style: Mapusaurus.minorityContinuousStyle,
            onEachFeature: Mapusaurus.eachTract});
        Mapusaurus.layers.tract.addTo(map);
        Mapusaurus.layers.county = new L.GeoJSON(null, {
            style: Mapusaurus.zoomedCountyStyle,
            onEachFeature: Mapusaurus.dblclickToZoom});
        Mapusaurus.layers.county.addTo(map);
        Mapusaurus.layers.metro = new L.GeoJSON(null, {
            style: Mapusaurus.zoomedMetroStyle,
            onEachFeature: Mapusaurus.dblclickToZoom});
        Mapusaurus.layers.metro.addTo(map);

        if (Mapusaurus.urlParam('lender')) {
            Mapusaurus.layers.loanVolume = L.layerGroup([]);
            Mapusaurus.layers.loanVolume.addTo(map);
            Mapusaurus.dataWithoutGeo.loanVolume = {};
            Mapusaurus.statsLoaded.loanVolume = {};
            $('#bubble-selector').removeClass('hidden').on('change',
                Mapusaurus.redrawBubbles);
        }
        //  Selector to change bucket/continuous shading
        $('#style-selector').on('change', function() {
            Mapusaurus.layers.tract.setStyle(
                Mapusaurus[$('#style-selector').val()]);
        });
        $('#category-selector').on('change', function() {
            Mapusaurus.layers.tract.setStyle(Mapusaurus.pickStyle);
        });

        $enforceBoundsEl.on('change', function() {
            if ($enforceBoundsEl[0].checked) {
                $enforceBoundsEl.prev().addClass('locked');
                Mapusaurus.enforceBounds();
            } else {
                $enforceBoundsEl.prev().removeClass('locked');
                Mapusaurus.disableBounds();
            }
        });
        if ($enforceBoundsEl.length > 0) {
            Mapusaurus.lockState.geoid = mainEl.data('geoid').toString();
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
    afterShapeTile: function(features) {
        var tracts = _.filter(features, Mapusaurus.isTract);
        //  convert to geoids
        tracts = _.map(tracts, function(feature) {
            return feature.properties.geoid;
        });
        if (tracts.length > 0) {
            Mapusaurus.updateDataWithoutGeos(tracts);
            Mapusaurus.fetchMissingStats(tracts);
        }
        
    },
    /* Keep expected functionality with double clicking */
    dblclickToZoom: function(feature, layer) {
        layer.on('dblclick', function(ev) {
            Mapusaurus.map.setZoomAround(ev.latlng,
                                         Mapusaurus.map.getZoom() + 1);
        });
    },
    /* As all "features" (shapes) come through a single source, we need to
     * separate them to know what style to apply */
    pickStyle: function(feature) {
        var zoomLevel = Mapusaurus.map.getZoom(),
            //  increase the width of boundaries as we zoom in -- to a cap
            zoomForWeight = Math.min(5, zoomLevel - 9),
            //  this will be calculated differently for different shapes
            weightAtThisZoom;
        if (Mapusaurus.isTract(feature) && Mapusaurus.lockState.locked &&
            feature.properties.cbsa !== Mapusaurus.lockState.geoid) {
            return Mapusaurus.outsideStyle;
        } else if (Mapusaurus.isTract(feature)) {
            return Mapusaurus.minorityContinuousStyle(
                feature.properties, Mapusaurus.tractStyle);
        //  Slightly different styles for metros at different zoom levels
        } else if (zoomLevel > 8) {
            if (Mapusaurus.isCounty(feature)) {
                weightAtThisZoom = Mapusaurus.zoomedCountyStyle.weight +
                                   zoomForWeight * 0.5;
                return $.extend({}, Mapusaurus.zoomedCountyStyle,
                                {weight: weightAtThisZoom});
            } else if (Mapusaurus.isMetro(feature)) {
                weightAtThisZoom = Mapusaurus.zoomedMetroStyle.weight +
                                   zoomForWeight * 1;
                return $.extend({}, Mapusaurus.zoomedMetroStyle,
                                {weight: weightAtThisZoom});
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
        Mapusaurus.layers.metro.bringToBack();
        //  Then put county at the back (hence metros will be on top)
        Mapusaurus.layers.county.bringToBack();
        //  Finally put tracts at the back (so that tracts are behind counties
        //  are behind metros)
        Mapusaurus.layers.tract.bringToBack();
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
        Mapusaurus.dblclickToZoom(feature, layer);
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
                    Mapusaurus.layers.tract.setStyle(Mapusaurus.pickStyle);
                    break;
                case 'loanVolume':
                    _.each(geoData, function(geo) {
                        var bubble = Mapusaurus.makeBubble(geo);
                        if (geo.cbsa !== Mapusaurus.lockState.geoid) {
                            Mapusaurus.lockState.outsideBubbles.push(bubble);
                        }
                        if (!Mapusaurus.lockState.locked ||
                            geo.cbsa === Mapusaurus.lockState.geoid) {
                            Mapusaurus.layers.loanVolume.addLayer(bubble);
                        }
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

    /* Makes sure that all bubbles are shown/hidden as needed and have the
     * correct radius. Called after major configuration switches */
    redrawBubbles: function() {
        if (Mapusaurus.lockState.locked) {
            _.each(Mapusaurus.lockState.outsideBubbles, function(bubble) {
                Mapusaurus.layers.loanVolume.removeLayer(bubble);
            });
        } else {
            _.each(Mapusaurus.lockState.outsideBubbles, function(bubble) {
                Mapusaurus.layers.loanVolume.addLayer(bubble);
            });
        }
        
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
            style = Mapusaurus.minorityContinuousStyle(
                geoProps, Mapusaurus.bubbleStyle),
            circle = L.circle([geoProps.centlat, geoProps.centlon],
                              Mapusaurus.hmdaStat(data), style);
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
    minorityContinuousStyle: function(geoProps, baseStyle) {
        return Mapusaurus.minorityStyle(
            geoProps, 
            function(minorityPercent, bucket) {
                return (minorityPercent - bucket.lowerBound) / bucket.span;
            },
            baseStyle
        );
    },
    //  Determines colors via distinct buckets
    minorityBucketedStyle: function(geoProps, baseStyle) {
        return Mapusaurus.minorityStyle(geoProps, function() { return 0.5; },
                                        baseStyle);
    },
    //  Shared function for minority styling; called by the two previous fns
    minorityStyle: function(geoProps, percentFn, baseStyle) {
        var geoid = geoProps.geoid,
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
            return $.extend({}, baseStyle, {
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
                lowR: 107,
                lowG: 40,
                lowB: 10,
                highR: 250,
                highG: 186,
                highB: 106
            }
        },
        {
            span: 0.5,
            lowerBound: 0.5,
            colors: {
                lowR: 124,
                lowG: 198,
                lowB: 186,
                highR: 12,
                highG: 48,
                highB: 97
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
        var enforceEl = $('#enforce-bounds'),
            minLat = parseFloat(enforceEl.data('min-lat')),
            maxLat = parseFloat(enforceEl.data('max-lat')),
            minLon = parseFloat(enforceEl.data('min-lon')),
            maxLon = parseFloat(enforceEl.data('max-lon'));
        //  Assumes northwest quadrisphere
        Mapusaurus.map.setMaxBounds([[minLat, minLon], [maxLat, maxLon]]);
        Mapusaurus.lockState.locked = true;
        Mapusaurus.layers.tract.setStyle(Mapusaurus.pickStyle);
        Mapusaurus.redrawBubbles();
    },
    /* Reverse of above */
    disableBounds: function() {
        Mapusaurus.map.setMaxBounds(null);
        Mapusaurus.lockState.locked = false;
        Mapusaurus.layers.tract.setStyle(Mapusaurus.pickStyle);
        Mapusaurus.redrawBubbles();
    },
    /* Separate the stream of geos coming from the ajax layer; add the shapes
     * to their appropriate layer */
    handleGeo: function(geo) {
        Mapusaurus.drawn[geo.properties.geoid] = true;
        if (Mapusaurus.isTract(geo)) {
            Mapusaurus.layers.tract.addData(geo);
        } else if (Mapusaurus.isCounty(geo)) {
            Mapusaurus.layers.county.addData(geo);
        } else if (Mapusaurus.isMetro(geo)) {
            Mapusaurus.layers.metro.addData(geo);
        }
    },

    /* Uses canvg to draw the svg map onto a canvas, which can then be opened
     * in a separate window. Some offset addition is requires to make sure we
     * are grabbing the right viewport */
    takeScreenshot: function() {
        var offscreen = document.createElement('canvas'),
            ctx = offscreen.getContext('2d'),
            svgEl = $('svg')[0],
            $map = $('#map'),
            $tiles = $(Mapusaurus.map.getPanes().tilePane).find('img'),
            offset = Mapusaurus.map.containerPointToLayerPoint([0, 0]),
            serializer = new XMLSerializer(),
            allImages = [],
            keyImage = $('#key-image'),
            keyXOffset = $map.width() - keyImage[0].width - 10;
        offscreen.width = $map.width();
        offscreen.height = $map.height();
        offset.x = svgEl.viewBox.baseVal.x - offset.x;
        offset.y = svgEl.viewBox.baseVal.y - offset.y;
        /* Some gymnastics are needed to get around crossOrigin tainting.
         * Leaflet does not load images with the crossOrigin attribute, so we
         * load each image and draw them to the offscreen canvas. Used
         * deferred so we can wait for all the images to load. Note that this
         * technique does not work in IE 8/9, but we check this via the
         * XDomainRequest guard. Todo: try to implement it via ajax */
        if (window.XDomainRequest === undefined) {
            allImages = $tiles.map(function(idx, tile) {
                var img = new Image(),
                    deferred = $.Deferred();
                img.setAttribute('crossOrigin', 'anonymous');
                img.onload = function () {
                    deferred.resolve({tile: tile, img: img});
                };
                img.src = tile.src;
                return deferred.promise();
            });
        }
        /* Finally, draw all the tiles, then the SVG, then the key */
        $.when.apply(null, allImages).then(function() {
            var $ssPlaceholder = $('#screenshot-placeholder'),
                replacementText = 'Right-click and select Save Image As...';
            //  draw each tile
            _.each(arguments, function(tileXImg) {
                var pos = $(tileXImg.tile).position();
                ctx.drawImage(tileXImg.img, pos.left, pos.top);
            });
            //  svg
            canvg(offscreen, serializer.serializeToString(svgEl), {
                  ignoreDimensions: true, offsetY: offset.y,
                  offsetX: offset.x, ignoreClear: true});
            //  key
            ctx.drawImage(keyImage[0], keyXOffset, 10);
            ctx.fillText($('#category-selector option:selected').text(),
                         keyXOffset + 20, 100);
            ctx.fillText($('#bubble-selector:visible option:selected').text(),
                         keyXOffset + 20, 120);

            //  Closed the popup before we could edit it
            if ($ssPlaceholder.length === 0) {
                vex.dialog.alert({
                    message: ('<h2>Export Map</h2>' +
                              '<p>' + replacementText + '</p>' + 
                              '<img width="400" height="150" src="' +
                              offscreen.toDataURL() + '" />')
                });
            //  Did not close popup; edit it in place
            } else {
                $ssPlaceholder.text(replacementText);
                $('<img width="400" height="150" />').attr(
                    'src',
                    offscreen.toDataURL()).appendTo($ssPlaceholder.parent());
            }
        });
    }
};

$(document).ready(function() {
    var downloadData = $('#download-data');
    downloadData.click(function(ev) {
        ev.preventDefault();
        vex.dialog.confirm({
            message: ('<h2>Export Data</h2>' +
                      '<p>You are being redirected to the public HMDA ' +
                      'Explorer tools on www.consumerfinance.gov</p>' +
                      '<p>From there, you can preview and download the ' +
                      'HMDA LAR set for this MSA.</p>'),
            callback: function(redirect) {
                if (redirect) {
                    window.open(downloadData.attr('href'));
                }
            }
        });
    });
    $('#take-screenshot').click(function(ev) {
        ev.preventDefault();
        vex.dialog.alert({
            message: ('<h2>Export Map</h2>' +
                      '<p id="screenshot-placeholder">Loading map...</p>')
        });
        Mapusaurus.takeScreenshot();
    });
});
