    /*
        ---- ASYNC HELPERS / DRAWERS ----
    */

    function drawBranches(){
        $.when( getBranchesInBounds( getBoundParams() ) ).then( function(branches){
            $.each( branches.features, function( i, val){
                drawMarker(val.properties);
            });
        });
    }

    // Creates the dataStore.tracts object global for use by application (depends upon rawGeo / rawData)
    function createTractDataObj( callback ){
        var count = 0;
        dataStore.tracts = {};

        // For each top-level data element returned (minority, loanVolume)
        _.each( rawGeo.features, function(feature, key){
            // Loop through each tract and merge the dataset (this could be done server side as well if faster)
            // Make sure the tracts object exists before writing to it.
            var geoid = feature.properties.geoid;
            dataStore.tracts[geoid] = feature.properties;
            _.extend( dataStore.tracts[geoid], rawData.minority[geoid] );

            if( typeof rawData.loanVolume[geoid] !== 'undefined'){
                _.extend( dataStore.tracts[geoid], rawData.loanVolume[geoid] );
            } else {
                dataStore.tracts[geoid].volume = 0;
            }
            count++;
        });

        if( typeof callback === 'function' && callback() ){
            callback();
        }
    }

    /* 
        ---- UTILITY FUNCTIONS ----

    */

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

    // Helper function that takes care of all the DOM interactions when "Lender Hierarchy" is checked
    function toggleSuper( status ){
        var url = $('#download-data').data('super-download'),
            origUrl = $('#download-data').data('download');

        if( !status ){
            $('#lender-affiliate-list').addClass('hidden');
            $('#lender-affiliates').removeClass('green-highlight');
            $('#download-data').attr('href', origUrl);
        } else {
            $('#lender-affiliate-list').removeClass('hidden');
            $('#lender-affiliates').addClass('green-highlight');
            $('#download-data').attr('href', url);
            if( $('#branchSelect').prop('checked') ){
                $('.tooltipsy.branch-component').addClass('red-highlight');                
            } else {
                $('.tooltipsy.branch-component').removeClass('red-highlight');    
            }
        }
        addParam('lh', status);
        $('#superSelect').prop('checked', status );

    }

    // Helper function that takes care of all the DOM interactions when "Branches" is checked
    function toggleBranches( status ){

        if( !status ){
            layers.Branches.clearLayers();
            $('#branchKey').addClass('hidden');
            $('.tooltipsy.branch-component').addClass('hidden');
            $('#lender-branches').removeClass('green-highlight');
        } else {
            drawBranches();
            $('#branchKey').removeClass('hidden');
            $('.tooltipsy.branch-component').removeClass('hidden');
            $('#lender-branches').addClass('green-highlight');
        }

        addParam('branches', status);
        $('#branchSelect').prop('checked', status );

    }   

    function togglePeers( status ){
        var url = $('#download-data').data('peer-download'),
            origUrl = $('#download-data').data('download');

        if( !status ){
            $('#lender-peers-list').addClass('hidden');
            $('#lender-peers').removeClass('green-highlight');
            $('.tooltipsy.peer-component').addClass('hidden');
            $('#download-data').attr('href', origUrl);
        } else {
            $('#lender-peers-list').removeClass('hidden');
            $('#lender-peers').addClass('green-highlight');
            $('.tooltipsy.peer-component').removeClass('hidden');
            $('#download-data').attr('href', url);
        }
        addParam('peers', status);
        $('#peerSelect').prop('checked', status );

    }     

    // Uses jQuery BlockUI plugin to block UI on data loading
    function blockStuff(){
        if( isUIBlocked === true ){
            return false;
        } else {
            isUIBlocked = true;
            $.blockUI(
                {   css: { 
                        border: 'none', 
                        padding: '15px', 
                        backgroundColor: '#000', 
                        '-webkit-border-radius': '10px', 
                        '-moz-border-radius': '10px', 
                        opacity: 0.5, 
                        color: '#fff' 
                    },
                    message: '<img src="/static/basestyle/img/loading_white.gif" height="75px"> <h6>Loading HMDA Data</h6>',
                    overlayCSS:  { 
                        backgroundColor: '#000', 
                        opacity:         0.0, 
                        cursor:          'wait' 
                    }
                }
            );
        }
        
    }

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
            console.log('The layer you\'ve requested does not exist: ', layer);
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
        
        addParam( 'category', layer );
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

    // Update the #printLink href to reflect the current map when "print" is clicked
    function updatePrintLink(){
        $('#printLink').attr('href', '/map/print' + window.location.search + window.location.hash );
    }

    // Update the #censusLink href to reflect the selections of the user
    function updateCensusLink(){
        var actions = getHashParams()
        var actionVar = getActionTaken( actions.action.values );
        $('#downloadCensus').attr('href', '/census/race_summary_csv/?metro=' + urlParam('metro') + '&lender=' + urlParam('lender') + '&action_taken=' + actionVar );
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
        padding = 0;
        return { neLat: (bounds._northEast.lat + padding).toFixed(6),
                neLon: (bounds._northEast.lng + padding).toFixed(6),
                swLat: (bounds._southWest.lat - padding).toFixed(6),
                swLon: (bounds._southWest.lng - padding).toFixed(6)
            };
    }

    function getUniques( arr ){
        return _.uniq( arr );
    }

    // Write the new value of the active layer category and DOM selector ID
    function assignCat( catVal ){
        cat = catVal.toString();
        catId = '#' + cat;
    }
    /* 
        END UTILITY FUNCTIONS
    */