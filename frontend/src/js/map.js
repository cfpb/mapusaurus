'use strict';

// Handle console.log statements in older versions of IE
if (!window.console) console = {log: function() {}};

// globals for table.js
var showDataContainer; 
var destroyLarChart;

// globals for layer selection and query type
var cat, catId;
var geoQueryType = 'selected';

// When the DOM is loaded, get state from URL params and add click listeners
$(document).ready(function(){
    // Set globals for peer, branch, and hierarchy checkboxes
    var lhStatus, peerStatus, branchStatus;

    // Invoke our tabs JavaScript for left navigation
    $('.tabs').show();

    // On window resize (when not in print view) set the map height anew
    $( window ).resize(function() {
        if( window.location.href.indexOf('print') < 0){
            setMapHeight();
        }
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
    // End geoQueryType code       

    // Check for branch URL parameters on load
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
            console.log('Peer and Hierarchy cannot be checked at the same time. Unchecking Peers.');
        } else {
            peerStatus = (loadParams.peers.values === 'true');
            $('#peerSelect').prop('checked', peerStatus );
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
        var act = $('#action-taken-selector option:selected').val();
        addParam( 'action', act);
        $('#actionTaken').text( getActionTaken( act ) );
        initCalls(geoQueryType);
    });

    // Generate tooltips - that one self documents
    generateTooltips();

    // Handle Map Key Show / Hide
    var keyHide = $('.hide-key');
    var keyShow = $('.show-key');
    var keyContents = $('.key-contents');
    var minorityKeyContents = $('.minority-key');
    keyHide.on('click', function(e){
        keyShow.removeClass('hidden');
        keyContents.addClass('hidden');
        minorityKeyContents.addClass('hidden');
        keyHide.addClass('hidden');
    });
    keyShow.on('click', function(e){
        keyHide.removeClass('hidden');
        keyContents.removeClass('hidden');
        minorityKeyContents.removeClass('hidden');
        keyShow.addClass('hidden');
    });

    // Handle layer detection on load, and click actions following
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
    });

    // Update links to peers
    getPeerLinks();
    
    // Kick off the application
    initCalls(geoQueryType);

    // Change the default mapbox layer select icon
    $('.leaflet-control-layers-toggle').css(
        {
            'background-image': 'url(/static/basestyle/img/icon_map-layers.png)',
            'background-size': '26px',
            'background-position': '0,0'
    });

    // Set the Action Taken value in the Key
    $('#actionTaken').text( getActionTaken( $('#action-taken-selector option:selected').val() ) );

});

// Global variable to store the MSAMD codes for those MSAs on the map
var msaArray = [];

// Global object with methods to perform when the map moves.
var moveEndAction = {};
// Store the last action so we can check if it's different and reload data if required.
var oldEndAction = geoQueryType; 

moveEndAction.selected = function(){
    if( oldEndAction === 'selected'){
    } else { 
        initCalls(geoQueryType);
        oldEndAction = 'selected';   
    }
};
// For All MSAs to be displayed, check to see what has already been loaded. If data present, skip load
// otherwise continue to load all MSAs with the appropriate params.
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

// Always pull data on mouseMoveEnd on map
moveEndAction.all = function(){
    initCalls(geoQueryType);
    oldEndAction = 'all';
};

// Function routes the application based on the geoQueryType selected (different params required for each type)
function initCalls(geoQueryType){
    var gt = geoQueryType;
    var action = getActionTaken( $('#action-taken-selector option:selected').val() );
    if( gt === 'selected'){
        // run init with no bounds and no geo_type
        blockStuff();
        $.when( getTractData(action, false, false) ).done( function(data1){
            init(data1);
        });
    } else if ( gt === 'all_msa'){
        // run init with bounds and geo_type = msa
        blockStuff();
        $.when( getTractData(action, getBoundParams(), 'msa') ).done( function(data1){
            init(data1);  
        });
    } else if ( gt === 'all'){
        // run init with bounds and geo_type = false
        blockStuff();
        $.when( getTractData(action, getBoundParams(), false )).done( function(data1){
            init(data1);
        });
    }

}

// Do what you need to do with the received data to build the map
function init(data1){
    var hashInfo = getHashParams(),
        layerInfo = getLayerType(hashInfo.category.values);

    // Create our two global data objects with our returned data
    rawData = data1;

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
