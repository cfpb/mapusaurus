
/*
    Draw the SVG Key based on radius params of existing Leaflet circle ranges
*/
function buildKeyCircles(){
    var params = getHashParams();
    var selector = $('#keySvg');
    selector.html('');
    
    // Circles to be generated
    var circles = getRange(map._layers);
    
    // Handle return of empty array (no tracts or no records)
    if( circles.length === 0 ){
        selector.html('No records found');
        return false;
    }

    // Get max, middle, min
    // Draw new circles for each in Leaflet with index IDs
    // Put those index IDs into an array
    // Copy those SVG elements using jQuery to the Key

    // Get the current scaling value from the drop-down menu.
    var $scale = $('#action-taken-selector option:selected');
    var scaleMultiplier = $scale.data('scale');
    var posx = 0;
    var rad = 0;
    var maxRad = _.max(circles, function(circleObj){ return circleObj._radius; })._radius;
    var posy = maxRad*2;
    var textPosy = posy + 16; //Add 16px for font

    // Create the initial SVG element
    var svgStr = '<svg height="' + (maxRad*2 + 20) + '">';

    for( var i=0; i<circles.length; i++ ){
        var circle = circles[i];
        rad = circle._radius;
        posx = posx + 45; // Move the circles horizontally, y values stay constant    
        svgStr += '<circle cx="' + posx + '" cy="' + (posy-rad) + '" r="' + rad + '" fillColor="#111111" fill-opacity=".7" stroke=false color="#333"/>';
        svgStr += '<text x="' + (posx) + '" y="' + textPosy + '" font-size="1em" text-anchor="middle">'+ circle.volume + '</text>';
    }

    svgStr += '</svg>';
    selector.html(svgStr);

}

/*
    Get the circle data for a min, max, and two points in between
*/
function getRange(data){
    // Find all circles in the current leaflet layer that are LAR circles
    var circles = _.matches({type: "tract-circle" });
    var circleFilter = _.filter(data, circles);

    // If no tracts in view, return blank array
    if ( circleFilter.length === 0 ){
        return valArray = [];
    }

    // Get the min and max
    var max = _.max(data, function(circleObj){ return circleObj._mRadius; });
    var min = _.min(data, function(circleObj){ return circleObj._mRadius; });

    // Determine the midpoint LAR counts for min / max
    var multiple = (max.volume - min.volume)/2;
    var drawNewArray = [(min.volume + multiple)];

    var keyCircles, keyCirclesFilter, valArray;
    
    // If the maximum volume is less than 2, only return the single max point.
    if ( max.volume < 2 && max.volume > 0){
        return valArray = [max];
    // if max volume for all tracts for the lender is zero, return empty array
    } else if ( max.volume === 0 ){
        return valArray = [];
    }

    if ( min.volume === 0 ){
        min = {
            volume: 1,
        };
        drawNewArray = [min.volume, (min.volume + multiple), max.volume];

        // Draw a fresh circle with _mRadius properties for two middle points
        _.each(drawNewArray, function(val, i){
            addKeyLayerCircle(val,i);
        });
        
        // Retrieve the layer info for these midpoint circles
        keyCircles = _.matches({"keyCircle": 1 });
        keyCirclesFilter = _.filter(data, keyCircles);

        // Add circles to our key array
        valArray = [ keyCirclesFilter[0], keyCirclesFilter[1], max ];
    } else {
        // Draw a fresh circle with _mRadius properties for two middle points
        _.each(drawNewArray, function(val, i){
            addKeyLayerCircle(val, i);
        });

        // Retrieve the layer info for these midpoint circles
        keyCircles = _.matches({"keyCircle": 1 });
        keyCirclesFilter = _.filter(data, keyCircles);

        // Add circles to our key array
        valArray = [ min, keyCirclesFilter[0], max ];        
    }

    if ( max.volume < 5 ){
        valArray = [valArray[0], valArray[2]];
    }


    return valArray;
}

function addKeyLayerCircle(volume, index){
    var geo = {
        volume: Math.round(volume),
        centlat: map.getCenter().lat, // Center lat required as Meters per pixel varies at different latitudes
        centlon: 1,
        geoid: index
    };
    var options = {
        keyCircle: 1 // Designate this as a "key Circle" so our filter applies in getRange
    };

    // Use the existing circle draw
    drawCircle(geo, options);
}
