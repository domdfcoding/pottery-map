# 3rd party
import jinja2
import networkx
from domdf_python_tools.paths import PathPlus

# this package
from pottery_map import load_pottery_collection
from pottery_map.companies import group_pottery_by_company, load_companies, make_successor_network
from pottery_map.templates import templates
from pottery_map.utils import make_id, set_branca_random_seed

set_branca_random_seed("WWRD")

pottery = load_pottery_collection("pottery.toml")
companies = load_companies("companies.toml")
pottery_by_company = group_pottery_by_company(pottery, companies)

companies_dir = PathPlus("companies")
companies_dir.maybe_make()

graph = make_successor_network(companies)

all_compannies = {*graph.nodes(), *pottery_by_company}

for company in all_compannies:
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
					make_id=make_id,
					)
			)

with companies_dir.joinpath("index.html").open('w') as fp:
	fp.write(
			"""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">

    <title></title>
  </head>

  <body>
	<div class="container">
		<h1>Companies</h1>

		<div class="row">
			<div class="col-sm-6">
		  		<h2>By Name</h2>
				<ul>
""",
			)

	company_item_counts = {}

	for company, company_data in pottery_by_company.items():
		company_item_counts[company] = len(company_data["items"])

	for company, item_count in sorted(company_item_counts.items()):
		fp.write(f"<li><a href='{make_id(company)}.html'>{company}</a> ({item_count})</li>")

	fp.write("""\
		</ul>
		</div>
		<div class="col-sm-6">
			<h2>By Parent</h2>
""")

	top_level_companies = [x for x in graph.nodes() if graph.out_degree(x) == 0]

	def write_company_entries(name, indent: int = 0):

		ancestors = networkx.ancestors(graph, name)
		ancestors.add(name)
		item_count = sum([company_item_counts.get(x, 0) for x in ancestors])

		fp.write((' ' * indent) + f"<li><a href='{make_id(name)}.html'>{name}</a> ({item_count})</li>")
		predecessors = list(graph.predecessors(name))
		if predecessors:
			fp.write((' ' * indent) + "<ul>")
			for predecessor in predecessors:
				write_company_entries(predecessor, indent + 2)
			fp.write((' ' * indent) + " </ul>")

	fp.write("<ul>")
	for company in top_level_companies:
		write_company_entries(company)
	fp.write("</ul>")

	fp.write(
			"""\
		</div>
	</div>
</div>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
</body>
</html>
""",
			)
