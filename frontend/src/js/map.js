'use strict';

if (!window.console) console = {log: function() {}};


    var cat, catId,
        geoQueryType = 'selected';

    // When the DOM is loaded, check for hash params and add event listeners

    // globals for table.js
    var showDataContainer; 
    var destroyLarChart;
    
    var geoQueryType = 'selected';

    // When the DOM is loaded, check for params and add listeners:
    $(document).ready(function(){
        var lhStatus, peerStatus, branchStatus;

        // Invoke our tabs JavaScript
        $('.tabs').show();

        // On window resize, set the map height anew
        $( window ).resize(function() {
            setMapHeight();
        });

        // Check to see if we have any parameters for action-taken
        if( typeof loadParams.action !== 'undefined'){
            $('#action-taken-selector').val( loadParams.action.values );
        } else {
            addParam( 'action', 'all-apps-5' );
        }

        // Check to see if we have any parameters for Lender Hierarchy
        if( typeof loadParams.lh !== 'undefined'){
            lhStatus = (loadParams.lh.values === 'true');
            $('#superSelect').prop('checked', lhStatus );
            $('#peerSelect').prop('disabled', lhStatus);
            toggleSuper(lhStatus);
        } else {
            addParam('lh', false );
        }

        // On LH selection, change the params, and use toggle Helper
        $('#superSelect').change( function(){
            var el = $('#superSelect');
            var status = el.prop('checked');
            toggleSuper(status);
            $('#peerSelect').prop('disabled', status);
            initCalls(geoQueryType);
        });

        // Set a global variable that determines which data will be pulled through on "init" function
        // Bounds should be passed for MSA and All, but not for the selected MSA.
        // If no bounds and Metro, then just that MSA
        // If bounds and type MSA, then all MSAs
        // If bounds and no type, then Everything.  

        if( typeof loadParams.geo_query_type !== 'undefined'){
            geoQueryType = loadParams.geo_query_type.values;
            $('#geoTypeQuerySelector').val(geoQueryType);
        } else {
            addParam('geo_query_type', 'selected' );
        }

        $('#geoTypeQuerySelector').change( function(){
            var el = $('#geoTypeQuerySelector');
            geoQueryType = el.val();
            addParam('geo_query_type', geoQueryType );
            moveEndAction[geoQueryType]();
        });


        // Set a global variable that determines which data will be pulled through on "init" function
        // Bounds should be passed for MSA and All, but not for the selected MSA.
        // If no bounds and Metro, then just that MSA
        // If bounds and type MSA, then all MSAs
        // If bounds and no type, then Everything.  

        if( typeof loadParams.geo_query_type !== 'undefined'){
            console.log("geoQueryType: ", loadParams.geo_query_type.values);
            geoQueryType = loadParams.geo_query_type.values;
        } else {
            addParam('geo_query_type', 'selected' );
        }

        // On Branch selection, change params and use the toggle helper
        $('#geoQueryTypeSelect').change( function(){
            var el = $('#gepQueryTypeSelect');
            geoQueryType = el.prop('selected').val();
            addParam('geo_query_type', geoQueryType );
        });
        // End geoQueryType stuff        

        // Check for branch parameters
        if( typeof loadParams.branches !== 'undefined'){
            branchStatus = (loadParams.branches.values === 'true');
            $('#branchSelect').prop('checked', branchStatus );
            toggleBranches(branchStatus);
        } else {
            addParam('branches', false );
        }

        // On Branch selection, change params and use the toggle helper
        $('#branchSelect').change( function(){
            var el = $('#branchSelect');
            var status = el.prop('checked');
            toggleBranches(status);            
        });

        if( typeof loadParams.peers !== 'undefined'){
            if( lhStatus === true){
                $('#peerSelect').prop('checked', false);
                console.log("Peer and Hierarchy cannot be checked at the same time. Unchecking Peers.");
            } else {
                peerStatus = (loadParams.peers.values === 'true');
                $('#peerSelect').prop('checked', peerStatus );
                $('#superSelect').prop('disabled', peerStatus );
                togglePeers(peerStatus);
            }
        } else {
            addParam('peers', false );
        }

        // If peers selected, change params and toggle helper
        $('#peerSelect').change( function(){
            var el = $('#peerSelect');
            var status = el.prop('checked');
            togglePeers(status);
            $('#superSelect').prop('disabled', status);
            initCalls(geoQueryType);
        });

        // When the user changes the action taken data selector, re-initialize
        $('#action-taken-selector').on('change', function(){
            addParam( 'action', $('#action-taken-selector option:selected').val() );
            initCalls(geoQueryType);
        });

        // Generate the tool-tip listener for anything with that class
        $('.tooltipsy').tooltipsy({
            className: 'bubbletooltip_tip',
            offset: [1,0],
            show: function (e, $el) {
                $el.fadeIn(100);
            },
            hide: function (e, $el) {
                $el.fadeOut(450);
            }
        });

        if( typeof loadParams.category !== 'undefined'){
            assignCat(loadParams.category.values);
            layerUpdate( cat );
            $( catId ).addClass('active-layer');
        } else {
            assignCat('inv_non_hisp_white_only_perc');
            layerUpdate( cat );
            $( catId ).addClass('active-layer');
        }
        
        var categoryOptions = $('.map-divider-minor.option');
        
        categoryOptions.on('click', function(e){
            categoryOptions.removeClass('active-layer');
            var selectedOption = $(this);
            assignCat( selectedOption.attr('id') );
            selectedOption.addClass('active-layer');
            layerUpdate( cat );
        });

        // When the user has stopped moving the map, check for new branches,
        // and run init(), with a slight delay to ensure many moves in a row do not crowd the queue
        map.on('moveend', function(e){
            if( $('#branchSelect').prop('checked') ){
                toggleBranches(true);
            }
        });

        map.on('moveend', function(){
            moveEndAction[geoQueryType]();
        });
        map.on('zoomend', function(){
            buildKeyCircles();
        });
        map.on('overlayadd', function(){
            if( map.hasLayer(layers.MSALabels) ){
                layers.MSALabels.bringToFront();
            }
        });

        map.on('moveend', _.debounce(moveEndAction[geoQueryType], 500));

        // When the page loads, update the print link, and update it whenever the hash changes
        updatePrintLink();
        updateCensusLink();

        layerUpdate( cat );

        $( window ).on('hashchange', function(){
            updatePrintLink();
            updateCensusLink();
            initCalls(geoQueryType);
        });

<<<<<<< HEAD
        // Update links to peers
        getPeerLinks();
        
        // Kick off the application
        initCalls(geoQueryType);

    });
