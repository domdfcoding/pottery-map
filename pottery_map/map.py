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
from typing import Any, TypeVar

# 3rd party
import folium
import folium.plugins
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import clean_writer
from folium.template import Template
from folium.utilities import escape_backticks
from folium_zoom_state import ZoomStateJS, ZoomStateMap

# this package
from pottery_map.templates import render_template
from pottery_map.utils import make_id

__all__ = ["make_map"]


def embed_styles(m: folium.Map) -> folium.Element:
	"""
	Embed the map's custom CSS into the HTML.

	:param m:
	"""

	css_content = importlib_resources.read_text("pottery_map.static", "pottery_map.css")

	class EmbeddedStyles(folium.MacroElement):
		_template = Template(
				f"""
			{{% macro header(this, kwargs) %}}
				<style>
					{css_content}
				</style>
			{{% endmacro %}}
	""",
				)

	return EmbeddedStyles().add_to(m)


class MarkerCluster(folium.plugins.MarkerCluster):
	default_js = []


class Map(ZoomStateMap):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._id = "pottery"


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


_E = TypeVar("_E", bound=folium.Element)


def _add_to(
		element: _E,
		parent: folium.Element,
		id: str,  # noqa: A002  # pylint: disable=redefined-builtin
		) -> _E:
	element._id = id
	element.add_to(parent)
	return element


def make_map(pottery_by_company: dict[str, Any], standalone: bool = True) -> Map:
	"""
	Map the pottery collection folium map.

	:param pottery_by_company:
	:param standalone: Create a standalone map with embedded CSS,
	"""

	m = Map(location=(53.02445128825057, -2.1834733161173445), font_size="16px")

	ZoomStateJS().add_to(m, embed_script=standalone)

	if standalone:
		embed_styles(m)
	else:
		m.add_css_link("pottery_map.css", "./static/css/pottery_map.css")
		m.add_js_link("zoom_state.js", "static/js/zoom_state.js")

	m.add_js_link(
			"markerclusterjs",
			"https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/leaflet.markercluster.js",
			)

	marker_cluster = _add_to(MarkerCluster(options={"maxClusterRadius": 50}), m, id="collection")

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
		_add_to(marker, marker_cluster, id=company_id)

	return m


def _create_standalone_map() -> None:

	# this package
	from pottery_map.companies import group_pottery_by_company, load_companies
	from pottery_map.pottery import load_pottery_collection
	from pottery_map.utils import set_branca_random_seed

	set_branca_random_seed("WWRD")

	pottery = load_pottery_collection("pottery.toml")
	companies = load_companies("companies.toml")
	pottery_by_company = group_pottery_by_company(pottery, companies)

	m = make_map(pottery_by_company)

	html = m.get_root().render()
	clean_writer(html, sys.stdout)


if __name__ == "__main__":
	_create_standalone_map()
