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

if __name__ == "__main__":
	# stdlib
	import json

	# 3rd party
	from domdf_python_tools.paths import PathPlus
	from folium import Figure, JavascriptLink

	# this package
	from pottery_map import load_pottery_collection
	from pottery_map.companies import Companies, load_companies, make_company_pages
	from pottery_map.dashboard import companies_bar_chart, groups_pie_chart
	from pottery_map.map import make_map
	from pottery_map.templates import render_template
	from pottery_map.utils import copy_static_files, make_id, set_branca_random_seed

	set_branca_random_seed("WWRD")

	output_dir = PathPlus("output")
	static_dir = output_dir / "static"
	static_dir.maybe_make(parents=True)

	copy_static_files(static_dir)

	pottery = load_pottery_collection("pottery.toml")
	companies = load_companies("companies.toml")
	c = Companies.from_raw_data(pottery, companies)

	m = make_map(c.pottery_by_company, standalone=False)

	root: Figure = m.get_root()  # type: ignore[assignment]

	js_libs = m.default_js
	m.default_js = []
	m.default_css = []

	scripts = [JavascriptLink(lib[1]).render() for lib in js_libs]

	for child in root._children.values():
		child.render()

	html = render_template(
			"map.jinja2",
			header=root.header.render(),
			body=root.html.render(),
			script=root.script.render(),
			scripts='\n'.join(scripts),
			all_companies=c.sorted_company_names,
			)

	(output_dir / "index.html").write_clean(html)

	companies_dir = output_dir / "companies"
	companies_dir.maybe_make()

	companies_index, company_pages = make_company_pages(c)

	for company, page_content in company_pages.items():
		companies_dir.joinpath(make_id(company) + ".html").write_clean(page_content)

	companies_dir.joinpath("index.html").write_clean(companies_index)

	output_dir.joinpath("dashboard.html").write_clean(
			render_template(
					"dashboard.jinja2",
					groups_pie_chart_data=json.dumps(groups_pie_chart(c)),
					companies_bar_chart_data=json.dumps(companies_bar_chart(c)),
					all_companies=c.sorted_company_names,
					),
			)
