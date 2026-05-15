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
from domdf_folium_tools.elements import add_to, set_id
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus, clean_writer
from folium.template import Template
from folium.utilities import escape_backticks
from folium_bottom_sheet import BottomSheetDialog
from folium_layercontrols.minimap.toggle import ToggleMinimapLayerControl
from folium_layercontrols.toggle import ToggleLayerControl
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
			# ("jquery", "https://code.jquery.com/jquery-3.7.1.min.js"),
			]

	default_css = [
			("leaflet_css", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"),
			]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_id(self, "pottery")


class PopupResizeMonitor(folium.MacroElement):
	"""
	Monitors the browser window for resizes and dismisses popups if going into "small screen" mode.

	This avoids the popup becoming malformed when reducing its width below what leaflet originally set it to.
	"""

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
		{{ this._parent.get_name() }}.on('click', bottomSheetDialog.close, bottomSheetDialog);
		PopupResizeMonitor({{ this._parent.get_name() }});
		{% endmacro %}

	""",
			)


class Popup(folium.Popup):
	"""
	Heavily customised folium popup that displays either a popup or the bottom sheet depending on the screen size.
	"""

	_template = Template(
			"""
		var {{this.get_name()}}_popup = L.popup({{ this.options|tojavascript }});

		var {{this.get_name()}} = new PopupOrBottomSheet(
			marker={{ this._parent.get_name() }},
			content=`{{ this.popup_content }}`,
			popup={{this.get_name()}}_popup,
		);

		{{this.get_name()}}.switch();
		{% if this.show %}{{this.get_name()}}.show(){% endif %}


		{% for name, element in this.script._children.items() %}
			{{element.render()}}
		{% endfor %}
	""".replace('\t', "    "),
			)

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

		assert not kwargs.get("lazy", False)

		super().__init__(html=html_element, max_width=max_width, min_width=min_width, **kwargs)
		self._id = id

		self.popup_content = html


class EmbeddedCSSJS(folium.MacroElement):
	"""
	Embed the map's custom CSS and JavaScript into the HTML.

	:param custom_css: CSS as a string.
	:param custom_js: JavaScript as a string.
	"""

	_template = Template(
			"""
			{% macro header(this, kwargs) %}
				<style>
					{{ this.custom_css }}
				</style>
			{% endmacro %}

			{% macro script(this, kwargs) %}
				{{ this.custom_js }}
			{% endmacro %}
	""",
			)

	def __init__(self, custom_css: str = '', custom_js: str = ''):
		super().__init__()
		self._name = "EmbeddedCSSJS"
		self.custom_css = custom_css
		self.custom_js = custom_js


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
		EmbeddedCSSJS(
				custom_css=importlib_resources.read_text("pottery_map.static", "pottery_map.css"),
				custom_js=importlib_resources.read_text("pottery_map.static", "map_popup.js"),
				).add_to(m)
	else:
		m.add_css_link("pottery_map.css", "./static/css/pottery_map.css")
		m.add_js_link("map-popup-js", "./static/js/map_popup.js")

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
				# popup=Popup('\n'.join(popup_text), max_width=400, min_width=245, id=company_id),
				popup=Popup(
						'\n'.join(popup_text),
						min_width=285,
						id=company_id,
						class_name="pottery-map-popup",
						autoPanPaddingTopLeft=[45, 0],
						autoPanPaddingBottomRight=[65, 0],
						),
				search_name=company.name,
				)
		add_to(marker, marker_cluster, company_id)

	layer_control: folium.LayerControl
	if standalone:
		layer_control = ToggleLayerControl()
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
	PopupResizeMonitor().add_to(m)
	BottomSheetDialog().add_to(m)

	return m


def _create_standalone_map(input_directory: PathPlus) -> str:

	# this package
	from pottery_map.companies import group_pottery_by_company, load_companies
	from pottery_map.pottery import load_pottery_collection

	pottery = load_pottery_collection(input_directory / "pottery.toml")
	companies = load_companies(input_directory / "companies.toml")
	pottery_by_company = group_pottery_by_company(pottery, companies)

	m = make_map(pottery_by_company.values())
	m.add_css_link("bootstrap_css", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css")
	m.add_js_link("bootstrap_js", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js")

	return m.get_root().render()


if __name__ == "__main__":
	# 3rd party
	from domdf_folium_tools import set_branca_random_seed

	set_branca_random_seed("WWRD")

	clean_writer(_create_standalone_map(PathPlus()), sys.stdout)
