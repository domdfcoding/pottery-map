if __name__ == "__main__":

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from pottery_map import load_pottery_collection
	from pottery_map.companies import group_pottery_by_company, load_companies, make_company_pages
	from pottery_map.map import make_map
	from pottery_map.utils import copy_static_files, make_id, set_branca_random_seed

	set_branca_random_seed("WWRD")
	output_dir = PathPlus("output")
	output_dir.maybe_make()

	static_dir = output_dir / "static"

	copy_static_files(static_dir)

	pottery = load_pottery_collection("pottery.toml")
	companies = load_companies("companies.toml")
	pottery_by_company = group_pottery_by_company(pottery, companies)

	companies_dir = output_dir / "companies"
	companies_dir.maybe_make()

	m = make_map(pottery_by_company)

	html = m.get_root().render()
	(output_dir / "index.html").write_clean(html)

	companies_index, company_pages = make_company_pages(companies, pottery_by_company)

	for company, page_content in company_pages.items():
		companies_dir.joinpath(make_id(company) + ".html").write_clean(page_content)

	companies_dir.joinpath("index.html").write_clean(companies_index)
