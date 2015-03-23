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
            
            pctMinority.push(1.0 - rawData.minority[geoid]['non_hisp_white_only_perc']);
            var loanVolume = rawData.loanVolume[geoid];

            if (_.isUndefined(loanVolume)) {
              larVolume.push(0);
            } else {
              larVolume.push((loanVolume['volume'] / loanVolume['num_households']) * 1000);
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
            $('.peers-of-true').addClass('hidden');
            $('.tooltipsy.peer-component').addClass('hidden');
            $('#download-data').attr('href', origUrl);
        } else {
            $('#lender-peers-list').removeClass('hidden');
            $('.peers-of-true').removeClass('hidden');
            $('#lender-peers').addClass('green-highlight');
            $('.tooltipsy.peer-component').removeClass('hidden');
            $('#download-data').attr('href', url);
        }
        addParam('peers', status);
        getPeerLinks();
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

        layerEval = getLayerType( layer );
        mbLayer = layerEval.layer;
        layerType = layerEval.type;
        keyPath = layerEval.keyPath;

        if( keyPath ){
            $('#altScaleImg').attr('src', keyPath);
            $('#altScale').removeClass('hidden');
            $('#scale').addClass('hidden');
        } else {
            $('#altScale').addClass('hidden');
            $('#scale').removeClass('hidden');
        }

        map.addLayer( mbLayer );
        mbLayer.bringToFront();
        layers.Water.bringToFront();
        layers.Boundaries.bringToFront();
        layers.CountyLabels.bringToFront();

        if( map.hasLayer(layers.MSALabels) ){
            layers.MSALabels.bringToFront();
        }
        
        addParam( 'category', layer );

        // NOTE: layerType is an artifact from when we used multiple keys for a single
        // layer type called "Minority" that used a scaled circle draw. I've kept the function
        // in the code in case we want to assign keys or other attributes based on a layer group
        // or layer type.
    }

    function getLayerType( layer ){
        var type, keyPath;

        switch( layer ){
            case 'inv_non_hisp_white_only_perc':
                layer = layers.PctMinority;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-minority.png';
                break;
            case 'hispanic_perc':
                layer = layers.PctHispanic;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-hisp.png';
                break;
            case 'non_hisp_black_only_perc':
                layer = layers.PctBlack;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-black.png';
                break;
            case 'non_hisp_asian_only_perc':
                layer = layers.PctAsian;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-asian.png';
                break;
            case 'non_hisp_white_only_perc':
                layer = layers.PctNonWhite;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-white.png';
                break;              
            case 'plurality':
                layer = layers.Plurality;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_min-plurality.png';
                break;
            default:
                layer = layers.PctMinority;
                type = 'seq';
                keyPath = false;
                break;
        }

        return { 'type': type, 'layer': layer, 'keyPath': keyPath };

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

    function getPeerLinks(){
        var peerList = $('.peer-link');
        $.each(peerList, function(i, val){
            var instid = $(val).data('instid');
            var href = '/map/?metro=' + urlParam('metro') + '&lender=' + instid + window.location.hash.replace('&peers=true', '');            
            $(val).attr('href', href);
        });
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