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

        //  We will use the tractid when redrawing
        circle.tractid = geo.tractid || '';
        circle.volume = geo.volume;
        circle.type = "tract-circle";
        circle.keyCircle = 0;

        if( typeof options !== "undefined"){
            circle.keyCircle = options.keyCircle;
        }

        circle.on('mouseover mousemove', function(e){
            new L.Rrose({ offset: new L.Point(0,0), closeButton: false, autoPan: false, y_bound: 160 })
                .setContent('<div class="bubble-header">Tract '+ circle.tractid + 
                    '</div><div class="lar-count"><span class="circle-hover-data">' +data['volume'] + 
                    '</span><span class="circle-hover-label">LAR</span></div><div class="hh-count"><span class="circle-hover-data">' + data['num_households'] + 
                    '</span><span class="circle-hover-label">Households</span></div></div>')
                .setLatLng(e.latlng)
                .openOn(map);
            
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
