#!/usr/bin/env python3
#
#  types.py
"""
Base types.
"""
#
#  Copyright © 2025 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# 3rd party
from typing_extensions import NotRequired, Required, TypedDict

__all__ = ["CompanyData", "Coordinates", "PotteryData"]


class Coordinates(TypedDict):
	"""
	The coordinates of a factory.
	"""

	latitude: float
	longitude: float


class PotteryData(TypedDict):
	"""
	An item in the pottery collection.
	"""

	company: NotRequired[str]
	factory: NotRequired[str]
	type: Required[str]
	item: Required[str]
	design: Required[str]
	era: Required[str]
	notes: NotRequired[list[str]]
	photo_url: NotRequired[str]  # TODO: multiple images
	location: NotRequired[Coordinates | None]
	successor: NotRequired[str | None]
	defunct: Required[bool]


class CompanyData(TypedDict):
	"""
	A company and the items made by it.
	"""

	factory: Required[str]
	location: Required[Coordinates | None]
	successor: Required[str | None]
	defunct: Required[bool]
	items: NotRequired[list[PotteryData]]
