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
from operator import itemgetter
from typing import Any

# 3rd party
import networkx
from gradpyent import Gradient

# this package
from pottery_map.companies import Companies, _get_item_count

__all__ = ["colour_cycle", "companies_bar_chart", "groups_pie_chart"]

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

	print(company_counts)

	sorted_company_counts = dict(
			sorted(company_counts.items(), key=itemgetter(1), reverse=True) + [("Other", other_count)],
			)

	groups_pie_chart_data = {
			"labels":
					list(sorted_company_counts.keys()),
			"datasets": [{
					"data": list(sorted_company_counts.values()),
					"backgroundColor": colour_cycle,
					"borderColor": "#8b8680",
					"borderWidth": 1,
					}],
			}

	return groups_pie_chart_data


def companies_bar_chart(companies: Companies) -> dict[str, Any]:
	"""
	Returns data for the bar chart showing items per company.

	For a chart powered by ChartJS.

	:param companies:
	"""

	print(companies.company_item_counts)

	sorted_item_counts = dict(sorted(
			companies.company_item_counts.items(),
			key=itemgetter(1),
			reverse=True,
			))

	unique_counts = sorted(set(companies.company_item_counts.values()))
	step = 1 / (len(unique_counts) - 1)
	input_list = [0 + (step * x) for x in range(len(unique_counts))]

	gg = Gradient(gradient_start="#0000FF", gradient_end="#00FF00")
	count_colour_map = dict(zip(unique_counts, gg.get_gradient_series(series=input_list, fmt="html")))

	data = []
	background_colour = []

	for count in sorted_item_counts.values():
		data.append(count)
		background_colour.append(count_colour_map[count])

	companies_bar_chart_data = {
			"labels": list(sorted_item_counts.keys()),
			"datasets": [{
					"data": data,
					"backgroundColor": background_colour,
					"borderColor": "#fff",
					}],
			}

	return companies_bar_chart_data
