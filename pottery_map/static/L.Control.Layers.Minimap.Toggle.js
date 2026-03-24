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

/*
 * Leaflet.layerscontrol-minimap-toggle
 *
 * Layers control with synced minimaps and visibility toggle for Leaflet.
 *
 * Dominic Davis-Foster <dominic@davis-foster.co.uk>
 */

L.Control.Layers.MinimapToggle = L.Control.Layers.Minimap.extend({
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
