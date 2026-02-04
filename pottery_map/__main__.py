

if __name__ == "__main__":
	from typing import Dict, List

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from pottery_map import load_pottery_collection
	from pottery_map.companies import group_pottery_by_company, load_companies
	from pottery_map.map import make_map
	from pottery_map.utils import set_branca_random_seed
	import networkx
	from domdf_python_tools.paths import PathPlus
	from domdf_python_tools.compat import importlib_resources


	# this package
	from pottery_map import load_pottery_collection
	from pottery_map.companies import group_pottery_by_company, load_companies, make_successor_network
	from pottery_map.templates import templates
	from pottery_map.utils import make_id, set_branca_random_seed

	set_branca_random_seed("WWRD")
	output_dir = PathPlus("output")
	output_dir.maybe_make()

	static_dir = output_dir / "static"
	js_dir = static_dir / "js"
	css_dir = static_dir / "css"
	js_dir.maybe_make(parents=True)
	css_dir.maybe_make()

	(js_dir / "sidebar.js").write_text(importlib_resources.read_text("pottery_map.static", "sidebar.js"))
	(css_dir / "pottery_map.css").write_text(importlib_resources.read_text("pottery_map.static", "pottery_map.css"))
	(css_dir / "sidebar.css").write_text(importlib_resources.read_text("pottery_map.static", "sidebar.css"))
	(css_dir / "style.css").write_text(importlib_resources.read_text("pottery_map.static", "style.css"))

	pottery = load_pottery_collection("pottery.toml")
	companies = load_companies("companies.toml")
	pottery_by_company = group_pottery_by_company(pottery, companies)

	companies_dir = output_dir / "companies"
	companies_dir.maybe_make()

	m = make_map(pottery_by_company)

	html = m.get_root().render()
	(output_dir / "index.html").write_clean(html)


	graph = make_successor_network(companies)

	all_companies = {*graph.nodes(), *pottery_by_company}

	for company in all_companies:
		if company in pottery_by_company:
			company_data = pottery_by_company[company]
		else:
			company_data = {"items": [], **companies[company]}

		companies_dir.joinpath(make_id(company) + ".html").write_clean(
				templates.get_template("company_page.jinja2").render(
						company=company,
						factory=company_data["factory"],
						location=company_data["location"],
						items=company_data["items"],
						all_companies=sorted(all_companies),
						)
				)



	company_item_counts: Dict[str, int] = {}

	for company, company_data in pottery_by_company.items():
		company_item_counts[company] = len(company_data["items"])

	top_level_companies = [x for x in graph.nodes() if graph.out_degree(x) == 0]

	def get_item_count(company_item_counts: Dict[str, int], ancestors: List[str]):
		return sum([company_item_counts.get(x, 0) for x in ancestors])

	companies_dir.joinpath("index.html").write_clean(
			templates.get_template("company_index.jinja2").render(
					company_item_counts=company_item_counts,
					top_level_companies=top_level_companies,
					sorted=sorted,
					get_item_count=get_item_count,
					networkx=networkx,
					graph=graph,
					list=list,
					all_companies=sorted(all_companies),
					)
			)

	