=======
        // Let the application do its thing 
        initCalls(geoQueryType);

    });
    
>>>>>>> updated init functions to handle msa clipping cases

    // Global variable to store the MSAMD codes for those MSAs on the map
    var msaArray = [];

    // Global object with methods to perform when the map moves.
    var moveEndAction = {};
    moveEndAction.selected = function(){
        // no action required.
    };
    moveEndAction.all_msa = function(){
        // go get our MSA list.
        var oldMsaArray = msaArray.slice(0);
        $.when( getMsasInBounds() ).done(function(data){
            var intersect = _.intersection(oldMsaArray, data);
            // console.log("Intersection: ", intersect);
            // console.log("oldMSA Array: ", oldMsaArray);
            if (intersect.length !== oldMsaArray.length ){ // If the intersection is not the same, init
                initCalls(geoQueryType);
            } else if (data.length !== intersect.length){ // Length of intersect and new data must be same
                initCalls(geoQueryType);
            } else {
                // console.log('No call required - MSAs are the same');
            }
        });
    };
    moveEndAction.all = function(){
        initCalls(geoQueryType);
    };

    function initCalls(geoQueryType){
        var gt = geoQueryType;
        // console.log("GT EQUALS: ", gt);
        var action = getActionTaken( $('#action-taken-selector option:selected').val() );
        if( gt === 'selected'){
            // run init with no bounds and no geo_type
            blockStuff();
            $.when( getTractsInBounds(false, false), getTractData(action, false, false) ).done( function(data1, data2){
                init(data1, data2);
            });
        } else if ( gt === 'all_msa'){
            // run init with bounds and geo_type = msa
            blockStuff();
            $.when( getTractsInBounds(getBoundParams(), 'msa'), getTractData(action, getBoundParams(), 'msa') ).done( function(data1, data2){
                init(data1, data2);  
            });
            // get msa info and create list of MSAs
            // on mousemoveend check if MSA list changes. If yes, get data with current bounds, else do nothing
        } else if ( gt === 'all'){
            // run init with bounds and geo_type = false
            blockStuff();
            $.when( getTractsInBounds( getBoundParams(), false ), getTractData(action, getBoundParams(), false )).done( function(data1, data2){
                init(data1, data2);
            });
        }

    }

    // Do what you need to do with the received data to build the map
    function init(data1, data2){
        // console.log("Data 1: ", data1);
        // console.log("Data 2: ", data2);
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
        
        // Update the key with the correct circle size
        buildKeyCircles();

        // Get list of MSAs and assign it to the global var
        $.when( getMsasInBounds() ).done(function(data){
            msaArray = data;
        });

        // Unblock the user interface (remove gradient)
        $.unblockUI();
        isUIBlocked = false;
    }

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
    
    function destroyLarChart() {
        d3.select("#plot-container").selectAll("*").remove();
    }

    function plotLarVolume() {

	var margin = {top: 20, right: 20, bottom: 30, left: 40},
	    width = 1180 - margin.left - margin.right,
	    height = 200 - margin.top - margin.bottom;
	var barWidth = width / larVolume.length;

	var data = _.zip(pctMinority, larVolume);
	data = _.sortBy(data, function(item) { return item[0]; });
	data = _.zip.apply(_, data);
	pctMinority = data[0];
	larVolume = data[1];

	var colorMap = d3.scale.quantile().domain([0, 0.5, 0.8, 1.0]).range(["#E8E7E3", "#B7C8D6", "#7FA2BB"]);

	d3.select("#plot-container").selectAll("*").remove();
	
	var larSvg = d3.select("#plot-container")
		.append("svg")
                .attr("width", width)
                .attr("height", height);

	var minSvg = d3.select("#plot-container")
		.append("svg")
		.attr("width", width)
		.attr("height", height);
	
	var larChart = larSvg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	var minChart = minSvg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var larX = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);
	var larY = d3.scale.linear().range([height, 0]);
	var larXAxis = d3.svg.axis().scale(larX).orient("bottom");
	var larYAxis = d3.svg.axis().scale(larY).orient("left");

	var minX = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);
	var minY = d3.scale.linear().range([height, 0]);
	var minXAxis = d3.svg.axis().scale(minX).orient("bottom");
	var minYAxis = d3.svg.axis().scale(minY).orient("left");

	larX.domain(geoIds);
	larY.domain([0, d3.max(larVolume, function(d) { return d; })]);

	minX.domain(geoIds);
	minY.domain([0, d3.max(pctMinority, function(d) { return d; })]);

