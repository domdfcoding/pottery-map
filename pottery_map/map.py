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
from typing import Any

# 3rd party
import folium
from folium.plugins import MarkerCluster

__all__ = ["make_map"]


def make_map(pottery_by_company: dict[str, Any]) -> folium.Map:
	"""
	Map the pottery collection folium map.

	:param pottery_by_company:
	"""

	m = folium.Map(location=(53.02445128825057, -2.1834733161173445), font_size="16px")
	m.add_css_link("pottery_map.css", "./static/css/pottery_map.css")

	marker_cluster = MarkerCluster(options={"maxClusterRadius": 50}).add_to(m)

	for company, company_data in pottery_by_company.items():

		if "location" not in company_data or not company_data["location"]:
			continue

		popup_text = f"""
<div class="item-details">
<h2>{company}</h2>
<h3><strong>{company_data['factory']}</strong></h3>
		"""

		for item in company_data["items"]:

			popup_text += f"""
<ul>
	<li>{item['design']}</li>
	<li>{item['type']} {item['item']}</li>
	<li>{item['era']}</li>
</ul>
<img class="pottery-image" src="{item['photo_url']}" />
	"""

		popup_text += "</div>"

		folium.Marker(
				location=[company_data["location"]["latitude"], company_data["location"]["longitude"]],
				tooltip=company,
				popup=folium.Popup(popup_text, max_width=400, min_width=245),
				).add_to(marker_cluster)

	return m
