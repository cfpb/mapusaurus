    /* 
        ---- DRAW CIRCLES AND MARKERS ----
    */

    var baseStyle = { fillOpacity: 0.7, className: 'lar-circle seq-circle', fillColor: '#111111', stroke: false};

    //  population-less tracts
    var noStyle = {stroke: false, weight: 0, fill: false};

    function redrawCircles( geoData ){
        // Show data load icon
        $('#bubbles_loading').show();     
        layers.Centroids.clearLayers();
        _.each(geoData, function(geo) {
            var bubble = drawCircle(geo);
        });
    }

    function drawCircle(geo, options){
        var data = geo,
            style;

        // If no population exists, use the "no style" style (hidden)
        if (geo['total_pop'] === 0 || geo.volume === 0 ) {
            style = noStyle;
        } else {
            style = baseStyle
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
                .setContent('<div class="bubble-header"><b>Tract '+ circle.geoid + '</div><div><span class="circle-hover-label">' +data['volume'] + '</span></b> LAR<br/><b><span class="circle-hover-label">' + data['num_households'] + '</span></b> Households</div>')
                    // '<div class="bubble-label"><b>Hispanic</b>: (' + hisp + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + hisp +'></div></div>' +
                    // '<div class="bubble-label"><b>Black</b>: (' + black + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + black +'></div></div>' + 
                    // '<div class="bubble-label"><b>Asian</b>: (' + asian + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + asian +'></div></div>' + 
                    // '<div class="bubble-label"><b>White</b>: (' + white + '%)</div><div class="css-chart"><div class="css-chart-inner" data-min=' + white +'></div></div>' )
                .setLatLng(e.latlng)
                .openOn(map);
            
            // $('.css-chart-inner').each( function(index){
            //     var self = $( this ),
            //         width = ( self.data('min') / 100 )*120,
            //         widthStr = width.toString() + 'px';
            //     self.css('width', widthStr);
            //     self.css('background-color', '#000');
            // });
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