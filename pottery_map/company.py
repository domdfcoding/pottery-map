#!/usr/bin/env python3
#
#  company.py
"""
Class to represent a company.
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

# stdlib
from typing import TYPE_CHECKING, NamedTuple

# 3rd party
import attrs
from domdf_folium_tools import Coordinates
from typing_extensions import NotRequired, Required, TypedDict

if TYPE_CHECKING:
	# this package
	from pottery_map.pottery import PotteryItem

__all__ = ["Company", "CompanyData", "CompanyItems"]

# this package


@attrs.define
class Company:
	"""
	A pottery manufacturer represented in the collection.
	"""

	name: str
	factory: str = "Unknown"
	# TODO: notes: list[str] = attrs.field(factory=list)
	# TODO: links: dict[str, str] = attrs.field(factory=dict)
	location: Coordinates | None = None
	area: str | None = None  # E.g. "Hanley", "Longton", "Czechosolvakia", "Chesterfield", "Jingdezhen"
	successor: str | None = None
	defunct: bool = False

	@classmethod
	def from_toml_dict(
			cls,
			name: str,
			**data,
			) -> "Company":
		r"""
		Create from a table in a TOML file.

		:param name: The company name.
		:param \*\*data:
		"""

		return cls(
				name=name,
				**data,
				)


class CompanyItems(NamedTuple):
	"""
	A company and the items made by it.
	"""

	company: Company
	items: list["PotteryItem"]

	def add_item(self, item: "PotteryItem") -> None:
		"""
		Add an item to ``.items``.

		:param item:
		"""

		self.items.append(item)


class CompanyData(TypedDict):
	"""
	A company and the items made by it.
	"""

	factory: Required[str]
	location: Required[Coordinates | None]
	successor: Required[str | None]
	defunct: Required[bool]
	area: NotRequired[str | None]
	items: NotRequired[list["PotteryItem"]]
