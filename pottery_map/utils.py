#!/usr/bin/env python3
#
#  utils.py
"""
Utility functions.
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
import re
from collections import defaultdict
from collections.abc import Callable, Collection, Iterable
from typing import TYPE_CHECKING, TypeVar

# 3rd party
import domdf_folium_tools.static_files
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike

if TYPE_CHECKING:
	# this package
	from pottery_map.pottery import PotteryItem

__all__ = ["copy_static_files", "filter_keys", "get_photo_path", "groupby", "make_id", "normalise_category"]

_id_regex = re.compile("[^0-9a-zA-Z]+")


def make_id(string: str) -> str:
	"""
	Make an ID for an HTML element from the given string.

	:param string:
	"""

	return _id_regex.sub('_', string.lower())


def copy_static_files(static_dir: PathPlus) -> None:
	"""
	Copy CSS and JS files into the given directory.

	:param static_dir:
	"""

	domdf_folium_tools.static_files.copy_static_files(
			static_dir=static_dir,
			js_files=[
					domdf_folium_tools.static_files.PythonResource("pottery_map.static", "sidebar.js"),
					domdf_folium_tools.static_files.PythonResource("pottery_map.static", "dashboard.js"),
					],
			css_files=[
					domdf_folium_tools.static_files.PythonResource("pottery_map.static", "pottery_map.css"),
					domdf_folium_tools.static_files.PythonResource("pottery_map.static", "sidebar.css"),
					domdf_folium_tools.static_files.PythonResource("pottery_map.static", "style.css"),
					],
			)


_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def groupby(iterable: Iterable[_T1], key: Callable[[_T1], _T2]) -> dict[_T2, list[_T1]]:
	"""
	Group the given items using the given key function.

	Like :func:`itertools.groupby` but returns a dictionary with list values instead.

	:param iterable:
	:param key:
	"""

	keyfunc = (lambda x: x) if key is None else key

	grouper: dict[_T2, list[_T1]] = defaultdict(list)

	for value in iter(iterable):
		curr_key = keyfunc(value)
		grouper[curr_key].append(value)

	return dict(grouper)


def normalise_category(category: str) -> str:
	"""
	Normalise a category name.

	:param category:
	"""

	category = category.lower()
	if category != "other":
		category += 's'

	return category.title()


KT = TypeVar("KT")
VT = TypeVar("VT")


def filter_keys(
		dictionary: dict[KT, VT],
		keep_keys: Collection[KT] = (),
		remove_keys: Collection[KT] = (),
		) -> dict[KT, VT]:
	"""
	Filter dictionaries by key.

	:param dictionary:
	:param keep_keys:
	:param remove_keys:
	"""

	new_dict: list[tuple[KT, VT]] = []

	for key, value in dictionary.items():
		if keep_keys:
			if key not in keep_keys:
				continue

		if remove_keys:
			if key in remove_keys:
				continue

		new_dict.append((key, value))

	return dict(new_dict)


def get_photo_path(pottery_item: "PotteryItem", fileystem_path: PathLike) -> PathPlus:
	"""
	Returns the filesystem path (in the output directory) for the given item and image.

	:param pottery_item:
	:param fileystem_path: Path to the image.
	"""

	return PathPlus("images") / pottery_item.id / PathPlus(fileystem_path).name
