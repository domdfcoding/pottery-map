import folium
import dom_toml

m = folium.Map(location=(53.02445128825057, -2.1834733161173445), font_size="16px")
m.add_css_link("pottery_map.css", "./pottery_map.css")

pottery = list(dom_toml.load("pottery.toml").values())

# pottery = [
# 	{
# 		"company": "J & G Meakin",
# 		"factory": "Eagle Pottery",
# 		"location": {"latitude": 53.02308684898784, "longitude": -2.1629028183132877},
# 		"type": "Earthenware",
# 		"item": "Plate",
# 		"design": "Strawberry Border",
# 		"photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Meakin_%27Impact%27_tableware_-_2025-04-22_-_Andy_Mabbett_-_01.jpg/330px-Meakin_%27Impact%27_tableware_-_2025-04-22_-_Andy_Mabbett_-_01.jpg",
# 	}
# ]

for item in pottery:
	popup_text = f"""\
<div class="item-details">
<ul>
	<li>{item['company']}</li>
	<li>{item['factory']}</li>
	<li>{item['type']}</li>
	<li>{item['item']}</li>
	<li>{item['design']}</li>
</ul>
<img class="pottery-image" src="{item['photo_url']}" />
</div>
"""
	folium.Marker(
		location=[item["location"]["latitude"], item["location"]["longitude"]],
		tooltip=item["company"],
		popup=folium.Popup(popup_text, max_width=250),
		# icon=folium.Icon(icon="cloud"),
	).add_to(m)


m.save("index.html")