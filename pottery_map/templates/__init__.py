# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus
from jinja2 import Environment

# this package
from pottery_map._jinja2_workarounds import MultiLineInclude
from pottery_map.utils import make_id

templates = Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str((PathPlus(__file__).parent).absolute())),
		undefined=jinja2.StrictUndefined,
		extensions=[MultiLineInclude],
		)

templates.globals["make_id"] = make_id
