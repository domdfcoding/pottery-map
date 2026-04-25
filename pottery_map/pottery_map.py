#!/usr/bin/env python3
#
#  pottery_map.py
"""
Map showing where items in a pottery collection were manufactured.
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
from collections.abc import Iterator
from operator import attrgetter
from typing import NamedTuple
from urllib.parse import urlparse

# 3rd party
from branca.element import Figure  # nodep
from domdf_folium_tools.elements import render_figure
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from folium_about_button import render_markdown

# this package
from pottery_map.companies import Companies, _get_item_count, load_companies
from pottery_map.dashboard import get_dashboard_data
from pottery_map.map import make_map
from pottery_map.pottery import PotteryItem, load_pottery_collection
from pottery_map.templates import render_template
from pottery_map.utils import (
		IMG_HEIGHT,
		IMG_WIDTH,
		FileModifications,
		ProgressBar,
		_convert_image,
		copy_static_files,
		get_photo_path,
		groupby,
		make_id,
		normalise_category
		)

__all__ = ["PotteryMap", "SidebarData"]


class SidebarData(NamedTuple):
	"""
	Data used in the sidebar.
	"""

	all_companies: tuple[str, ...]
	all_categories: tuple[str, ...]


class PotteryMap:
	"""
	Class for producing the pottery map website.

	:param input_directory: Directory containing collection data files.
	:param output_directory:
	"""

	input_directory: PathPlus
	output_directory: PathPlus
	pottery: list[PotteryItem]
	companies: Companies
	has_notes: bool
	notes_markdown: str
	has_wishlist: bool
	wishlist_markdown: str
	category_data: dict[str, list[PotteryItem]]
	sidebar_data: SidebarData

	def __init__(self, input_directory: PathLike = '.', output_directory: PathLike = "output"):
		self.input_directory = PathPlus(input_directory)
		self.output_directory = PathPlus(output_directory)

		self.pottery = load_pottery_collection(self.input_directory / "pottery.toml")
		companies = load_companies(self.input_directory / "companies.toml")
		self.companies = Companies.from_raw_data(self.pottery, companies)

		self.category_data: dict[
				str,
				list[PotteryItem],
				] = groupby(self.pottery, lambda p: normalise_category(p.category))

		self.sidebar_data = SidebarData(
				all_companies=tuple(self.companies.sorted_company_names),
				all_categories=tuple(sorted(self.category_data.keys())),
				)

		try:
			self.notes_markdown = self.input_directory.joinpath("notes.md").read_text()
			self.has_notes = True
		except (FileNotFoundError, UnicodeDecodeError, PermissionError):
			self.notes_markdown = ''
			self.has_notes = False

		try:
			self.wishlist_markdown = self.input_directory.joinpath("wishlist.md").read_text()
			self.has_wishlist = True
		except (FileNotFoundError, UnicodeDecodeError, PermissionError):
			self.wishlist_markdown = ''
			self.has_wishlist = False

	def render_page(self, template: str, **kwargs) -> str:
		r"""
		Render the template with the given filename with the given parameters.

		:param template:
		:param \*\*kwargs:
		"""

		return render_template(
				template,
				sidebar_data=self.sidebar_data,
				has_notes=self.has_notes,
				has_wishlist=self.has_wishlist,
				**kwargs,
				)

	def render_index(self) -> str:
		"""
		Render the index page with the map.
		"""

		m = make_map(self.companies.pottery_by_company.values(), standalone=False)

		root: Figure = m.get_root()  # type: ignore[assignment]

		return self.render_page(
				"map.jinja2",
				**render_figure(root)._asdict(),
				)

	def render_dashboard(self) -> str:
		"""
		Renders HTML for the dashboard page.
		"""

		return self.render_page(
				"dashboard.jinja2",
				**get_dashboard_data(self.pottery, self.companies),
				chart_list=[
						"groups-pie-chart",
						"materials-pie-chart",
						"companies-bar-chart",
						"areas-pie-chart",
						"categories-pie-chart",
						"types-bar-chart",
						],
				)

	def render_notes(self) -> str:
		"""
		Render the notes page.
		"""

		return self.render_page(
				"markdown_page.jinja2",
				title="Notes",
				body=render_markdown(self.notes_markdown),
				)

	def render_wishlist(self) -> str:
		"""
		Render the wishlist page.
		"""

		return self.render_page(
				"markdown_page.jinja2",
				title="Wishlist",
				body=render_markdown(self.wishlist_markdown),
				)

	def render_items_page(self) -> str:
		"""
		Render the page showing all items.
		"""

		return self.render_page(
				"items_page.jinja2",
				items=sorted(self.pottery, key=attrgetter("design")),
				)

	def render_companies_index(self) -> str:
		"""
		Render the page giving an overview of the companies represented in the collection.
		"""

		return self.render_page(
				"company_index.jinja2",
				companies=self.companies,
				get_item_count=_get_item_count,
				)

	def render_company_pages(self) -> Iterator[tuple[str, str]]:
		"""
		Render the pages for the companies.
		"""

		for (company, items) in self.companies.pottery_by_company.values():

			html = self.render_page(
					"company_page.jinja2",
					company=company,
					items=items,
					)
			yield company.name, html

	def render_categories_index(self) -> str:
		"""
		Render the page listing all categories.
		"""

		return self.render_page(
				"categories_index.jinja2",
				category_data=self.category_data,
				)

	def render_categories_pages(self) -> Iterator[tuple[str, str]]:
		"""
		Render the pages for the categories.
		"""

		for category, items in self.category_data.items():

			html = self.render_page(
					"category_page.jinja2",
					category=category,
					items=sorted(items, key=attrgetter("design")),
					)
			yield category, html

	def prepare_output_directories(self) -> dict[str, PathPlus]:
		"""
		Create the output directory structure.

		:returns: A mapping of the subdirectory names to :class:`~.PathPlus` objects.
		"""

		static_dir = self.output_directory / "static"
		static_dir.maybe_make(parents=True)

		companies_dir = self.output_directory / "companies"
		companies_dir.maybe_make()

		categories_dir = self.output_directory / "categories"
		categories_dir.maybe_make()

		return {
				"static": static_dir,
				"companies": companies_dir,
				"categories": categories_dir,
				}

	def copy_images(self) -> None:
		"""
		Copy required images into the output folder.
		"""

		image_hashes = FileModifications(self.output_directory / "images" / "hashes.json")

		photos_to_copy: list[tuple[PathPlus, PathPlus]] = []
		for item in self.pottery:
			for path in item.get_substituted_photo_paths():
				parts = urlparse(path)
				if not (parts.scheme and parts.netloc):
					# Local filesystem path; will be copied into images/{id}
					photos_to_copy.append((
							self.input_directory / path,
							self.output_directory / get_photo_path(item, path),
							))

		if photos_to_copy:
			progbar = ProgressBar(photos_to_copy, desc="Copying images")

			src_path: PathPlus
			dst_path: PathPlus

			for src_path, dst_path in progbar:
				dst_path.parent.maybe_make(parents=True)

				if src_path.is_file():
					if not image_hashes.has_file_changed(src_path):
						# File hasn't changed
						continue

					# progbar.write(f"{src_path.as_posix()} -> {dst_path.as_posix()}")

					img_ratio = _convert_image(src_path, dst_path)
					if img_ratio != 4 / 3:
						warning_msg = f"Warning: Image has wrong ratio ({img_ratio}; expected {IMG_WIDTH / IMG_HEIGHT}): {src_path.as_posix()}"
						progbar.warning(warning_msg)
					else:
						image_hashes.record_changed_file(src_path)
				else:
					progbar.error(f"Error: Image not found: {src_path.as_posix()}")

			image_hashes.write_file()
			progbar.report_errors_warnings("Complete. ")

	def write_output(self) -> None:
		"""
		Write the files for the pottery collection website.
		"""

		directories = self.prepare_output_directories()

		copy_static_files(directories["static"])

		(self.output_directory / "index.html").write_clean(self.render_index())
		self.output_directory.joinpath("dashboard.html").write_clean(self.render_dashboard())
		self.output_directory.joinpath("items.html").write_clean(self.render_items_page())

		if self.has_notes:
			self.output_directory.joinpath("notes.html").write_clean(self.render_notes())

		if self.has_wishlist:
			self.output_directory.joinpath("wishlist.html").write_clean(self.render_wishlist())

		for company, page_content in self.render_company_pages():
			directories["companies"].joinpath(make_id(company) + ".html").write_clean(page_content)

		directories["companies"].joinpath("index.html").write_clean(self.render_companies_index())

		for category, html in self.render_categories_pages():
			directories["categories"].joinpath(f"{make_id(category)}.html").write_clean(html)

		directories["categories"].joinpath("index.html").write_clean(self.render_categories_index())
