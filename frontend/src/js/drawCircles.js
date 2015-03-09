    /* 
        ---- DRAW CIRCLES AND MARKERS ----
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
            if( layer.volume === 0 ){
                return false;
            }

            if( layerType === 'minority' ){
                var newStyle = {};
                _.extend(newStyle, baseStyle);
                newStyle.fillColor = updateMinorityCircleFill(layer.geoid);
                layer.setStyle( newStyle );
            } else if( layerType === 'seq'){
                layer.setStyle( seqBaseStyle );
            }
        });
        console.log('color update complete.');
    }


    function drawCircle(geo, layerType, options){
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
        circle.type = "tract-circle";
        circle.keyCircle = 0;

        if( typeof options !== "undefined"){
            circle.keyCircle = options.keyCircle;
        }

        circle.on('mouseover mousemove', function(e){
            var hisp,white,black,asian;
            hisp = (data['hispanic_perc']*100).toFixed(2);
            white = (data['non_hisp_white_only_perc']*100).toFixed(2);
            black = (data['non_hisp_black_only_perc']*100).toFixed(2);
            asian = (data['non_hisp_asian_only_perc']*100).toFixed(2);
            new L.Rrose({ offset: new L.Point(0,0), closeButton: false, autoPan: false, y_bound: 160 })
                .setContent('<div class="bubble-header"><b>Tract '+ circle.geoid + '<br/>' +data['volume'] + '</b> LAR | <b>' + data['num_households'] + '</b> HHs</div>' +
                    '<div class="bubble-label"><b>Hispanic</b>: (' + hisp + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + hisp +'></div></div>' +
                    '<div class="bubble-label"><b>Black</b>: (' + black + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + black +'></div></div>' + 
                    '<div class="bubble-label"><b>Asian</b>: (' + asian + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + asian +'></div></div>' + 
                    '<div class="bubble-label"><b>White</b>: (' + white + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + white +'></div></div>' )
                .setLatLng(e.latlng)
                .openOn(map);
            
            $('.css-chart-inner').each( function(index){
                var self = $( this ),
                    width = ( self.data('min') / 100 )*120,
                    widthStr = width.toString() + 'px';
                self.css('width', widthStr);
                self.css('background-color', '#000');
            });
        });
                    
        circle.on('mouseout', function(){ 
            map.closePopup();
        });

        layers.Centroids.addLayer(circle);

    }

    function drawMarker(data){
        var myIcon = L.icon({ iconUrl: '/static/basestyle/img/branch-marker_off.png', iconSize: [8,8] }),
            myIconHover = L.icon({ iconUrl: '/static/basestyle/img/branch-marker_on.png', iconSize: [8,8] });

        var marker = L.marker([data.lat, data.lon], {icon: myIcon });
        
        marker.on('mouseover mousemove', function(e){
            this.setIcon(myIconHover);
            new L.Rrose({ offset: new L.Point(0,0), closeButton: false, autoPan: false })
                .setContent('<div class="branch-marker">' + data.name + '<br/>' + data.city)
                .setLatLng(e.latlng)
                .openOn(map);            
        });

        marker.on('mouseout', function(e){
            this.setIcon(myIcon);
            map.closePopup();

        });

        layers.Branches.addLayer(marker);
    }

    /*
        END DRAW CIRCLES AND MARKERS SECTION
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
    ];

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
    }

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