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
from random import Random

# 3rd party
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus

__all__ = ["copy_static_files", "make_id", "set_branca_random_seed"]


def set_branca_random_seed(seed: str | int) -> None:
	"""
	Use a fixed random number generator seed for branca (affects element IDs e.g. folium's ``map_{id}``).

	:param seed:
	"""

	# 3rd party
	from branca import element  # nodep

	rand = Random(seed)

	def urandom(size: int) -> bytes:
		return rand.randbytes(size)

	element.urandom = urandom


_id_regex = re.compile("[^0-9a-zA-Z]+")


def make_id(string: str) -> str:
	"""
	Make an ID for an HTML element from the given string.

	:param string:
	"""

	return _id_regex.sub('_', string.lower())


def _copy_file(module: str, filename: str, target_dir: PathPlus) -> None:
	(target_dir / filename).write_text(importlib_resources.read_text(module, filename))


def copy_static_files(static_dir: PathPlus) -> None:
	"""
	Copy CSS and JS files into the given directory.

	:param static_dir:
	"""

	js_dir = static_dir / "js"
	css_dir = static_dir / "css"
	js_dir.maybe_make(parents=True)
	css_dir.maybe_make()

	_copy_file("pottery_map.static", "sidebar.js", js_dir)
	_copy_file("pottery_map.static", "pottery_map.css", css_dir)
	_copy_file("pottery_map.static", "sidebar.css", css_dir)
	_copy_file("pottery_map.static", "style.css", css_dir)
