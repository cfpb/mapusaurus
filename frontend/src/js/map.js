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

        if( typeof loadParams.lh !== 'undefined'){
            var status = (loadParams.lh.values == "true");
            console.log('load params status: ', status);
            $('#superSelect').prop('checked', status );
            toggleSuper(status);
        }

        $('#superSelect').change( function(){
            var el = $('#superSelect');
            var status = el.prop('checked');
            addParam('lh', status );
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
        $.when( getTractsInBounds( getBoundParams() ), getTractData( getBoundParams(), getActionTaken( $('#action-taken-selector option:selected').val() ))).done( function(data1, data2){
            rawGeo = data1[0];
            rawData = data2[0];
            createTractDataObj(); 
            redrawCircles(dataStore.tracts);
            $('#bubbles_loading').hide();
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
    }

    /* 
        ---- GET DATA SCRIPTS ----
    */    

    var rawGeo, rawLar, rawMinority, rawData,
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
                        'lh': $('#superSelect').prop('checked'),
                        'neLat': bounds.neLat,
                        'neLon': bounds.neLon,
                        'swLat': bounds.swLat,
                        'swLon': bounds.swLon };

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

    function redrawCircles( geoData ){
        // Remove circles currently on the page (TODO: Add as LayerGroup and transition)
        $('#bubbles_loading').show();
        layers.Centroids.clearLayers();
        _.each(geoData, function(geo) {
            var bubble = drawCircle(geo);
        });
    }

    function updateCircles(){
        //TODO: Figure out best way to update colors of existing, not redraw to reduce lag
        layers.Centroids.eachLayer( function(layer){
            layer.setStyle({fillColor: updateMinorityCircleFill(layer.geoid) });
        });
        console.log("color update complete.");
    }


    function drawCircle(geo){
        var data = geo,
            style = minorityContinuousStyle(
               geo, baseStyle),
            circle = L.circle([geo.centlat, geo.centlon],
                              hmdaStat(data), style );
        //  We will use the geoid when redrawing
        circle.geoid = geo.geoid;
        circle.on('mouseover mousemove', function(e){
            new L.Rrose({ offset: new L.Point(0,0), closeButton: false, autoPan: false })
              .setContent(data['volume'] + ' records<br />' + data['num_households'] + ' households')
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

    // Helper that ensures when a new layer is selected, all others are hidden and primaries stay up front
    function layerUpdate( layer ){
        if ( !layer ){
            console.log('The layer you\'ve requested does not exist.');
        }
        for (var i = minorityLayers.length - 1; i >= 0; i--) {
            map.removeLayer(minorityLayers[i]);
        };
        switch( layer ){
            case 'inv_non_hisp_white_only_perc':
                layer = layers.PctMinority;
                break;
            case 'hispanic_perc':
                layer = layers.PctHispanic;
                break;
            case 'non_hisp_black_only_perc':
                layer = layers.PctBlack;
                break;
            case 'non_hisp_asian_only_perc':
                layer = layers.PctAsian;
                break;
            case 'non_hisp_white_only_perc':
                layer = layers.PctNonWhite;
                break;
        }
        map.addLayer( layer );
        layers.Water.bringToFront();
        layers.Boundaries.bringToFront();
        layers.CountyLabels.bringToFront();
        addParam( 'category', $('#category-selector option:selected').val() );
        updateCircles();
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
        console.log(bounds);
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