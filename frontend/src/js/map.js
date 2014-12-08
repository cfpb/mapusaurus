'use strict';

if (!window.console) console = {log: function() {}};

    // When the DOM is loaded, do the following:
    $(document).ready(function(){

        $('.tabs').show();

        $( window ).resize(function() {
            setMapHeight();
        });

        // When minority changes, redraw the circles with appropriate styles
        $('#category-selector').on('change', function(e) {
            var val = $('#category-selector').val();
            layerUpdate(val);  
        });

        // Check to see if we have any parameters for category-selector
        if( typeof loadParams.category != 'undefined'){
            $('#category-selector').val( loadParams.category.values );
            layerUpdate( loadParams.category.values );
        } else {
            addParam( 'category', 'inv_non_hisp_white_only_perc' );
            layerUpdate( 'inv_non_hisp_white_only_perc' );
        }

        // Check to see if we have any parameters for action-taken
        if( typeof loadParams.action != 'undefined'){
            $('#action-taken-selector').val( loadParams.action.values );
        } else {
            addParam( 'action', 'all-apps-5' );
        }

        if( typeof loadParams.lh != 'undefined'){
            var status = (loadParams.lh.values == "true");
            $('#superSelect').prop('checked', status );
            toggleSuper(status);
        } else {
            addParam('lh', false );
        }

        $('#superSelect').change( function(){
            var el = $('#superSelect');
            var status = el.prop('checked');
            toggleSuper(status);
            init();
        });

        // When the user changes the action taken data selector, re-initialize
        $('#action-taken-selector').on('change', function(){
            addParam( 'action', $('#action-taken-selector option:selected').val() );
            init();
        });

        //Let the application do its thing 
        init();
        
    });
    
    // Go get the tract centroids and supporting data, THEN build a data object (uses jQuery Deferreds)
    function init(){
        blockStuff();
        $.when( getTractsInBounds( getBoundParams() ), getTractData( getBoundParams(), getActionTaken( $('#action-taken-selector option:selected').val() ))).done( function(data1, data2){
            // Get the information about the currently selected layer so we can pass bubble styles to redraw
            var hashInfo = getHashParams(),
                layerInfo = getLayerType(hashInfo.category.values);

            // Create our two global data objects with our returned data
            rawGeo = data1[0];
            rawData = data2[0];

            // Create our Tract Data Object (Datastore.tracts) from the raw sources
            createTractDataObj(); 

            // Redraw the circles using the created tract object AND the layer bubble type
            redrawCircles(dataStore.tracts, layerInfo.type );
            
            // Unblock the user interface (remove gradient)
            $.unblockUI();
            isUIBlocked = false;
        });
    }

    // Supporting function to adjust the leaflet map to the height of the window
    function setMapHeight() {
        /* Set the map div to the height of the browser window minus the header. */
        var viewportHeight = $(window).height();
        var warningBannerHeight = $('#warning-banner').outerHeight();
        var headerHeight = $('#header').outerHeight();
        var mapHeaderHeight = $('#map-header').outerHeight();
        var mapHeight = (viewportHeight - (warningBannerHeight + headerHeight + mapHeaderHeight));
        $('#map-aside').css('height', mapHeight);
        $('#map').css('height', mapHeight);
    }

    function toggleSuper( status ){
        var url = $('#download-data').data('super-download'),
            origUrl = $('#download-data').data('download');

        if( !status ){
            $('#download-data').attr('href', origUrl);
        } else {
            $('#download-data').attr('href', url);
        }
        addParam('lh', status);
        $('#superSelect').prop('checked', status );

    }

    function blockStuff(){
        if( isUIBlocked === true ){
            return false;
        } else {
            isUIBlocked = true;
            $.blockUI(
                { css: { 
                        border: 'none', 
                        padding: '15px', 
                        backgroundColor: '#000', 
                        '-webkit-border-radius': '10px', 
                        '-moz-border-radius': '10px', 
                        opacity: .5, 
                        color: '#fff' 
                    },
                 message: '<img src="/static/basestyle/img/loading_white.gif" height="75px"> <h6>Loading HMDA Data</h6>'
                }
            );
        }
        
    }


    /* 
        ---- GET DATA SCRIPTS ----
    */    

    var rawGeo, rawLar, rawMinority, rawData, 
    isUIBlocked = false,
    dataStore = {};
    dataStore.tracts = {};
    
    function getTractsInBounds( bounds, callback ){
        //TODO: Modify parameters for this endpoint to take param hooks instead of forward slash

        $('#bubbles_loading').show();

        // Create the appropriate URL path to return values
        var endpoint = '/api/tractCentroids/', 
            params = { neLat: bounds.neLat,
                       neLon: bounds.neLon,
                       swLat: bounds.swLat,
                       swLon: bounds.swLon };
        return $.ajax({
            url: endpoint, data: params, traditional: true,
            success: console.log('tract Get successful')
        }).fail( function( status ){
            console.log( 'no data was available at' + endpoint + '. status: ' + status );
        });

        if( typeof callback === 'function' && callback() ){
            callback;
        }

    }    

    function getTractData( bounds, actionTakenVal, callback ){
        $('#bubbles_loading').show();
        var endpoint = '/api/all/',
            params = { year: 2013,
                        'lh': false,
                        'neLat': bounds.neLat,
                        'neLon': bounds.neLon,
                        'swLat': bounds.swLat,
                        'swLon': bounds.swLon };
        var hash = getHashParams();
        if( typeof hash.lh !== 'undefined' ){
            params.lh = hash.lh.values;
        }

        // Check to see if another year has been requested other than the default
        if ( urlParam('year') ){
            params.year = urlParam('year');
        }

        // Set the lender parameter based on the current URL param
        if ( urlParam('lender') ){
            params['lender'] = urlParam('lender');
        } else {
            console.log(' Lender parameter is required.');
            return false;
        }


        // If actionTaken, go get data, otherwise
        // let the user know about the default value
        if ( actionTakenVal ) {
            params['action_taken'] = actionTakenVal;
        } else {
            console.log('No action taken value - default (1-5) will be used.');
        }

        return $.ajax({
            url: endpoint, data: params, traditional: true,
            success: console.log('get API All Data request successful')
        }).fail( function( status ){
            console.log( 'no data was available at' + endpoint + '. status: ' + status );
        });;

        if( typeof callback === 'function' && callback() ){
            callback;
        }
    }

    function createTractDataObj( callback ){
        dataStore.tracts = {};

        // For each top-level data element returned (minority, loanVolume)
        _.each( rawGeo.features, function(feature, key){
            // Loop through each tract and merge the dataset (this could be done server side as well if faster)
            // Make sure the tracts object exists before writing to it.
            var geoid = feature.properties.geoid;
            dataStore.tracts[geoid] = feature.properties;
            _.extend( dataStore.tracts[geoid], rawData.minority[geoid] );

            if( typeof rawData.loanVolume[geoid] != 'undefined'){
                _.extend( dataStore.tracts[geoid], rawData.loanVolume[geoid] );
            } else {
                dataStore.tracts[geoid].volume = 0;
            }

        });

        if( typeof callback === 'function' && callback() ){
            callback;
        }
    }

  
    /*
        END GET DATA SECTION
    */

    /* 
        ---- DRAW CIRCLES ----
    */

    function redrawCircles( geoData, layerType ){
        // Show data load icon
        $('#bubbles_loading').show();     
        layers.Centroids.clearLayers();
        _.each(geoData, function(geo) {
            var bubble = drawCircle(geo, layerType);
        });
    }

    function updateCircles( layerType ){
        layers.Centroids.eachLayer( function(layer){
            
            // If layer has no LAR information, zero this out.
            if( layer.volume == 0 ){
                return false;
            }

            if( layerType == 'minority' ){
                var newStyle = {}
                _.extend(newStyle, baseStyle);
                newStyle.fillColor = updateMinorityCircleFill(layer.geoid);
                layer.setStyle( newStyle );
            } else if( layerType =='seq'){
                layer.setStyle( seqBaseStyle );
            }
        });
        console.log("color update complete.");
    }


    function drawCircle(geo, layerType){
        var data = geo,
            style;
        // If no population exists, use the "no style" style (hidden)
        if (geo['total_pop'] === 0 || geo.volume === 0 ) {
            style = noStyle;
        } else if( layerType === 'seq' ){
            style = seqBaseStyle;
        } else {
            style = minorityContinuousStyle(geo, baseStyle);
        }
        var circle = L.circle([geo.centlat, geo.centlon],
                              hmdaStat(data), style );

        //  We will use the geoid when redrawing
        circle.geoid = geo.geoid;
        circle.volume = geo.volume;
        circle.on('mouseover mousemove', function(e){
            new L.Rrose({ offset: new L.Point(0,0), closeButton: false, autoPan: false })
              .setContent(data['volume'] + ' records<br />' + data['num_households'] + ' households<br />% White: ' + data['non_hisp_white_only_perc']*100 +
                '<br /> % Hispanic: ' + data['hispanic_perc']*100 + '<br />% Black: ' + data['non_hisp_black_only_perc']*100 + 
                '<br /> % Asian: ' + data['non_hisp_asian_only_perc']*100 )
              // To complete this, you'll want to create a div with a class for 'sparkline' and data elements for each value then call
              // all sparkline render function on redraw!  Wheeeeeee!
              .setLatLng(e.latlng)
              .openOn(map);
        });
        circle.on('mouseout', function(){ 
            map.closePopup();
        });
        layers.Centroids.addLayer(circle);

    }

    /*
        END DRAW CIRCLES SECTION
    */

    /*
        ---- STYLE THE CIRCLES BASED ON MINORITY ----
    */

    var baseStyle = { fillOpacity: 0.9, weight: 0.5, className: 'lar-circle', fillColor: '#333' };
    var seqBaseStyle = { fillOpacity: 0.7, weight: 0.75, className: 'lar-circle seq-circle', fillColor: '#111111', stroke: true, color: '#333', opacity: 1 };

    //  population-less tracts
    var noStyle = {stroke: false, weight: 0, fill: false};
    
    function minorityContinuousStyle(geoProps, baseStyle) {
        return minorityStyle(
            geoProps, 
            function(minorityPercent, bucket) {
                return (minorityPercent - bucket.lowerBound) / bucket.span;
            },
            baseStyle
        );
    }

    //  Shared function for minority styling; called by the two previous fns
    function minorityStyle(geoProps, percentFn, baseStyle) {
        var geoid = geoProps.geoid,
            tract = dataStore.tracts[geoid];
        // Different styles for when the tract has zero pop, or
        // we have percentages of minorities
        if (tract['total_pop'] === 0 || tract.volume === 0 ) {
            return noStyle;
        } else {
            var perc = minorityPercent(tract),
                bucket = toBucket(perc),
                // convert given percentage to percents within bucket's bounds
                bucketPercent = percentFn(perc, bucket);
            return $.extend({}, baseStyle, {
                fillColor: colorFromPercent(bucketPercent,
                                           bucket.colors)
            });
        }
    }

    // This function returns only the fill color after a minority is changed.
    function updateMinorityCircleFill(geoid){
        var tract = dataStore.tracts[geoid];
        // Different styles for when the tract has zero pop, or
        // we have percentages of minorities
        if (tract['total_pop'] === 0 || tract.volume === 0 ){
            return noStyle;
        } else {
            var perc = minorityPercent(tract),
                bucket = toBucket(perc),
                // convert given percentage to percents within bucket's bounds
                bucketPercent = percentFn(perc, bucket);
            return colorFromPercent(bucketPercent, bucket.colors);
        }    
    }

    function percentFn(minorityPercent, bucket) {
                return (minorityPercent - bucket.lowerBound) / bucket.span;
    }

    //  Using the selector, determine which statistic to display.
    function minorityPercent(tractData) {
        var fieldName = $('#category-selector option:selected').val();
        if (fieldName.substring(0, 4) === 'inv_') {
            return 1 - tractData[fieldName.substr(4)];
        } else {
            return tractData[fieldName];
        }
    }

    var colorRanges = [
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
    ]

    function toBucket(percent) {
        var i,
            len = colorRanges.length;
        for (i = 0; i < len - 1; i++) {
            //  Next bucket is too far
            if (colorRanges[i + 1].lowerBound > percent) {
                return colorRanges[i];
            }
        } 
        return colorRanges[len - 1];  //  last color
    };

    /* Given low and high colors and a percent, figure out the RGB of said
     * percent in that scale */
    function colorFromPercent(percent, c) {
        var diffR = (c.highR - c.lowR) * percent,
            diffG = (c.highG - c.lowG) * percent,
            diffB = (c.highB - c.lowB) * percent;
        return 'rgb(' + (c.lowR + diffR).toFixed() + ', ' +
               (c.lowG + diffG).toFixed() + ', ' +
               (c.lowB + diffB).toFixed() + ')';
    }

    /*
        END STYLE SECTION
    */

    /* 
        ---- UTILITY FUNCTIONS ----

    */

    //Scales statistical data to the appropriate level
    function hmdaStat(tractData) {
        var $selected = $('#action-taken-selector option:selected'),
            fieldName = $selected.val(),
            scale = $selected.data('scale'),
            area = scale * tractData['volume'];
        //  As Pi is just a constant scalar, we can ignore it in this
        //  calculation: a = pi*r*r   or r = sqrt(a/pi)
            return Math.sqrt(area);
    }

    function getLayerType( layer ){
        var type;

        switch( layer ){
            case 'inv_non_hisp_white_only_perc':
                layer = layers.PctMinority;
                type = 'minority';
                break;
            case 'hispanic_perc':
                layer = layers.PctHispanic;
                type = 'minority';
                break;
            case 'non_hisp_black_only_perc':
                layer = layers.PctBlack;
                type = 'minority';
                break;
            case 'non_hisp_asian_only_perc':
                layer = layers.PctAsian;
                type = 'minority';
                break;
            case 'non_hisp_white_only_perc':
                layer = layers.PctNonWhite;
                type = 'minority';
                break;
            case 'sequential3':
                layer = layers.Sequential3;
                type = 'seq';
                break;
            case 'sequential10':
                layer = layers.Sequential10;
                type = 'seq';
                break;
            case 'plurality':
                layer = layers.Plurality;
                type = 'seq';
                break;
        }

        return { 'type': type, 'layer': layer };
    }

    // Helper that ensures when a new layer is selected, all others are hidden and primaries stay up front
    function layerUpdate( layer ){

        var layerEval, mbLayer, layerType, keyPath;

        // layer Type is set to minority by default
        // Type determines which style scale is used to fill circles

        if ( !layer ){
            console.log('The layer you\'ve requested does not exist.');
            return false;
        }

        for (var i = minorityLayers.length - 1; i >= 0; i--) {
            map.removeLayer(minorityLayers[i]);
        }

        //Custom Key / replacement handling because of the different scales.
        // Check which layer is being presented and replace the key appropriately
        // Then hide the minority scale if required. If we agree on these scales
        // Then we should code this as HTML like the existing key because
        // This is relatively hacky, and hard-codes the static files directory
        switch( layer ){
            case 'sequential3':
                keyPath = '/static/basestyle/img/fl_color-ramp_seq-03.png';
                break;
            case 'sequential10':
                keyPath = '/static/basestyle/img/fl_color-ramp_seq-10.png';
                break;
            case 'plurality':
                keyPath = '/static/basestyle/img/fl_color-ramp_plurality.png';                
                break;
            case 'default':
                keyPath = false;
        }

        if( keyPath ){
            $('#altScaleImg').attr('src', keyPath);
            $('#altScale').removeClass('hidden');
            $('#scale').addClass('hidden');
        } else {
            $('#altScale').addClass('hidden');
            $('#scale').removeClass('hidden');
        }

        layerEval = getLayerType( layer );
        mbLayer = layerEval.layer;
        layerType = layerEval.type;

        map.addLayer( mbLayer );
        mbLayer.bringToFront();
        layers.Water.bringToFront();
        layers.Boundaries.bringToFront();
        layers.MSALabels.bringToFront();

        if( map.hasLayer(layers.CountyLabels) ){
            layers.CountyLabels.bringToFront();
        }
        
        addParam( 'category', $('#category-selector option:selected').val() );
        updateCircles( layerType );
    }

    // Gets non-hash URL parameters
    function urlParam(field) {
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
    }

    // Parameter helper function that filters the query according to dropdown values
    function getActionTaken( value ){
        var actionTaken;

        switch (value) {
            case 'all-apps-5': 
                actionTaken = '1,2,3,4,5';
                break; 
            case 'all-apps-6': 
                actionTaken = '1,2,3,4,5,6';
                break; 
            case 'originations-1': 
                actionTaken = '1';
                break; 
        }
        return actionTaken;
    }

    // Simple function to return bounds consistently with our padding / fixed #
    function getBoundParams(){
        var bounds = map.getBounds(),
        padding = .00;
        return { neLat: (bounds._northEast.lat + padding).toFixed(6),
                neLon: (bounds._northEast.lng + padding).toFixed(6),
                swLat: (bounds._southWest.lat - padding).toFixed(6),
                swLon: (bounds._southWest.lng - padding).toFixed(6)
            }
    }

    function getUniques( arr ){
        return _.uniq( arr );
    }

    /* 
        END UTILITY FUNCTIONS
    */