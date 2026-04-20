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

# TODO: notes and links for the company itself (including to thepotteries.org and Wikipedia where available)

# stdlib
import warnings
from collections.abc import Iterable
from dataclasses import dataclass

# 3rd party
import dom_toml
import networkx
from domdf_python_tools.typing import PathLike

# this package
from pottery_map.company import Company, CompanyData, CompanyItems
from pottery_map.pottery import PotteryItem

__all__ = ["Companies", "group_pottery_by_company", "load_companies", "make_successor_network"]

# TODO: include ultimate (i.e. current) parent. E.g. J&G Meakin is now Wedgwood/WWRD.


def load_companies(companies_file: PathLike = "companies.toml") -> dict[str, Company]:
	"""
	Load company data (name, factory, location) from file.

	:param companies_file:
	"""

	companies: dict[str, Company] = {}
	existing_coordinates = []
	company_data: CompanyData

	for company_name, company_data in dom_toml.load(companies_file).items():
		if "location" in company_data:
			if company_data["location"] in existing_coordinates:
				warnings.warn(f"Multiple factories at location {company_data['location']!r}")
			existing_coordinates.append(company_data["location"])

		companies[company_name] = Company.from_toml_dict(company_name, **company_data)

	return companies


def group_pottery_by_company(
		pottery: list[PotteryItem],
		companies: dict[str, Company],
		) -> dict[str, CompanyItems]:
	"""
	Group items in the pottery collection by the company who made them.

	:param pottery: The pottery collection.
	:param companies: Data about companies, giving factory locations.
	"""

	pottery_by_company: dict[str, CompanyItems] = {}

	for item in pottery:
		company_name = item.company.name
		if company_name not in pottery_by_company:
			if company_name in companies:
				company = companies[company_name]
			else:
				# "Ad-hoc" company that only exists in pottery.toml, not in companies.toml
				company = item.company

			pottery_by_company[company_name] = CompanyItems(company, [])

		pottery_by_company[company_name].add_item(item)

	for company_name, company in companies.items():
		if company_name not in pottery_by_company:
			pottery_by_company[company_name] = CompanyItems(company, [])

	return pottery_by_company


def make_successor_network(companies: dict[str, Company]) -> networkx.DiGraph:
	"""
	Make a graph of relationships betweenn companies and their successors/parents.

	:param companies:
	"""

	graph: networkx.DiGraph = networkx.DiGraph()

	for company_name, company in companies.items():
		graph.add_node(company_name)
		if company.successor:
			graph.add_node(company.successor)
			graph.add_edge(company_name, company.successor)

	return graph


def _get_item_count(company_item_counts: dict[str, int], successors: Iterable[str]) -> int:
	return sum([company_item_counts.get(x, 0) for x in successors])


@dataclass
class Companies:
	"""
	Helper class for companies in the collection.
	"""

	#: Graph showing relationships between companies.
	graph: networkx.DiGraph

	#: Mapping of all company names to the company objects and items made by the company (if any).
	pottery_by_company: dict[str, CompanyItems]

	@classmethod
	def from_raw_data(cls, pottery: list, companies: dict[str, Company]) -> "Companies":
		"""

		:param pottery: The pottery collection.
		:param companies: Data about companies, giving factory locations.
		"""

		graph = make_successor_network(companies)
		pottery_by_company = group_pottery_by_company(pottery, companies)

		# Check no extra companies have snuck into or escaped from the graph
		all_companies: set[str] = {*graph.nodes(), *pottery_by_company}
		assert not all_companies.difference(pottery_by_company)
		assert all_companies == set(pottery_by_company)

		return cls(
				graph=graph,
				pottery_by_company=pottery_by_company,
				)

	@property
	def sorted_company_names(self) -> list[str]:
		"""
		Sorted list of the companies' names.
		"""

		return sorted(self.pottery_by_company)

	@property
	def company_item_counts(self) -> dict[str, int]:
		"""
		Mapping of company names to the number of items by that company in the collecton.
		"""

		company_item_counts: dict[str, int] = {}

		for company_name, company_data in self.pottery_by_company.items():
			company_item_counts[company_name] = len(company_data.items)

		return company_item_counts

	@property
	def top_level_companies(self) -> list[str]:
		"""
		List of top level companies (those with no successors, e.g. Churchill China).
		"""

		return [x for x in self.graph.nodes() if self.graph.out_degree(x) == 0]

	@property
	def represented_companies(self) -> list[str]:
		"""
		List of companies represented in the collection.
		
		Excludes successors for which metadata exists but no items of theirs are in the collection.
		"""

		return [k for k, v in self.company_item_counts.items() if v > 0]
