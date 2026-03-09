#!/usr/bin/env python3
#
#  notes.py
"""
Render markdown for notes and wishlist pages.
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
from re import Match

# 3rd party
import markdown
from markdown.inlinepatterns import IMAGE_LINK_RE, ImageInlineProcessor

__all__ = ["render_markdown"]


class _ImgFluidInlineProcessor(ImageInlineProcessor):
	"""
	Markdown image processor to use bootstrap's ``img-fluid`` class.
	"""

	# TODO: mypy thinks the signature doesn't match the superclass but it matches what's in their docs and the pyright stubs.
	def handleMatch(self, m: Match[str], data: str):  # type: ignore[override]  # noqa: MAN002
		el, start, index = super().handleMatch(m, data)
		assert el is not None
		el.set("class", "img-fluid")  # type: ignore[union-attr]
		return el, start, index


def render_markdown(source: str) -> str:
	"""
	Render the given markdown to HTML.

	:param source:
	"""

	text = source.splitlines()

	md = markdown.Markdown(extensions=["fenced_code", "codehilite", "toc"])
	md.inlinePatterns.register(_ImgFluidInlineProcessor(IMAGE_LINK_RE, md), "image_link", 150)

	while not text[0].strip():
		text.pop(0)

	body = md.convert('\n'.join(text))

	return body
