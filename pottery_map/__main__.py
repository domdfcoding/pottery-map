#!/usr/bin/env python3
#
#  __main__.py
"""
Generate map showing where items in a pottery collection were manufactured, and catalogue pages.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from consolekit import CONTEXT_SETTINGS, click_command
from consolekit.options import auto_default_argument, auto_default_option

__all__ = ["main"]


@auto_default_argument("input_directory")
@auto_default_option("-o", "--out-dir", help="The output directory.")
@auto_default_option("-i", "--img-dir", help="The images directory to copy into the output directory.")
@auto_default_option(
		"--standalone", is_flag=True, help="Create a standalone map without catalogue pages or additional files."
		)
@click_command(context_settings={**CONTEXT_SETTINGS, "show_default": True})
def main(
		input_directory: str = '.',
		out_dir: str = "output",
		img_dir: str = "images",
		standalone: bool = False,
		) -> None:
	"""
	Generate map showing where items in a pottery collection were manufactured, and catalogue pages.
	"""

	# stdlib
	import shutil

	# 3rd party
	from domdf_folium_tools import set_branca_random_seed
	from domdf_python_tools.paths import PathPlus

	# this package
	from pottery_map.map import _create_standalone_map
	from pottery_map.pottery_map import PotteryMap

	set_branca_random_seed("WWRD")

	output_directory = PathPlus(out_dir)

	if standalone:
		html = _create_standalone_map(PathPlus(input_directory))
		output_directory.joinpath("index.html").write_clean(html)
		return

	PotteryMap(input_directory=input_directory, output_directory=out_dir).write_output()

	image_directory = PathPlus(img_dir)
	if not image_directory.is_absolute():
		if (input_directory / image_directory).exists():
			image_directory = input_directory / image_directory

	if image_directory.exists():
		# Perfectly acceptable for it not to
		shutil.copytree(image_directory, output_directory / image_directory.name, dirs_exist_ok=True)


if __name__ == "__main__":
	main()
