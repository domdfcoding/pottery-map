// Adapted from https://github.com/jieter/leaflet.layerscontrol-minimap
// Copyright (c) 2013, Jan Pieter Waagmeester
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
// ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

(function() {
	function r(e, n, t) {
		function o(i, f) {
			if (!n[i]) {
				if (!e[i]) {
					var c = 'function' == typeof require && require;
					if (!f && c) return c(i, !0);
					if (u) return u(i, !0);
					var a = new Error("Cannot find module '" + i + "'");
					throw a.code = 'MODULE_NOT_FOUND', a;
				}
				var p = n[i] = { exports: {} };
				e[i][0].call(p.exports, function(r) {
					var n = e[i][1][r];
					return o(n || r);
				}, p, p.exports, r, e, n, t);
			}
			return n[i].exports;
		}
		for (var u = 'function' == typeof require && require, i = 0; i < t.length; i++) o(t[i]);
		return o;
	}
	return r;
})()({ 1: [function(require, module, exports) {
	/*
	 * Leaflet.layerscontrol-minimap
	 *
	 * Layers control with synced minimaps for Leaflet.
	 *
	 * Jan Pieter Waagmeester <jieter@jieter.nl>
	 */
	var cloneLayer = require('leaflet-clonelayer');

	require('leaflet.sync');

	L.Control.Layers.MinimapToggle = L.Control.Layers.Minimap.extend({
		options: {
			position: 'topright',
			topPadding: 10,
			bottomPadding: 40,
			overlayBackgroundLayer: L.tileLayer('http://{s}.tile.openstreetmap.se/hydda/base/{z}/{x}/{y}.png', {
				attribution:
					'Tiles courtesy of <a href="http://openstreetmap.se/" target="_blank">OpenStreetMap Sweden</a> &mdash; '
					+ 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			}),
		},


		_initLayout: function() {
			L.Control.Layers.prototype._initLayout.call(this);
			L.DomEvent.off(this._container, 'mouseleave', this.collapse, this);
			L.DomEvent.off(this._container, 'mouseenter', this._expandSafely, this);

			L.DomEvent.off(this._layersLink);
			L.DomEvent.on(this._layersLink, {
				keydown: function(e) {
					if (e.keyCode === 13) {
						this._expandSafely();
					}
				},
				click: function(e) {
					console.log('Layer button clicked');
					L.DomEvent.preventDefault(e);
					// L.DomEvent.stopPropagation(e);
					if (!this.isCollapsed()) {
						this.collapse();
					} else {
						this._expandSafely();
					}
				},
			}, this);

			L.DomUtil.addClass(this._container, 'leaflet-control-layers-minimap');

			var scrollContainer = this._scrollContainer();
			L.DomEvent.on(scrollContainer, 'scroll', this._onListScroll, this);
			// disable scroll propagation, Leaflet is going to do this too
			// https://github.com/Leaflet/Leaflet/issues/5277
			L.DomEvent.disableScrollPropagation(scrollContainer);
		},

	});

	L.control.layers.minimap.toggle = function(baseLayers, overlays, options) {
		return new L.Control.Layers.MinimapToggle(baseLayers, overlays, options);
	};
}, { 'leaflet-clonelayer': 2, 'leaflet.sync': 3 }], 2: [function(require, module, exports) {
	function cloneOptions(options) {
		var ret = {};
		for (var i in options) {
			var item = options[i];
			if (item && item.clone) {
				ret[i] = item.clone();
			} else if (item instanceof L.Layer) {
				ret[i] = cloneLayer(item);
			} else {
				ret[i] = item;
			}
		}
		return ret;
	}

	function cloneInnerLayers(layer) {
		var layers = [];
		layer.eachLayer(function(inner) {
			layers.push(cloneLayer(inner));
		});
		return layers;
	}

	function cloneLayer(layer) {
		var options = cloneOptions(layer.options);

		// we need to test for the most specific class first, i.e.
		// Circle before CircleMarker

		// Renderers
		if (layer instanceof L.SVG) {
			return L.svg(options);
		}
		if (layer instanceof L.Canvas) {
			return L.canvas(options);
		}

		// GoogleMutant GridLayer
		if (L.GridLayer.GoogleMutant && layer instanceof L.GridLayer.GoogleMutant) {
			var googleLayer = L.gridLayer.googleMutant(options);

			layer._GAPIPromise.then(function() {
				var subLayers = Object.keys(layer._subLayers);

				for (var i in subLayers) {
					googleLayer.addGoogleLayer(subLayers[i]);
				}
			});

			return googleLayer;
		}

		// Tile layers
		if (layer instanceof L.TileLayer.WMS) {
			return L.tileLayer.wms(layer._url, options);
		}
		if (layer instanceof L.TileLayer) {
			return L.tileLayer(layer._url, options);
		}
		if (layer instanceof L.ImageOverlay) {
			return L.imageOverlay(layer._url, layer._bounds, options);
		}

		// Marker layers
		if (layer instanceof L.Marker) {
			return L.marker(layer.getLatLng(), options);
		}

		if (layer instanceof L.Circle) {
			return L.circle(layer.getLatLng(), layer.getRadius(), options);
		}
		if (layer instanceof L.CircleMarker) {
			return L.circleMarker(layer.getLatLng(), options);
		}

		if (layer instanceof L.Rectangle) {
			return L.rectangle(layer.getBounds(), options);
		}
		if (layer instanceof L.Polygon) {
			return L.polygon(layer.getLatLngs(), options);
		}
		if (layer instanceof L.Polyline) {
			return L.polyline(layer.getLatLngs(), options);
		}

		if (layer instanceof L.GeoJSON) {
			return L.geoJson(layer.toGeoJSON(), options);
		}

		if (layer instanceof L.FeatureGroup) {
			return L.featureGroup(cloneInnerLayers(layer));
		}
		if (layer instanceof L.LayerGroup) {
			return L.layerGroup(cloneInnerLayers(layer));
		}

		throw 'Unknown layer, cannot clone this layer. Leaflet-version: ' + L.version;
	}

	if (typeof exports === 'object') {
		module.exports = cloneLayer;
	}
}, {}], 3: [function(require, module, exports) {
	/*
	 * Extends L.Map to synchronize the interaction on one map to one or more other maps.
	 */

	(function() {
		var NO_ANIMATION = {
			animate: false,
			reset: true,
			disableViewprereset: true,
		};

		L.Sync = function() {};
		/*
		 * Helper function to compute the offset easily.
		 *
		 * The arguments are relative positions with respect to reference and target maps of
		 * the point to sync. If you provide ratioRef=[0, 1], ratioTarget=[1, 0] will sync the
		 * bottom left corner of the reference map with the top right corner of the target map.
		 * The values can be less than 0 or greater than 1. It will sync points out of the map.
		 */
		L.Sync.offsetHelper = function(ratioRef, ratioTarget) {
			var or = L.Util.isArray(ratioRef) ? ratioRef : [0.5, 0.5];
			var ot = L.Util.isArray(ratioTarget) ? ratioTarget : [0.5, 0.5];
			return function(center, zoom, refMap, targetMap) {
				var rs = refMap.getSize();
				var ts = targetMap.getSize();
				var pt = refMap.project(center, zoom)
					.subtract([(0.5 - or[0]) * rs.x, (0.5 - or[1]) * rs.y])
					.add([(0.5 - ot[0]) * ts.x, (0.5 - ot[1]) * ts.y]);
				return refMap.unproject(pt, zoom);
			};
		};

		L.Map.include({
			sync: function(map, options) {
				this._initSync();
				options = L.extend({
					noInitialSync: false,
					syncCursor: false,
					syncCursorMarkerOptions: {
						radius: 10,
						fillOpacity: 0.3,
						color: '#da291c',
						fillColor: '#fff',
					},
					offsetFn: function(center, zoom, refMap, targetMap) {
						// no transformation at all
						return center;
					},
				}, options);

				// prevent double-syncing the map:
				if (this._syncMaps.indexOf(map) === -1) {
					this._syncMaps.push(map);
					this._syncOffsetFns[L.Util.stamp(map)] = options.offsetFn;
				}

				if (!options.noInitialSync) {
					map.setView(
						options.offsetFn(this.getCenter(), this.getZoom(), this, map),
						this.getZoom(),
						NO_ANIMATION,
					);
				}
				if (options.syncCursor) {
					if (typeof map.cursor === 'undefined') {
						map.cursor = L.circleMarker([0, 0], options.syncCursorMarkerOptions).addTo(map);
					}

					this._cursors.push(map.cursor);

					this.on('mousemove', this._cursorSyncMove, this);
					this.on('mouseout', this._cursorSyncOut, this);
				}

				// on these events, we should reset the view on every synced map
				// dragstart is due to inertia
				this.on('resize zoomend', this._selfSetView);
				this.on('moveend', this._syncOnMoveend);
				this.on('dragend', this._syncOnDragend);
				return this;
			},

			// unsync maps from each other
			unsync: function(map) {
				var self = this;

				if (this._cursors) {
					this._cursors.forEach(function(cursor, indx, _cursors) {
						if (cursor === map.cursor) {
							_cursors.splice(indx, 1);
						}
					});
				}

				// TODO: hide cursor in stead of moving to 0, 0
				if (map.cursor) {
					map.cursor.setLatLng([0, 0]);
				}

				if (this._syncMaps) {
					this._syncMaps.forEach(function(synced, id) {
						if (map === synced) {
							delete self._syncOffsetFns[L.Util.stamp(map)];
							self._syncMaps.splice(id, 1);
						}
					});
				}

				if (!this._syncMaps || this._syncMaps.length == 0) {
					// no more synced maps, so these events are not needed.
					this.off('resize zoomend', this._selfSetView);
					this.off('moveend', this._syncOnMoveend);
					this.off('dragend', this._syncOnDragend);
				}

				return this;
			},

			// Checks if the map is synced with anything or a specifyc map
			isSynced: function(otherMap) {
				var has = this.hasOwnProperty('_syncMaps') && Object.keys(this._syncMaps).length > 0;
				if (has && otherMap) {
					// Look for this specific map
					has = false;
					this._syncMaps.forEach(function(synced) {
						if (otherMap == synced) has = true;
					});
				}
				return has;
			},

			// Callbacks for events...
			_cursorSyncMove: function(e) {
				this._cursors.forEach(function(cursor) {
					cursor.setLatLng(e.latlng);
				});
			},

			_cursorSyncOut: function(e) {
				this._cursors.forEach(function(cursor) {
					// TODO: hide cursor in stead of moving to 0, 0
					cursor.setLatLng([0, 0]);
				});
			},

			_selfSetView: function(e) {
				// reset the map, and let setView synchronize the others.
				this.setView(this.getCenter(), this.getZoom(), NO_ANIMATION);
			},

			_syncOnMoveend: function(e) {
				if (this._syncDragend) {
					// This is 'the moveend' after the dragend.
					// Without inertia, it will be right after,
					// but when inertia is on, we need this to detect that.
					this._syncDragend = false; // before calling setView!
					this._selfSetView(e);
					this._syncMaps.forEach(function(toSync) {
						toSync.fire('moveend');
					});
				}
			},

			_syncOnDragend: function(e) {
				// It is ugly to have state, but we need it in case of inertia.
				this._syncDragend = true;
			},

			// overload methods on originalMap to replay interactions on _syncMaps;
			_initSync: function() {
				if (this._syncMaps) {
					return;
				}
				var originalMap = this;

				this._syncMaps = [];
				this._cursors = [];
				this._syncOffsetFns = {};

				L.extend(originalMap, {
					setView: function(center, zoom, options, sync) {
						// Use this sandwich to disable and enable viewprereset
						// around setView call
						function sandwich(obj, fn) {
							var viewpreresets = [];
							var doit = options && options.disableViewprereset && obj && obj._events;
							if (doit) {
								// The event viewpreresets does an invalidateAll,
								// that reloads all the tiles.
								// That causes an annoying flicker.
								viewpreresets = obj._events.viewprereset;
								obj._events.viewprereset = [];
							}
							var ret = fn(obj);
							if (doit) {
								// restore viewpreresets event to its previous values
								obj._events.viewprereset = viewpreresets;
							}
							return ret;
						}

						// Looks better if the other maps 'follow' the active one,
						// so call this before _syncMaps
						var ret = sandwich(this, function(obj) {
							return L.Map.prototype.setView.call(obj, center, zoom, options);
						});

						if (!sync) {
							originalMap._syncMaps.forEach(function(toSync) {
								sandwich(toSync, function(obj) {
									return toSync.setView(
										originalMap._syncOffsetFns[L.Util.stamp(toSync)](center, zoom, originalMap, toSync),
										zoom,
										options,
										true,
									);
								});
							});
						}

						return ret;
					},

					panBy: function(offset, options, sync) {
						if (!sync) {
							originalMap._syncMaps.forEach(function(toSync) {
								toSync.panBy(offset, options, true);
							});
						}
						return L.Map.prototype.panBy.call(this, offset, options);
					},

					_onResize: function(event, sync) {
						if (!sync) {
							originalMap._syncMaps.forEach(function(toSync) {
								toSync._onResize(event, true);
							});
						}
						return L.Map.prototype._onResize.call(this, event);
					},

					_stop: function(sync) {
						L.Map.prototype._stop.call(this);
						if (!sync) {
							originalMap._syncMaps.forEach(function(toSync) {
								toSync._stop(true);
							});
						}
					},
				});

				originalMap.dragging._draggable._updatePosition = function() {
					L.Draggable.prototype._updatePosition.call(this);
					var self = this;
					originalMap._syncMaps.forEach(function(toSync) {
						L.DomUtil.setPosition(toSync.dragging._draggable._element, self._newPos);
						toSync.eachLayer(function(layer) {
							if (layer._google !== undefined) {
								var offsetFn = originalMap._syncOffsetFns[L.Util.stamp(toSync)];
								var center = offsetFn(originalMap.getCenter(), originalMap.getZoom(), originalMap, toSync);
								layer._google.setCenter(center);
							}
						});
						toSync.fire('move');
					});
				};
			},
		});
	})();
}, {}] }, {}, [1]);
