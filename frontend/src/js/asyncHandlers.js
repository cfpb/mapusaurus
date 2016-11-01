
    /* 
        ---- GET DATA SCRIPTS ----
    */    

    var rawGeo, rawLar, rawMinority, rawData, 
    selectedYear = selectedYear || 2015,
    isUIBlocked = false,
    larVolume = [],
    pctMinority = [],
    dataStore = {};
    dataStore.tracts = {};
    
    // Get the census tracts that are in bounds for the current map view. Return a promise.
    function getTractsInBounds(bounds, geoType){

        $('#bubbles_loading').show();

        // Create the appropriate URL path to return values
        var endpoint = '/api/tractCentroids/', 
            params = { year: selectedYear };

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
            // Unblock the user interface (remove gradient)
            $.unblockUI();
            isUIBlocked = false;
        });

    }    

    // Get minority and LAR data for census Tracts within the bounding box, for a specific criteria (actionTaken)
    // Return a promise.
    function getTractData( actionTakenVal, bounds, geoType ){
        $('#bubbles_loading').show();
        var endpoint = '/api/hmda/',
            params = { year: selectedYear,
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
            // Unblock the user interface (remove gradient)
            $.unblockUI();
            isUIBlocked = false;
        });

    }


    // Get the Metro Areas currently shown on the map (used to check if we need to load new data on move)
    function getMsasInBounds(){
        var endpoint = '/api/msas/', 
            params = { year: selectedYear },
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
            // Unblock the user interface (remove gradient)
            $.unblockUI();
            isUIBlocked = false;
        });
    }


    // Gets Branch Locations in bounds when a user selects "Branch Locations"
    // Returns a promise
    function getBranchesInBounds( bounds ){

        // Create the appropriate URL path to return values
        var endpoint = '/api/branchLocations/', 
            params = { year: selectedYear,
                       neLat: bounds.neLat,
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

    /*
        END GET DATA SECTION
    */
