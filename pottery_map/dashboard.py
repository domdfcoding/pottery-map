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
from collections import Counter
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
		"companies_bar_chart",
		"create_dashboard_page",
		"groups_pie_chart",
		"materials_pie_chart",
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

	:param companies:
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
			types_bar_chart_data=json.dumps(types_bar_chart(pottery)),
			all_companies=companies.sorted_company_names,
			)
