#!/usr/bin/env python3
#
#  companies.py
"""
Function for loading data about companies.
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
import warnings
from dataclasses import dataclass
from typing import Any
from collections.abc import Iterable

# 3rd party
import dom_toml
import networkx
from domdf_python_tools.typing import PathLike

# this package
from pottery_map.templates import render_template

__all__ = ["group_pottery_by_company", "load_companies", "make_company_pages", "make_successor_network"]

# TODO: include ultimate (i.e. current) parent. E.g. J&G Meakin is now Wedgwood/WWRD.


def load_companies(companies_file: PathLike = "companies.toml") -> dict[str, Any]:
	"""
	Load company data (name, factory, location) from file.

	:param companies_file:
	"""

	companies = {}
	existing_coordinates = []
	company_data: dict
	for company_name, company_data in dom_toml.load(companies_file).items():
		if "location" in company_data:
			if company_data["location"] in existing_coordinates:
				warnings.warn(f"Multiple factories at location {company_data['location']!r}")
			existing_coordinates.append(company_data["location"])
		company_data.setdefault("factory", "Unknown")
		company_data.setdefault("location", None)
		companies[company_name] = company_data

	return companies


# TODO: TypedDict etc.
def group_pottery_by_company(pottery: list, companies: dict[str, Any]) -> dict[str, Any]:
	"""
	Group items in the pottery collection by the company who made them.

	:param pottery: The pottery collection.
	:param companies: Data about companies, giving factory locations.
	"""

	pottery_by_company = {}

	for item in pottery:
		new_item = dict(item)
		company = new_item.pop("company")
		if company not in pottery_by_company:
			if company in companies:
				factory = companies[company]["factory"]
				location = companies[company]["location"]
				successor = companies[company].get("successor")
			else:
				factory = new_item.get("factory", "Unknown")
				location = new_item.get("location")
				successor = new_item.get("successor")
			pottery_by_company[company] = {
					"items": [],
					"factory": factory,
					"location": location,
					"successor": successor,
					}

		if "location" in new_item:
			del new_item["location"]
		if "factory" in new_item:
			del new_item["factory"]
		if "successor" in new_item:
			del new_item["successor"]

		pottery_by_company[item["company"]]["items"].append(new_item)

	return pottery_by_company


def make_successor_network(companies: dict[str, Any]) -> networkx.DiGraph:
	"""
	Make a graph of relationships betweenn companies and their successors/parents.

	:param companies:
	"""

	graph: networkx.DiGraph = networkx.DiGraph()

	for company, company_data in companies.items():
		successor = company_data.get("successor")
		graph.add_node(company)
		if successor:
			graph.add_node(successor)
			graph.add_edge(company, successor)

	return graph


def _get_item_count(company_item_counts: dict[str, int], successors: Iterable[str]) -> int:
	return sum([company_item_counts.get(x, 0) for x in successors])


@dataclass
class Companies:
	#: Graph showing relationships between companies.
	graph: networkx.DiGraph

	#: The names of all companies.
	all_companies: set[str]

	companies_data: dict[str, Any]

	pottery_by_company: dict[str, Any]

	@classmethod
	def from_raw_data(cls, pottery: list, companies: dict[str, Any]) -> "Companies":
		"""

		:param pottery: The pottery collection.
		:param companies: Data about companies, giving factory locations.
		"""

		graph = make_successor_network(companies)
		pottery_by_company = group_pottery_by_company(pottery, companies)
		all_companies: set[str] = {*graph.nodes(), *pottery_by_company}
		return cls(
				graph=graph,
				all_companies=all_companies,
				companies_data=companies,
				pottery_by_company=pottery_by_company,
				)

	@property
	def sorted_company_names(self) -> list[str]:
		return sorted(self.all_companies)

	@property
	def company_item_counts(self) -> dict[str, int]:
		company_item_counts: dict[str, int] = {}

		for company, company_data in self.pottery_by_company.items():
			company_item_counts[company] = len(company_data["items"])

		return company_item_counts

	@property
	def top_level_companies(self) -> list[str]:
		return [x for x in self.graph.nodes() if self.graph.out_degree(x) == 0]


def make_company_pages(companies: Companies) -> tuple[str, dict[str, str]]:
	"""
	Create pages listing all items made by the company, and an index of all companies.

	:param companies:
	"""

	pages = {}

	for company in companies.all_companies:
		if company in companies.pottery_by_company:
			company_data = companies.pottery_by_company[company]
		else:
			company_data = {"items": [], **companies.companies_data[company]}

		pages[company] = render_template(
				"company_page.jinja2",
				company=company,
				factory=company_data["factory"],
				location=company_data["location"],
				items=company_data["items"],
				all_companies=companies.sorted_company_names,
				)

	index_page = render_template(
			"company_index.jinja2",
			company_item_counts=companies.company_item_counts,
			top_level_companies=companies.top_level_companies,
			all_companies=companies.sorted_company_names,
			graph=companies.graph,
			get_item_count=_get_item_count,
			)

	return index_page, pages
