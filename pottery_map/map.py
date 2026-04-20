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
from collections.abc import Iterable

# 3rd party
import folium
import folium.plugins
from domdf_folium_tools import embed_styles
from domdf_folium_tools.elements import add_to, set_id
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import clean_writer
from folium.utilities import escape_backticks
from folium_layerscontrol_minimap.toggle import ToggleMinimapLayerControl
from folium_map_search import MapSearchControl, MapSearchProvider
from folium_zoom_state import BasemapFromURL, ZoomStateJS, ZoomStateMap

# this package
from pottery_map.companies import CompanyItems
from pottery_map.nls_basemaps import os10k, os25inch, os1250, os2500
from pottery_map.templates import render_template
from pottery_map.utils import make_id

__all__ = ["make_map"]


class Map(ZoomStateMap):

	# Remove outdated bootstrap and unused glyphicons and awesome markers

	default_js = [
			("leaflet", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"),
			("jquery", "https://code.jquery.com/jquery-3.7.1.min.js"),
			]

	default_css = [
			("leaflet_css", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"),
			]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_id(self, "pottery")


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


def make_map(pottery_collection: Iterable[CompanyItems], standalone: bool = True) -> Map:
	"""
	Make the pottery collection folium map.

	:param pottery_collection:
	:param standalone: Create a standalone map with embedded CSS,
	"""

	MAX_ZOOM = 20

	osm_tiles = set_id(
			folium.TileLayer(
					tiles="OpenStreetMap",
					name="OpenStreetMap",
					show=False,
					max_zoom=MAX_ZOOM,
					max_native_zoom=19,
					referrerPolicy="strict-origin-when-cross-origin",
					),
			"osm_carto",
			)

	m = Map(
			location=(53.02445128825057, -2.1834733161173445),
			font_size="16px",
			tiles=osm_tiles,
			maxZoom=MAX_ZOOM,
			wheelPxPerZoomLevel=80,
			)

	set_id(os10k, "os10k").add_to(m)
	set_id(os1250, "os1250").add_to(m)
	set_id(os2500, "os2500").add_to(m)
	set_id(os25inch, "os25inch").add_to(m)
	# TODO: use these IDs in the url rather than the long, space-filled, human-readable name

	ZoomStateJS(setup_basemap_state=True).add_to(m)

	if standalone:
		embed_styles(m, importlib_resources.read_text("pottery_map.static", "pottery_map.css"))
	else:
		m.add_css_link("pottery_map.css", "./static/css/pottery_map.css")

	marker_cluster = add_to(
			folium.plugins.MarkerCluster(options={"maxClusterRadius": 50}, control=False),
			m,
			"collection",
			)

	for company_data in pottery_collection:
		company = company_data.company
		if not company.location:
			continue

		popup_text = render_template(
				"map_popup.jinja2",
				company_data=company_data,
				standalone=standalone,
				make_id=make_id,
				).splitlines()

		company_id = make_id(company.name)

		marker = folium.Marker(
				location=[company.location["latitude"], company.location["longitude"]],
				tooltip=company.name,
				popup=Popup('\n'.join(popup_text), max_width=400, min_width=245, id=company_id),
				search_name=company.name,
				)
		add_to(marker, marker_cluster, company_id)

	if standalone:
		layer_control = folium.LayerControl()
	else:
		layer_control = ToggleMinimapLayerControl()

	add_to(layer_control, m, "basemap")

	BasemapFromURL(osm_tiles.tile_name, layer_control).add_to(m)
	# TODO: about dialog
	MapSearchControl(
			provider=MapSearchProvider(layer=marker_cluster, map=m, feature_type="settlement"),
			auto_complete_delay=1000,  # Effectively turns off autocomplete to comply with Nominatum TOS
			show_marker=False,
			max_suggestions=15,
			search_label="Enter town or manufacturer name",
			disable_enter_search=True,  # Otherwise markers don't appear 🤷
			close_on_submit=True,
			).add_to(m)

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

	m = make_map(pottery_by_company.values())
	m.add_css_link("bootstrap_css", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css")
	m.add_js_link("bootstrap_js", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js")

	html = m.get_root().render()
	clean_writer(html, sys.stdout)


if __name__ == "__main__":
	_create_standalone_map()
