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
from typing import Any

# 3rd party
import dom_toml
from domdf_python_tools.typing import PathLike

__all__ = ["load_companies"]

# TODO: include ultimate (i.e. current) parent. E.g. J&G Meakin is now Wedgwood/WWRD.


def load_companies(companies_file: PathLike = "companies.toml") -> dict[str, Any]:
	"""
	Load company data (name, factory, location) from file.

	:param companies_file:
	"""

	companies = {}
	existing_coordinates = []
	for company_name, company_data in dom_toml.load(companies_file).items():
		if company_data["location"] in existing_coordinates:
			warnings.warn(f"Multiple factories at location {company_data['location']!r}")
		existing_coordinates.append(company_data["location"])
		companies[company_name] = company_data

	return companies
