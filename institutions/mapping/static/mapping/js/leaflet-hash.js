(function(window) {
	var HAS_HASHCHANGE = (function() {
		var doc_mode = window.documentMode;
		return ('onhashchange' in window) &&
			(doc_mode === undefined || doc_mode > 7);
	})();

	L.Hash = function(map) {
		this.onHashChange = L.Util.bind(this.onHashChange, this);

		if (map) {
			this.init(map);
		}
	};

	// Change this to parse the different options as an object.
	L.Hash.parseHash = function(hash) {
		var params = getHashParams();	
		console.log( 'params zoom: ', params.zoom);	
		if( typeof params.zoom != 'undefined' || typeof params.lat != 'undefined' || typeof params.lon != 'undefined') {
			var zoom = parseInt(params.zoom.values, 10),
			lat = parseFloat(params.lat.values),
			lon = parseFloat(params.lon.values);
			if (isNaN(zoom) || isNaN(lat) || isNaN(lon)) {
				return false;
			} else {
				return {
					center: new L.LatLng(lat, lon),
					zoom: zoom, 
					params: params
				};
			}
		} else {
			return false;
		}
	};

	L.Hash.formatHash = function(map) {
		var center = map.getCenter(),
			zoom = map.getZoom(),
			precision = Math.max(0, Math.ceil(Math.log(zoom) / Math.LN2)),
			returnObj = {
				'zoom': { values: zoom, comparator: '='},
				'lat': { values: center.lat.toFixed(3), comparator: '=' },
				'lon': { values: center.lng.toFixed(3), comparator: '=' }
			};
			return returnObj; 	
	};

	L.Hash.prototype = {
		map: null,
		lastHash: null,

		parseHash: L.Hash.parseHash,
		formatHash: L.Hash.formatHash,

		init: function(map) {
			this.map = map;

			// reset the hash
			this.lastHash = null;
			this.onHashChange();

			if (!this.isListening) {
				this.startListening();
			}
		},

		removeFrom: function(map) {
			if (this.changeTimeout) {
				clearTimeout(this.changeTimeout);
			}

			if (this.isListening) {
				this.stopListening();
			}

			this.map = null;
		},

		onMapMove: function() {
			// bail if we're moving the map (updating from a hash),
			// or if the map is not yet loaded
			console.log('onMapMove run');
			var hash;

			if (this.movingMap || !this.map._loaded) {
				return false;
			}

			// If getHashParams returns no zoom, etc it is created for initialization
			if ( !this.parseHash(hash) ){
				hash = getHashParams();
				_.extend(hash, this.formatHash(this.map) );
				updateUrlHash(hash);
			} else {
				hash = getHashParams();
				var newParams = this.formatHash(this.map);
				
				_.each(newParams, function(val,key){
					hash[key].values = val.values;
					hash[key].comparator = '=';
				});
				updateUrlHash(hash);
			}

			this.lastHash = hash;

		},

		movingMap: false,
		update: function() {
			var hash = getHashParams();
			if ( _.isEqual( hash, this.lastHash) ){
				return false;
			}
			var parsed = this.parseHash(hash);
			if (parsed) {
				this.movingMap = true;

				this.map.setView(parsed.center, parsed.zoom);

				this.movingMap = false;
			} else {
				console.log('Update else calling onMapMove');
				this.onMapMove(this.map);
			}
		},

		// defer hash change updates every 200ms
		changeDefer: 200,
		changeTimeout: null,
		onHashChange: function() {
			// throttle calls to update() so that they only happen every
			// `changeDefer` ms
			if (!this.changeTimeout) {
				var that = this;
				this.changeTimeout = setTimeout(function() {
					that.update();
					that.changeTimeout = null;
				}, this.changeDefer);
			}
		},

		isListening: false,
		hashChangeInterval: null,
		startListening: function() {
			console.log('startListening calling onMapMove');
			this.map.on("moveend", this.onMapMove, this);

			if (HAS_HASHCHANGE) {
				L.DomEvent.addListener(window, "hashchange", this.onHashChange);
			} else {
				clearInterval(this.hashChangeInterval);
				this.hashChangeInterval = setInterval(this.onHashChange, 500);
			}
			this.isListening = true;
		},

		stopListening: function() {
			console.log('stopListening calling onMapMove');
			this.map.off("moveend", this.onMapMove, this);

			if (HAS_HASHCHANGE) {
				L.DomEvent.removeListener(window, "hashchange", this.onHashChange);
			} else {
				clearInterval(this.hashChangeInterval);
			}
			this.isListening = false;
		}
	};

	L.hash = function(map) {
		return new L.Hash(map);
	};
	L.Map.prototype.addHash = function() {
		this._hash = L.hash(this);
	};
	L.Map.prototype.removeHash = function() {
		this._hash.removeFrom();
	};
})(window);

// Return the hash parameters from the current URL. [source](http://goo.gl/mebsOI)
function getHashParams(){
    var hashParams = {};
    var e,
        a = /\+/g,  // Regex for replacing addition symbol with a space
        r = /([^!&;=<>]+)(!?[=><]?)([^&;]*)/g,
        d = function (s) { return decodeURIComponent(s.replace(a, ' ')); },
        q = window.location.hash.substring(1).replace(/^!\/?/, '');

    while (e = r.exec(q)) {
      hashParams[d(e[1])] = {
        values: d(e[3]),
        comparator: d(e[2])
      };
    }
    return hashParams;
}

// The `generateUrlHash` method builds and returns a URL hash from a set of object parameters
function updateUrlHash(params) {
    var newHash,
    hashParams = [];
    // Loop through params, stringify them and push them into the temp array.
    function buildHashParam( param, name ) {
        console.log('name: ', name);
        console.log("param: ", param);

      hashParams.push( name + '=' + param.values );

    }
    console.log('params inside updateUrlHash: ', params);
    _.forEach( params, buildHashParam );
    //console.log('Hash Params: ', hashParams);
    newHash = '&' + hashParams.join('&');
    window.location.hash = newHash;

}

/* 
    END HASH PARSING FUNCTIONS
*/
