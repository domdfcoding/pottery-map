#!/usr/bin/env python3
#
#  dashboard.py
"""
Dashboard charts.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from operator import itemgetter
from typing import Any

# 3rd party
import networkx
from gradpyent import Gradient  # type: ignore[import-untyped]

# this package
from pottery_map.companies import Companies, _get_item_count
from pottery_map.pottery import PotteryItem
from pottery_map.templates import render_template

__all__ = [
		"colour_cycle",
		"areas_pie_chart",
		"companies_bar_chart",
		"create_dashboard_page",
		"gradient_for_data",
		"groups_pie_chart",
		"materials_pie_chart",
		"sort_counts",
		"types_bar_chart",
		]

colour_cycle = [
		"blue",
		"green",
		"red",
		"cyan",
		"magenta",
		"yellow",
		"black",
		"purple",
		"pink",
		"brown",
		"orange",
		"teal",
		"coral",
		"lightblue",
		"lime",
		"lavender",
		"turquoise",
		"darkgreen",
		"tan",
		"salmon",
		"gold",
		"lightpurple",
		"darkred",
		"darkblue",
		]


def groups_pie_chart(companies: Companies) -> dict[str, Any]:
	"""
	Returns data for the pie chart showing company groups.

	For a chart powered by ChartJS.

	:param companies: Companies
	"""

	other_count = 0
	company_counts = {}
	for company in companies.top_level_companies:
		ancestors: set[str] = networkx.ancestors(companies.graph, company)
		ancestors.add(company)
		item_count = _get_item_count(companies.company_item_counts, ancestors)
		if item_count > 1:
			company_counts[company] = item_count
		else:
			other_count += item_count

	sorted_company_counts = dict(
			sorted(company_counts.items(), key=itemgetter(1), reverse=True) + [("Other", other_count)],
			)

	labels, data = list(zip(*sorted_company_counts.items()))

	groups_pie_chart_data = {
			"labels":
					labels,
			"datasets": [{
					"data": data,
					"backgroundColor": colour_cycle,
					"borderColor": "#8b8680",
					"borderWidth": 1,
					}],
			}

	return groups_pie_chart_data


def gradient_for_data(
		data: list[float],
		gradient_start: str = "#0000FF",
		gradient_end: str = "#00FF00",
		) -> list[str]:
	"""
	Construct a colour gradient for the given values.

	:param data:
	:param gradient_start:
	:param gradient_end:
	"""

	unique_values = sorted(set(data))

	if len(unique_values) > 1:
		step = 1 / (len(unique_values) - 1)
		input_list = [0 + (step * x) for x in range(len(unique_values))]
	else:
		input_list = [0]

	gg = Gradient(gradient_start=gradient_start, gradient_end=gradient_end)
	count_colour_map = dict(zip(unique_values, gg.get_gradient_series(series=input_list, fmt="html")))

	background_colour = []

	for count in data:
		background_colour.append(count_colour_map[count])

	return background_colour


def sort_counts(counts: Mapping[str, float]) -> tuple[list[str], list[float]]:
	"""
	Sort a dictionary of items and frequencies by the frequency (highest to lowest) and return as two separate lists.

	:param counts:
	"""

	sorted_counts = dict(sorted(
			counts.items(),
			key=itemgetter(1),
			reverse=True,
			))

	labels, data = list(zip(*sorted_counts.items()))
	return list(labels), list(data)


def companies_bar_chart(companies: Companies) -> dict[str, Any]:
	"""
	Returns data for the bar chart showing items per company.

	For a chart powered by ChartJS.

	:param companies:
	"""

	labels, data = sort_counts(companies.company_item_counts)

	companies_bar_chart_data = {
			"labels": labels,
			"datasets": [{
					"data": data,
					"backgroundColor": gradient_for_data(data),
					"borderColor": "#fff",
					}],
			}

	return companies_bar_chart_data


def materials_pie_chart(pottery: list[PotteryItem]) -> dict[str, Any]:
	"""
	Returns data for the pie chart showing materials, such as ``Bone China``.

	For a chart powered by ChartJS.

	:param pottery:
	"""

	materials = []
	for item in pottery:
		material = item.material.strip().strip('?').strip()
		if material:
			materials.append(material)

	labels, data = sort_counts(Counter(materials))

	materials_pie_chart_data = {
			"labels":
					labels,
			"datasets": [{
					"data": data,
					"backgroundColor": colour_cycle,
					"borderColor": "#8b8680",
					"borderWidth": 1,
					}],
			}

	return materials_pie_chart_data


def types_bar_chart(pottery: list[PotteryItem]) -> dict[str, Any]:
	"""
	Returns data for the pie chart showing item types, such as ``Bowl``.

	For a chart powered by ChartJS.

	:param pottery:
	"""

	item_types = []
	for item in pottery:
		item_type = item.type.strip().strip('?').strip()
		if item_type:
			item_types.append(item_type)

	labels, data = sort_counts(Counter(item_types))

	types_bar_chart_data = {
			"labels": labels,
			"datasets": [{
					"data": data,
					"backgroundColor": gradient_for_data(data),
					"borderColor": "#fff",
					}],
			}

	return types_bar_chart_data


def create_dashboard_page(pottery: list[PotteryItem], companies: Companies) -> str:
	"""
	Renders HTML for the dashboard page.

	:param pottery:
	:param companies:
	"""

	return render_template(
			"dashboard.jinja2",
			groups_pie_chart_data=json.dumps(groups_pie_chart(companies)),
			companies_bar_chart_data=json.dumps(companies_bar_chart(companies)),
			materials_pie_chart_data=json.dumps(materials_pie_chart(pottery)),
			areas_pie_chart_data=json.dumps(areas_pie_chart(companies)),
			types_bar_chart_data=json.dumps(types_bar_chart(pottery)),
			all_companies=companies.sorted_company_names,
			)


def areas_pie_chart(companies: Companies) -> dict[str, Any]:
	"""
	Returns data for the pie chart showing areas factories are locted in, such as ``Tunstall``.

	For a chart powered by ChartJS.

	:param companies: Companies
	"""

	areas: dict[str, int] = defaultdict(int)

	for company_name, company_data in companies.companies_data.items():
		area = company_data.get("area", None)
		if area is None:
			continue
		# 	warnings.warn(f"No area specified for {company_name} at {company_data['factory']}")
		# 	area = "Unknown"
		areas[area] += 1

	# labels, data = sort_counts(areas)

	other_count = 0
	for company_name in list(areas.keys()):
		if areas[company_name] < 2:
			other_count += areas.pop(company_name)

	sorted_counts = dict(sorted(areas.items(), key=itemgetter(1), reverse=True) + [("Other", other_count)])

	labels, data = list(zip(*sorted_counts.items()))

	areas_pie_chart_data = {
			"labels":
					labels,
			"datasets": [{
					"data": data,
					"backgroundColor": colour_cycle,
					"borderColor": "#8b8680",
					"borderWidth": 1,
					}],
			}

	return areas_pie_chart_data
