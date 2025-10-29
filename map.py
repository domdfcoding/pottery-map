# 3rd party
from domdf_python_tools.paths import PathPlus

# this package
from pottery_map import load_pottery_collection
from pottery_map.companies import group_pottery_by_company, load_companies
from pottery_map.map import make_map
from pottery_map.utils import set_branca_random_seed

set_branca_random_seed("WWRD")

pottery = load_pottery_collection("pottery.toml")
companies = load_companies("companies.toml")
pottery_by_company = group_pottery_by_company(pottery, companies)

m = make_map(pottery_by_company)

html = m.get_root().render()
PathPlus("index.html").write_clean(html)
