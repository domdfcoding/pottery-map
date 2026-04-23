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

# stdlib
from urllib.parse import urlparse

# 3rd party
import attrs
import dom_toml
from domdf_python_tools.typing import PathLike

# this package
from pottery_map.company import Company
from pottery_map.utils import filter_keys, get_photo_path, make_id

__all__ = ["PotteryItem", "load_pottery_collection"]


@attrs.define
class PotteryItem:
	"""
	An item in the pottery collection.
	"""

	# TODO: move company parts into an instance of the Company class.

	id: str

	#: Used as the table name in ``pottery.toml``.
	toml_id: str

	company: Company
	material: str  # E.g. "Bone China"
	type: str  # E.g. "Sandwich Plate"
	design: str
	designer: str = ''
	category: str = "Other"  # E.g. "Plate", "Bowl", "Cup"
	era: str = ''
	notes: list[str] = attrs.field(factory=list)
	links: dict[str, str] = attrs.field(factory=dict)
	photo_paths: list[str] = attrs.field(factory=list)
	diameter: str | None = None

	@property
	def description(self) -> str:
		"""
		A description of the item, including its material, diameter (if applicable), and type (e.g. plate).

		E.g. ``bone china 12 cm plate``.
		"""

		parts = []

		for part in [
				self.material,
				self.diameter,
				self.type,
				]:
			if part:
				assert isinstance(part, str)
				part = part.strip()
				parts.append(part)

		return ' '.join(parts)

	def get_photo_urls(self, root: str = '') -> list[str]:
		"""
		Returns the list of photo URLs with parameters substituted.

		:param root: URL path to the website root.
		"""

		# TODO: copy files (maybe converting to webp or avif) from the photo_url path (if not a URL) and put into subfolder of images folder with same ID as the item (filename itself stays the same)

		photo_urls = []

		for path in self.get_substituted_photo_paths():
			parts = urlparse(path)
			if parts.scheme and parts.netloc:
				# It's a URL
				photo_urls.append(path)
			else:
				# Local filesystem path; will be copied into images/{id}
				photo_urls.append(f"{root}{get_photo_path(self, path)}")

		return photo_urls

	def get_substituted_photo_paths(self) -> list[str]:
		"""
		Returns a list of photo paths after parameter substitution.
		"""

		photo_paths = []
		params = attrs.asdict(self)
		params.pop("photo_paths")

		for path in self.photo_paths:
			path = (path.format_map(params))
			photo_paths.append(path.strip())

		return photo_paths

	@property
	def has_notes(self) -> bool:
		"""
		Returns whether the item, or its company, has any notes or links.
		"""

		return any([self.notes, self.links, self.company.has_notes])

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

		company_arg_names = {"factory", "location", "area", "successor", "defunct"}
		company_data = filter_keys(data, keep_keys=company_arg_names)
		company = Company(name=data["company"], **company_data)

		data = filter_keys(data, remove_keys={"company", *company_arg_names})

		return cls(
				id=make_id(id),
				toml_id=id,
				company=company,
				**data,
				)


def load_pottery_collection(pottery_file: PathLike = "pottery.toml") -> list[PotteryItem]:
	"""
	Load a pottery collection from a TOML file.

	:param pottery_file:
	"""

	pottery = []
	for item_id, item in dom_toml.load(pottery_file).items():
		pottery.append(PotteryItem.from_toml_dict(item_id, **item))

	return pottery
