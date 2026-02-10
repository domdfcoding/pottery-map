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
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import clean_writer
from folium.template import Template

# this package
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


class Map(folium.Map):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._id = "pottery"


def _make_link(company: str, inner: str, item: str | None = None, standalone: bool = True) -> str:
	if standalone:
		return inner

	if not item:
		return f'<a href="companies/{make_id(company)}.html">{inner}</a>'

	return f'<a href="companies/{make_id(company)}.html#{item}">{inner}</a>'


def make_map(pottery_by_company: dict[str, Any], standalone: bool = True) -> Map:
	"""
	Map the pottery collection folium map.

	:param pottery_by_company:
	:param standalone: Create a standalone map with embedded CSS,
	"""

	m = Map(location=(53.02445128825057, -2.1834733161173445), font_size="16px")

	if standalone:
		embed_styles(m)
	else:
		m.add_css_link("pottery_map.css", "./static/css/pottery_map.css")

	m.add_js_link(
			"markerclusterjs",
			"https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/leaflet.markercluster.js",
			)

	marker_cluster = MarkerCluster(options={"maxClusterRadius": 50}).add_to(m)

	for company, company_data in pottery_by_company.items():

		if "location" not in company_data or not company_data["location"]:
			continue

		popup_text = ['<div class="item-details">']
		popup_text.append(_make_link(company, inner=f"<h2>{company}</h2>", standalone=standalone))
		popup_text.append(f"<h3><strong>{company_data['factory']}</strong></h3>")

		for item in company_data["items"]:

			item_link = _make_link(
					company,
					item=item["id"],
					inner=f"<li>{item['design']}</li>",
					standalone=standalone,
					)

			popup_text.append(
					f"""
<ul>
	{item_link}
	<li>{item['type']} {item['item']}</li>
	<li>{item['era']}</li>
</ul>
<img class="pottery-image" src="{item['photo_url']}" />
	""",
					)

		popup_text.append("</div>")

		folium.Marker(
				location=[company_data["location"]["latitude"], company_data["location"]["longitude"]],
				tooltip=company,
				popup=folium.Popup('\n'.join(popup_text), max_width=400, min_width=245),
				).add_to(marker_cluster)

	return m


def _create_standalone_map() -> None:

	# this package
	from pottery_map import load_pottery_collection
	from pottery_map.companies import group_pottery_by_company, load_companies
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
