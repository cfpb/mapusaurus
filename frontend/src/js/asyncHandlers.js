
    /* 
        ---- GET DATA SCRIPTS ----
    */    

    var rawGeo, rawLar, rawMinority, rawData, 
    isUIBlocked = false,
    dataStore = {};
    dataStore.tracts = {};
    
    // Get the census tracts that are in bounds for the current map view. Return a promise.
    function getTractsInBounds(bounds, geoType){

        $('#bubbles_loading').show();

        // Create the appropriate URL path to return values
        var endpoint = '/api/tractCentroids/', 
            params = {};

        if( bounds && typeof bounds === 'object' ){
            params.neLat = bounds.neLat;
            params.neLon = bounds.neLon;
            params.swLat = bounds.swLat;
            params.swLon = bounds.swLon;
        }

        if( geoType ){
            params.geoType = geoType;
        }

        if ( urlParam('metro') ){
            params.metro = urlParam('metro');
        } else {
            console.log("No metro area provided");
        }

        // Set the lender parameter based on the current URL param
        if ( urlParam('lender') ){
            params['lender'] = urlParam('lender');
        } else {
            console.log(' Lender parameter is required.');
            return false;
        }

        return $.ajax({
            url: endpoint, data: params, traditional: true,
            success: console.log('tract Get successful')
        }).fail( function( status ){
            console.log( 'no data was available at' + endpoint + '. status: ' + status );
        });

    }    

    // Get minority and LAR data for census Tracts within the bounding box, for a specific criteria (actionTaken)
    // Return a promise.
    function getTractData( actionTakenVal, bounds, geoType ){
        $('#bubbles_loading').show();
        var endpoint = '/api/all/',
            params = { year: 2013,
                        'lh': false,
                        'peers': false,
                        'geo_type': geoType };

        if( bounds && typeof bounds === 'object'){
            params.neLat = bounds.neLat;
            params.neLon = bounds.neLon;
            params.swLat = bounds.swLat;
            params.swLon = bounds.swLon;
        }

        if( geoType ){
            params.geoType = geoType;
        }

        var hash = getHashParams();

        // Check to see if Lender Hierarchy (lh) exists.
        if( typeof hash.lh !== 'undefined' ){
            params.lh = hash.lh.values;
        }

        if( typeof hash.peers !== 'undefined') {
            params.peers = hash.peers.values;
        }

        // Check to see if another year has been requested other than the default
        if ( urlParam('year') ){
            params.year = urlParam('year');
        }

        if ( urlParam('metro') ){
            params.metro = urlParam('metro');
        } else {
            console.log("No metro area provided");
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

    // Get the Metro Areas currently shown on the map (used to check if we need to load new data on move)
    function getMsasInBounds(){
        var endpoint = '/api/msas', 
            params = {},
            bounds = getBoundParams();

        params.neLat = bounds.neLat;
        params.neLon = bounds.neLon;
        params.swLat = bounds.swLat;
        params.swLon = bounds.swLon;

        return $.ajax({
            url: endpoint, data: params, traditional: true,
            success: function(data){
                // console.log("MSA Data for bounds successfully obtained: ", data);
            }
        }).fail( function( status ){
            console.log( 'no MSA data was available at' + endpoint + '. status: ' + status );
        });
    }


    // Gets Branch Locations in bounds when a user selects "Branch Locations"
    // Returns a promise
    function getBranchesInBounds( bounds ){

        // Create the appropriate URL path to return values
        var endpoint = '/api/branchLocations/', 
            params = { neLat: bounds.neLat,
                       neLon: bounds.neLon,
                       swLat: bounds.swLat,
                       swLon: bounds.swLon };

        // Add the lender param, if it exists, otherwise error out.
        if ( urlParam('lender') ){
            params['lender'] = urlParam('lender');
        } else {
            console.log(' Lender parameter is required.');
            return false;
        }

        return $.ajax({
            url: endpoint, data: params, traditional: true,
            success: console.log('Branch Location Get successful')
        }).fail( function( status ){
            console.log( 'no data was available at' + endpoint + '. status: ' + status );
        });

    } 

    function drawBranches(){
        $.when( getBranchesInBounds( getBoundParams() ) ).then( function(branches){
            $.each( branches.features, function( i, val){
                drawMarker(val.properties);
            });
        });
    }

    /*
        END GET DATA SECTION
    */