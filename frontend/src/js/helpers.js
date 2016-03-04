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
        dataStore.tracts = rawData;


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
        var combinedHeadersHeight = warningBannerHeight + headerHeight + mapHeaderHeight;
        var mapHeight = viewportHeight - combinedHeadersHeight;
        $('#map-aside').css('height', mapHeight);
        $('#map-container').css('height', mapHeight);
        if (showDataContainer) {
            $('.map-container').css({'height': (mapHeight * .5) + combinedHeadersHeight, 'overflow': 'hidden'});
            $('#map').css('height', mapHeight * .5);
            $('#map-aside').css('height', mapHeight * .5);
            $('#data-container').css('height', (mapHeight * .5) - 5);
            $('body').addClass('show-data');
        } else {
            $('#map-aside').css('height', mapHeight);
            $('.map-container').css('height', 'auto');
            $('#map').css('height', mapHeight);
            $('body').removeClass('show-data');
        }
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
            $('#lender-branches').removeClass('green-highlight');
        } else {
            drawBranches();
            $('#branchKey').removeClass('hidden');
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
            $('#download-data').attr('href', origUrl);
        } else {
            $('#lender-peers-list').removeClass('hidden');
            $('.peers-of-true').removeClass('hidden');
            $('#lender-peers').addClass('green-highlight');
            $('#download-data').attr('href', url);
        }
        addParam('peers', status);
        getPeerLinks();

        // If Peer is checked, uncheck and disable Peers and branches as they will not be displayed for peer set.
        $('#branchSelect').prop('disabled', status );
        $('#superSelect').prop('disabled', status );
        toggleBranches(false);
        toggleSuper(false);

        // Check the box
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
            $('#altScaleImgLabel').text(layerEval.displayName);
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


    // Adjudicate the variables associated with selected app layers across the application (names, paths, etc)
    function getLayerType( layer ){
        var type, keyPath, displayName;

        switch( layer ){
            case 'inv_non_hisp_white_only_perc':
                layer = layers.PctMinority;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-minority.png';
                displayName = 'Percentage Minority';
                break;
            case 'hispanic_perc':
                layer = layers.PctHispanic;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-hisp.png';
                displayName = 'Percentage Hispanic';
                break;
            case 'non_hisp_black_only_perc':
                layer = layers.PctBlack;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-black.png';
                displayName = 'Percentage Black / African American';
                break;
            case 'non_hisp_asian_only_perc':
                layer = layers.PctAsian;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-asian.png';
                displayName = 'Percentage Asian';
                break;
            case 'non_hisp_white_only_perc':
                layer = layers.PctWhite;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_pct-white.png';
                displayName = 'Percentage White';                
                break;              
            case 'plurality':
                layer = layers.Plurality;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_min-plurality.png';
                displayName = 'Minority Plurality';
                break;
            case 'owner_occupancy':
                layer = layers.OwnerOccupancy;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_own-occupancy.png';
                displayName = 'Owner Occupancy Rate';                
                break;                
            case 'median_family_income':
                layer = layers.MedianIncome;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_med-fam-income.png';
                displayName = 'Median Family Income by Census Tract';                
                break;   
            case 'median_value':
                layer = layers.MedianValue;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_med-hse-val.png';
                displayName = 'Median Value of O-O Housing';                
                break;  
            case 'median_year':
                layer = layers.MedianYearBuilt;
                type = 'seq';
                keyPath = '/static/basestyle/img/key_medyr-hse-built.png';
                displayName = 'Median Year Structure Built';                
                break;                                               
            default:
                layer = layers.PctMinority;
                type = 'seq';
                keyPath = false;
                displayName = 'Percentage Minority';
                break;
        }

        return { 'type': type, 'layer': layer, 'keyPath': keyPath, 'displayName': displayName };

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
            var href = '/map/?metro=' + urlParam('metro') + '&lender=' + instid + '&year=' + selectedYear + window.location.hash.replace('&peers=true', '');            
            $(val).attr('href', href);
        });
    }

    // Update the #censusLink href to reflect the selections of the user
    function updateCensusLink(){
        var actions = getHashParams()
        var actionVar = getActionTaken( actions.action.values );
        $('#downloadCensus').attr('href', '/census/race_summary_csv/?metro=' + urlParam('metro') + '&lender=' + urlParam('lender') + '&action_taken=' + actionVar  + '&year=' + selectedYear );
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

    function generateTooltips(selector, offset){
        // Generate the tool-tip listener for anything with that class - one can only do this once for 
        // the entire app and then must do so again for any new tooltipsy elements or else the duplicates
        // will cause UI anomalies
        if(!offset){
            offset = [1,0]; // Default 1px to the right
        }

        if( selector ){
            $(selector + ' .tooltipsy').tooltipsy({
                className: 'bubbletooltip_tip',
                offset: offset,
                show: function (e, $el) {
                    $el.fadeIn(100);
                },
                hide: function (e, $el) {
                    $el.fadeOut(450);
                }
            });            
        } else {
            $('.tooltipsy').tooltipsy({
                className: 'bubbletooltip_tip',
                offset: offset,
                show: function (e, $el) {
                    $el.fadeIn(100);
                },
                hide: function (e, $el) {
                    $el.fadeOut(450);
                }
            });
        }
        
    }
    /* 
        END UTILITY FUNCTIONS
    */