>>>>>>> updated init functions to handle msa clipping cases

    // Global variable to store the MSAMD codes for those MSAs on the map
    var msaArray = [];

    // Global object with methods to perform when the map moves.
    var moveEndAction = {};
    // Store the last action so we can check if it's different and redraw.
    var oldEndAction = geoQueryType; 
    moveEndAction.selected = function(){
        if( oldEndAction === 'selected'){
            console.log("No action required for 'selected' status. Nothing happens.");
        } else { 
            initCalls(geoQueryType);
            oldEndAction = 'selected';   
        }
        
    };
    moveEndAction.all_msa = function(){
        var oldMsaArray = msaArray.slice(0);
        if( oldEndAction === 'all_msa'){
            $.when( getMsasInBounds() ).done(function(data){
                var intersect = _.difference(data, oldMsaArray);
                if (intersect.length > 0 ){ // If the intersection is not the same, init
                    initCalls(geoQueryType);
                } else if (intersect.length === 0){
                    console.log('No call required - MSAs are the same');
                }
            });
        } else {
            initCalls(geoQueryType);
            oldEndAction = 'all_msa';
        }
    };
    moveEndAction.all = function(){
        initCalls(geoQueryType);
        oldEndAction = 'all';
    };

    function initCalls(geoQueryType){
        var gt = geoQueryType;
        var action = getActionTaken( $('#action-taken-selector option:selected').val() );
        if( gt === 'selected'){
            // run init with no bounds and no geo_type
            blockStuff();
            $.when( getTractsInBounds(false, false), getTractData(action, false, false) ).done( function(data1, data2){
                init(data1, data2);
            });
        } else if ( gt === 'all_msa'){
            // run init with bounds and geo_type = msa
            blockStuff();
            $.when( getTractsInBounds(getBoundParams(), 'msa'), getTractData(action, getBoundParams(), 'msa') ).done( function(data1, data2){
                init(data1, data2);  
            });
        } else if ( gt === 'all'){
            // run init with bounds and geo_type = false
            blockStuff();
            $.when( getTractsInBounds( getBoundParams(), false ), getTractData(action, getBoundParams(), false )).done( function(data1, data2){
                init(data1, data2);
            });
        }

    }

    // Do what you need to do with the received data to build the map
    function init(data1, data2){
        var hashInfo = getHashParams(),
            layerInfo = getLayerType(hashInfo.category.values);

        // Create our two global data objects with our returned data
        rawGeo = data1[0];
        rawData = data2[0];

        // Create our Tract Data Object (Datastore.tracts) from the raw sources
        createTractDataObj(); 

        // Redraw the circles using the created tract object AND the layer bubble type
        redrawCircles(dataStore.tracts, layerInfo.type );
        
        // Update the key with the correct circle size
        buildKeyCircles();

        // Get list of MSAs and assign it to the global var
        $.when( getMsasInBounds() ).done(function(data){
            msaArray = data;
        });

        // Unblock the user interface (remove gradient)
        $.unblockUI();
        isUIBlocked = false;
    }

