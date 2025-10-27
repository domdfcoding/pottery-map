# stdlib
import warnings
from typing import Any

# 3rd party
import dom_toml


def load_companies() -> dict[str, Any]:
	companies = {}
	existing_coordinates = []
	for company_name, company_data in dom_toml.load("companies.toml").items():
		if company_data["location"] in existing_coordinates:
			warnings.warn(f"Multiple factories at location {company_data['location']!r}")
		existing_coordinates.append(company_data["location"])
		companies[company_name] = company_data

	return companies
