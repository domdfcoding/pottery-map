#!/usr/bin/env python3
#
#  pottery.py
"""
Classes to represent pottery collection.
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

# 3rd party
import attrs
import dom_toml
from domdf_python_tools.typing import PathLike

# this package
from pottery_map.types import Coordinates, PotteryData
from pottery_map.utils import make_id

__all__ = ["PotteryItem", "load_pottery_collection"]


@attrs.define
class PotteryItem:
	"""
	An item in the pottery collection.
	"""

	id: str
	company: str
	material: str  # E.g. "Bone China"
	type: str  # E.g. "Sandwich Plate"
	design: str
	factory: str = "Unknown"
	designer: str = ''
	category: str = "Other"  # E.g. "Plate", "Bowl", "Cup"
	era: str = ''
	notes: list[str] = attrs.field(factory=list)
	photo_urls: list[str] = attrs.field(factory=list)
	location: Coordinates | None = None
	area: str | None = None  # E.g. "Hanley", "Longton", "Czechosolvakia", "Chesterfield", "Jingdezhen"
	successor: str | None = None
	defunct: bool = False

	@classmethod
	def from_toml_dict(
			cls,
			id: str,  # noqa: A002  # pylint: disable=redefined-builtin
			**data,
			) -> "PotteryItem":
		r"""
		Create from a table in a TOML file.

		:param id: Unique identifier for the item.
		:param \*\*data:
		"""

		return cls(
				id=make_id(id),
				**data,
				)

	def get_item_data(self) -> PotteryData:
		"""
		Returns data about the item but not where it was made.
		"""

		return {
				"id": self.id,
				"material": self.material,
				"type": self.type,
				"design": self.design,
				"designer": self.designer,
				"category": self.category,
				"era": self.era,
				"notes": self.notes,
				"photo_urls": self.photo_urls,
				}


def load_pottery_collection(pottery_file: PathLike = "pottery.toml") -> list[PotteryItem]:
	"""
	Load a pottery collection from a TOML file.

	:param pottery_file:
	"""

	pottery = []
	for item_id, item in dom_toml.load(pottery_file).items():
		pottery.append(PotteryItem.from_toml_dict(item_id, **item))

	return pottery
