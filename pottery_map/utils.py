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
import shutil
from collections import defaultdict
from collections.abc import Callable, Collection, Iterable
from hashlib import sha256
from typing import TYPE_CHECKING, TypeVar

# 3rd party
import domdf_folium_tools.static_files
import tqdm
from consolekit.terminal_colours import Fore
from domdf_python_tools.paths import PathPlus, TemporaryPathPlus
from domdf_python_tools.typing import PathLike
from PIL import Image

if TYPE_CHECKING:

	# this package
	from pottery_map.pottery import PotteryItem

__all__ = [
		"FileModifications",
		"ProgressBar",
		"copy_static_files",
		"filter_keys",
		"get_photo_path",
		"get_sha256_hash",
		"groupby",
		"make_id",
		"normalise_category",
		]

_id_regex = re.compile("[^0-9a-zA-Z]+")

IMG_WIDTH = 960
IMG_HEIGHT = 720


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
					domdf_folium_tools.static_files.PythonResource("pottery_map.static", "items_search.js"),
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

	file_name = PathPlus(fileystem_path).stem + f"_{IMG_WIDTH}px"
	return (PathPlus("images") / pottery_item.id / file_name).with_suffix(".webp")


def _convert_image(src_path: PathPlus, dst_path: PathPlus) -> float:
	img = Image.open(src_path)
	img_ratio = img.width / img.height
	img.resize((IMG_WIDTH, IMG_HEIGHT)).save(dst_path)

	return img_ratio


def get_sha256_hash(filename: PathLike, blocksize: int = 1 << 20) -> str:
	"""
	Returns the SHA256 hash hexdigest for the given file.

	:param filename:
	:param blocksize: The blocksize to read the file with.
	"""

	with open(filename, "rb") as fp:
		hash_obj = sha256()

		fb = fp.read(blocksize)
		while len(fb):  # pylint: disable=len-as-condition
			hash_obj.update(fb)
			fb = fp.read(blocksize)

		return hash_obj.hexdigest()


class ProgressBar(tqdm.tqdm):  # noqa: PRM002
	"""
	Customised ``tqdm`` progressbar.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._error_count = 0
		self._warning_count = 0

	def error(self, message: str) -> None:
		"""
		Print the given error message, in yellow text.

		:param message:
		"""

		self._error_count += 1
		self.write(Fore.RED(message))

	def warning(self, message: str) -> None:
		"""
		Print the given warning message, in yellow text.

		:param message:
		"""

		self._warning_count += 1
		self.write(Fore.YELLOW(message))

	def report_errors_warnings(self, message: str = '') -> None:
		"""
		Print the given message followed by a count of errors and warnings, if any.

		:param message:
		"""

		if self._error_count:
			if self._error_count >= 1:
				message += f"{self._error_count} errors"
			else:
				message += f"{self._error_count} error"

			if self._warning_count:
				message += "; "

		if self._warning_count:
			if self._warning_count >= 1:
				message += f"{self._warning_count} warnings."
			else:
				message += f"{self._warning_count} warning."

		if message:
			if self._error_count:
				self.write(Fore.RED(message))
			elif self._warning_count:
				self.write(Fore.YELLOW(message))
			else:
				self.write(message)


# TODO: helper class for the following three hash/mtime functions


class FileModifications:
	"""
	Helper class for tracking file modifications.

	:param filename: The filename to read and store data to/from.
	"""

	_filename: PathPlus
	_hashes: dict[str, tuple[float, str]]

	def __init__(self, filename: PathLike):
		self._filename = PathPlus(filename)

		try:
			self._hashes = self._filename.load_json()
		except Exception:  # Whatever the cause; maybe log it?
			self._hashes = {}

	def has_file_changed(self, file: PathPlus) -> bool:
		"""
		Returns whether the file has changed by comparing its modifcation time and sha256 hash against the stored values.

		:param file:
		"""

		if file.as_posix() in self._hashes:
			last_mtime, last_hash = self._hashes[file.as_posix()]
			if file.lstat().st_mtime == last_mtime:
				# File hasn't changed
				return False

			if get_sha256_hash(file) == last_hash:
				# File hasn't changed
				return False

		return True

	def record_changed_file(self, file: PathPlus, write: bool = True) -> None:
		"""
		Record the file's current (new) modifcation time and sha256 hash.

		:param file:
		:param write: Write the changes to file now.
		"""

		self._hashes[file.as_posix()] = (file.lstat().st_mtime, get_sha256_hash(file))

		if write:
			self.write_file()

	def write_file(self) -> None:
		"""
		Write the hashes and mtime data to disk.
		"""

		with TemporaryPathPlus() as tmpdir:
			tmpfile = tmpdir / self._filename.name
			tmpfile.dump_json(self._hashes, indent=2)
			# tmpfile.rename(self._filename)  # Doesn't work across devices (drives)
			shutil.copy2(tmpfile, self._filename)
