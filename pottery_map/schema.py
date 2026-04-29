#!/usr/bin/env python3
#
#  schema.py
"""
Generate JSON schema for the TOML files.
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

# stdlib
import types
from collections.abc import Sequence
from typing import ClassVar, get_args, get_origin

# 3rd party
import attrs
from domdf_folium_tools import Coordinates
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from typing_extensions import NotRequired, Required, TypedDict

# this package
from pottery_map.company import Company
from pottery_map.pottery import PotteryItem

__all__ = ["Schema", "create_schemas", "dump_schema", "get_schema_property", "make_schema"]


class PotteryMapAttrsInstance(attrs.AttrsInstance):
	_schema_table_name_field: ClassVar[str]
	_schema_exclude_fields: ClassVar[Sequence[str]]


class Property(TypedDict):
	"""
	Represents a property in a JSON Schema.
	"""

	type: Required[str]
	items: NotRequired["Property"]


class Schema(TypedDict):
	"""
	Represents the top-level of a JSON Schema.
	"""

	type: Required[str]
	title: Required[str]
	properties: NotRequired[dict[str, Property]]
	additionalProperties: NotRequired["Schema"]
	required: NotRequired[list[str]]


def get_schema_property(origin: type, args: Sequence[type]) -> Property:
	"""
	Returns the schema propety for the given Python type and its generic args (if any).

	:param origin:
	:param args:
	"""

	if origin is str:
		return {"type": "string"}
		# TODO: string format

	if origin is int:
		return {"type": "integer"}

	if origin is bool:
		return {"type": "boolean"}

	if origin is list:
		schema_property: Property = {"type": "array"}

		if args[0] is str:
			schema_property["items"] = {"type": "string"}
			# TODO: string format
			return schema_property

		if args[0] is int:
			schema_property["items"] = {"type": "integer"}
			return schema_property

	if origin in {dict, Coordinates}:
		# TODO: nested object properties
		return {"type": "object"}

	# print(attribute.name, attribute.type, origin, args)
	raise NotImplementedError(origin, args)


def make_schema(cls: type[PotteryMapAttrsInstance]) -> Schema:
	"""
	Create a schema for the given object.

	:param cls:
	"""

	schema: Schema = {
			"type": "object",
			"title": cls.__name__,
			"properties": {},
			"required": [],
			}

	attribute: attrs.Attribute
	for attribute in attrs.fields(cls):
		# print(attribute)
		assert attribute.validator is None
		assert attribute.converter is None
		assert attribute.name == attribute.alias
		# print(attribute.name, attribute.default, attribute.type)

		if attribute.name == cls._schema_table_name_field or attribute.name in cls._schema_exclude_fields:
			continue

		if attribute.default is attrs.NOTHING:
			schema["required"].append(attribute.name)

		origin, args = get_origin(attribute.type), get_args(attribute.type)
		if attribute.type and origin is None:
			origin = attribute.type

		assert isinstance(origin, type)

		if origin is types.UnionType:  # noqa: E721  # False positive
			union_types = list(args)
			if attribute.default is None and types.NoneType in union_types:
				union_types.remove(types.NoneType)
			if len(union_types) == 1:
				origin = union_types[0]
				args = ()

		if origin is Company:
			schema["properties"].update(make_schema(origin)["properties"])
			# schema_property["$ref"] = "companies.toml.schema.json"
			# schema["properties"][attribute.name] = schema_property
			continue

		schema_property = get_schema_property(origin, args)
		# TODO: property description from docstring/doc comments
		schema["properties"][attribute.name] = schema_property

	return schema


def dump_schema(schema: Schema, toml_filename: str, output_dir: PathLike = '.') -> PathPlus:
	"""
	Write the given schema to file.

	The output filename is ``<output_dir>/<toml_filename>.schema.json``

	:param schema:
	:param toml_filename: The name of the TOML file this schema applies to.
	:param output_dir: Directory to write the schema file to.

	:returns: The path to the created file.
	"""

	main_schema: Schema = {
			# TODO:  "$id": "https://example.com/person.schema.json",
			"$schema": "https://json-schema.org/draft/2020-12/schema",  # type: ignore[typeddict-unknown-key]
			"type": "object",
			"title": toml_filename,
			"additionalProperties": schema,
			}

	schema_file = PathPlus(output_dir) / f"{toml_filename}.schema.json"
	schema_file.dump_json(main_schema, indent=2)
	return schema_file


def create_schemas(output_dir: PathLike = '.') -> list[PathPlus]:
	"""
	Create the two schemas and return the paths to them.

	:param output_dir: Directory to write the schema file to.
	"""

	return [
			dump_schema(
					make_schema(Company),  # type: ignore[arg-type]  # False positive despite Protocol
					"companies.toml",
					output_dir=output_dir,
					),
			dump_schema(
					make_schema(PotteryItem),  # type: ignore[arg-type]  # False positive despite Protocol
					"pottery.toml",
					output_dir=output_dir,
					),
			]
