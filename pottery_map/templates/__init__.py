# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus
from jinja2 import Environment

templates = Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str((PathPlus(__file__).parent).absolute())),
		undefined=jinja2.StrictUndefined,
		)
