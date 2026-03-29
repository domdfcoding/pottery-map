#!/usr/bin/env python3
#
#  map.py
"""
The map itself.
"""
#
#  Copyright © 2025 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import sys
from typing import Any

# 3rd party
import folium
import folium.plugins
import folium_layerscontrol_minimap
from domdf_folium_tools import embed_styles
from domdf_folium_tools.elements import NLSTileLayer, add_to, set_id
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import clean_writer
from folium.utilities import escape_backticks
from folium_zoom_state import BasemapFromURL, ZoomStateJS, ZoomStateMap

# this package
from pottery_map.templates import render_template
from pottery_map.utils import make_id

__all__ = ["make_map"]


class MarkerCluster(folium.plugins.MarkerCluster):
	default_js = []


class Map(ZoomStateMap):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_id(self, "pottery")
		self.options["maxZoom"] = kwargs["max_zoom"]


class Popup(folium.Popup):

	def __init__(
			self,
			html: str,
			id: str,  # noqa: A002  # pylint: disable=redefined-builtin
			max_width: str | int = 400,
			min_width: str | int = 245,
			**kwargs,
			):
		html_element = folium.Html(escape_backticks(html), script=True)
		html_element._id = id

		super().__init__(html=html_element, max_width=max_width, min_width=min_width, **kwargs)
		self._id = id


class MinimapLayerControl(folium_layerscontrol_minimap.MinimapLayerControl):
	default_js = []
	control_class_name = "L.control.layers.minimap.toggle"


def make_map(pottery_by_company: dict[str, Any], standalone: bool = True) -> Map:
	"""
	Map the pottery collection folium map.

	:param pottery_by_company:
	:param standalone: Create a standalone map with embedded CSS,
	"""

	osm_tiles = set_id(
			folium.TileLayer(tiles="OpenStreetMap", name="OpenStreetMap", show=False),
			"osm_carto",
			)

	m = Map(
			location=(53.02445128825057, -2.1834733161173445),
			font_size="16px",
			tiles=osm_tiles,
			max_zoom=20,
			)

	os10k = NLSTileLayer(
			"OS 1:10,000 1949-1972",
			"https://geo.nls.uk/mapdata3/os/britain10knationalgridnew/{z}/{x}/{y}.png",
			max_native_zoom=16,
			show=False,
			)

	os1250 = NLSTileLayer(
			"OS 1:1,250 1949-1975",
			"https://geo.nls.uk/maps/os/1250_B_2eng/{z}/{x}/{y}.png",
			max_native_zoom=20,
			show=False,
			)

	os2500 = NLSTileLayer(
			"OS 1:2,500 1948-1975",
			"https://geo.nls.uk/maps/os/2500_A_1S/{z}/{x}/{y}.png",
			max_native_zoom=18,
			show=False,
			)

	os25inch = NLSTileLayer(
			"OS 25 Inch, 1892-1914",
			"https://mapseries-tilesets.s3.amazonaws.com/25_inch/stafford/{z}/{x}/{y}.png",
			max_native_zoom=18,
			show=False,
			)

	set_id(os10k, "os10k").add_to(m)
	set_id(os1250, "os1250").add_to(m)
	set_id(os2500, "os2500").add_to(m)
	set_id(os25inch, "os25inch").add_to(m)

	ZoomStateJS(setup_basemap_state=True).add_to(m, embed_script=standalone)

	if standalone:
		embed_styles(m, importlib_resources.read_text("pottery_map.static", "pottery_map.css"))
	else:
		m.add_css_link("pottery_map.css", "./static/css/pottery_map.css")
		m.add_js_link("zoom_state.js", "static/js/zoom_state.js")

	m.add_js_link(*folium.plugins.MarkerCluster.default_js[0])
	marker_cluster = add_to(MarkerCluster(options={"maxClusterRadius": 50}, control=False), m, "collection")

	for company, company_data in pottery_by_company.items():

		if "location" not in company_data or not company_data["location"]:
			continue

		popup_text = render_template(
				"map_popup.jinja2",
				company=company,
				company_data=company_data,
				standalone=standalone,
				make_id=make_id,
				).splitlines()

		company_id = make_id(company)

		marker = folium.Marker(
				location=[company_data["location"]["latitude"], company_data["location"]["longitude"]],
				tooltip=company,
				popup=Popup('\n'.join(popup_text), max_width=400, min_width=245, id=company_id),
				)
		add_to(marker, marker_cluster, company_id)

	if standalone:
		layer_control = folium.LayerControl()
	else:
		layer_control = MinimapLayerControl()

		m.add_js_link(*folium_layerscontrol_minimap.MinimapLayerControl.default_js[0])

		m.add_js_link(
				"layerscontrol-minimap-js-custom",
				"static/js/L.Control.Layers.Minimap.Toggle.js",
				)

	add_to(layer_control, m, "basemap")

	BasemapFromURL(osm_tiles.tile_name, layer_control).add_to(m)

	return m


def _create_standalone_map() -> None:

	# 3rd party
	from domdf_folium_tools import set_branca_random_seed

	# this package
	from pottery_map.companies import group_pottery_by_company, load_companies
	from pottery_map.pottery import load_pottery_collection

	set_branca_random_seed("WWRD")

	pottery = load_pottery_collection("pottery.toml")
	companies = load_companies("companies.toml")
	pottery_by_company = group_pottery_by_company(pottery, companies)

	m = make_map(pottery_by_company)

	html = m.get_root().render()
	clean_writer(html, sys.stdout)


if __name__ == "__main__":
	_create_standalone_map()
