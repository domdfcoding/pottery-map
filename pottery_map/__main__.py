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

	# 3rd party
	from domdf_python_tools.paths import PathPlus
	from folium import Figure, JavascriptLink

	# this package
	from pottery_map import load_pottery_collection
	from pottery_map.companies import (
			group_pottery_by_company,
			load_companies,
			make_company_pages,
			make_successor_network
			)
	from pottery_map.map import make_map
	from pottery_map.templates import templates
	from pottery_map.utils import copy_static_files, make_id, set_branca_random_seed

	set_branca_random_seed("WWRD")

	output_dir = PathPlus("output")
	static_dir = output_dir / "static"
	static_dir.maybe_make(parents=True)

	copy_static_files(static_dir)

	pottery = load_pottery_collection("pottery.toml")
	companies = load_companies("companies.toml")
	pottery_by_company = group_pottery_by_company(pottery, companies)

	companies_dir = output_dir / "companies"
	companies_dir.maybe_make()

	m = make_map(pottery_by_company, standalone=False)

	root: Figure = m.get_root()  # type: ignore[assignment]

	js_libs = m.default_js
	m.default_js = []
	m.default_css = [
			("leaflet_css", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"),
			(
					"awesome_markers_css",
					"https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css",
					),
			]

	scripts = []
	for lib in js_libs:
		scripts.append(JavascriptLink(lib[1]).render())

	for child in root._children.values():
		child.render()

	graph = make_successor_network(companies)

	all_companies: set[str] = {*graph.nodes(), *pottery_by_company}

	html = templates.get_template("map.jinja2").render(
			header=root.header.render(),
			body=root.html.render(),
			script=root.script.render(),
			scripts='\n'.join(scripts),
			all_companies=sorted(all_companies),
			)

	(output_dir / "index.html").write_clean(html)

	companies_index, company_pages = make_company_pages(companies, pottery_by_company)

	for company, page_content in company_pages.items():
		companies_dir.joinpath(make_id(company) + ".html").write_clean(page_content)

	companies_dir.joinpath("index.html").write_clean(companies_index)
