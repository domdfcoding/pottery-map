# 3rd party
from domdf_python_tools.paths import PathPlus

# this package
from pottery_map import load_pottery_collection
from pottery_map.companies import group_pottery_by_company, load_companies
from pottery_map.utils import make_id, set_branca_random_seed

set_branca_random_seed("WWRD")

pottery = load_pottery_collection("pottery.toml")
companies = load_companies("companies.toml")
pottery_by_company = group_pottery_by_company(pottery, companies)

companies_dir = PathPlus("companies")
companies_dir.maybe_make()

for company, company_data in pottery_by_company.items():

	with companies_dir.joinpath(make_id(company) + ".html").open('w') as fp:

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

"""
				)

		# fp.write(f"<div class='company container' id={make_id(company)}>")
		fp.write(f"<h1>{company}</h1>\n")
		fp.write(f"<h2>{company_data['factory']}</h2>\n")
		location = company_data["location"]
		if location:
			factory_lat = company_data["location"]["latitude"]
			factory_lng = company_data["location"]["longitude"]
			fp.write(
					f"<h6><a href='https://www.google.com/maps/place/{factory_lat},{factory_lng}'>View On Map</a></h6>\n"
					)
		fp.write(f"<div class='wares gy-2' id={make_id(company)}-wares>")
		fp.write(f"<h3>Wares</h3>\n")
		for item in company_data["items"]:
			fp.write(f"<div class='item border' id={item['id']}>")
			fp.write(f"<h4>{item['design']}</h4>\n")
			fp.write(f"<p>{item['type']}</p>\n")
			fp.write(f"<p>{item['era']}</p>\n")
			if "notes" in item:
				fp.write(f"<code>{item['notes']}</code><br>\n")
			fp.write(f"<img class='pottery-image' src='{item['photo_url']}' />")
			fp.write("</div>")
		fp.write("</div>")
		# fp.write("</div>")

		fp.write(
				"""\
	</div>
			<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
	</body>
	</html>
	"""
				)

with PathPlus("companies.html").open('w') as fp:
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
		  <ul>
"""
			)
	for company, company_data in sorted(pottery_by_company.items()):
		item_count = len(company_data["items"])
		fp.write(f"<li><a href='companies/{make_id(company)}.html'>{company}</a> ({item_count})</li>")

	fp.write(
			"""\
</ul>
</div>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
</body>
</html>
"""
			)
