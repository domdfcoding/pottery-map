# stdlib
from random import Random

# 3rd party
import dom_toml
import folium
from branca import element
from domdf_python_tools.paths import PathPlus
from folium.plugins import MarkerCluster

# this package
from pottery_map.companies import load_companies

rand = Random("WWRD")


def urandom(size: int) -> bytes:
	return rand.randbytes(size)


element.urandom = urandom

# TODO: era

m = folium.Map(location=(53.02445128825057, -2.1834733161173445), font_size="16px")
m.add_css_link("pottery_map.css", "./pottery_map.css")

marker_cluster = MarkerCluster(options={"maxClusterRadius": 50}).add_to(m)

pottery = list(dom_toml.load("pottery.toml").values())
companies = load_companies("companies.toml")
pottery_by_company = {}

for item in pottery:
	new_item = dict(item)
	company = new_item.pop("company")
	if company not in pottery_by_company:
		if company in companies:
			factory = companies[company]["factory"]
			location = companies[company]["location"]
		else:
			factory = new_item.get("factory", "Unknown")
			location = new_item.get("location")
		pottery_by_company[company] = {"items": [], "factory": factory, "location": location}

	if "location" in new_item:
		del new_item["location"]
	if "factory" in new_item:
		del new_item["factory"]

	pottery_by_company[item["company"]]["items"].append(new_item)

for company, company_data in pottery_by_company.items():

	if "location" not in company_data or not company_data["location"]:
		continue

	popup_text = f"""
<div class="item-details">
<h2>{company}</h2>
<h3><strong>{company_data['factory']}</strong></h3>
		"""

	for item in company_data["items"]:

		popup_text += f"""
<ul>
	<li>{item['design']}</li>
	<li>{item['type']} {item['item']}</li>
	<li>{item['era']}</li>
</ul>
<img class="pottery-image" src="{item['photo_url']}" />
	"""

	popup_text += "</div>"

	folium.Marker(
			location=[company_data["location"]["latitude"], company_data["location"]["longitude"]],
			tooltip=company,
			popup=folium.Popup(popup_text, max_width=400, min_width=245),
			).add_to(marker_cluster)

html = m.get_root().render()
PathPlus("index.html").write_clean(html)
