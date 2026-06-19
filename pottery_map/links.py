#!/usr/bin/env python3
#
#  links.py
"""
Helpers to find links for companies (Wikipedia, thepotteries.org).
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
import posixpath
import webbrowser
from urllib.parse import quote, urlparse

# 3rd party
import requests  # nodep
from bs4 import BeautifulSoup  # nodep
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from tomledit import Document  # type: ignore[import-not-found]  # nodep

# this package
from pottery_map.company import CompanyData

__all__ = [
		"extract_html_title",
		"extract_wikipedia_title",
		"google_pdo",
		"has_url_for",
		"search_wikipedia",
		"toml_dump_editable",
		"toml_load_editable",
		]


def _quote(string: str) -> str:
	return quote(string, safe="/+")


def google_pdo(company_name: str) -> None:
	"""
	Opens the web browser and searches Google for the company's page on thepotteries.org (if any).

	:param company_name:
	"""

	root_url = "https://www.google.com/search?q="
	webbrowser.open(root_url + _quote(company_name.replace(' ', '+') + "+site:" + "thepotteries.org"))


def search_wikipedia(company_name: str) -> None:
	"""
	Opens the web browser and searches Wikipedia for the company's article (if any).

	:param company_name:
	"""

	root_url = "https://en.wikipedia.org/w/index.php?title=Special:Search&search="
	webbrowser.open(root_url + _quote(company_name.replace(' ', '+')))


def extract_html_title(url: str) -> str:
	"""
	Returns the web page title for the given URL.

	:param url:
	"""

	response = requests.get(url)
	response.raise_for_status()

	soup = BeautifulSoup(response.text, "html.parser")
	title = soup.find("title")
	assert title is not None
	return title.text


def extract_wikipedia_title(url: str) -> str:
	"""
	Returns the Wikipedia page title for the given URL.

	:param url:
	"""

	# TODO: handle invalid characters

	parts = urlparse(url)
	return posixpath.split(parts.path)[-1].replace('_', ' ')


def toml_load_editable(filename: PathLike) -> Document:
	"""
	Load a TOML file for editing, preserving formatting and comments.

	:param filename:
	"""

	return Document.parse(PathPlus(filename).read_text())


def toml_dump_editable(document: Document, filename: PathLike) -> None:
	"""
	Save an edited TOML document, preserving formatting and comments.

	:param document:
	:param filename:
	"""

	PathPlus(filename).write_clean(document.as_toml())


def has_url_for(domain: str, company: CompanyData) -> bool:
	"""
	Returns whether the given company has a link pointing to the given domain.

	:param domain:
	:param company:
	"""

	links: dict[str, str] = company.get("links", {})
	return any(domain in text.lower() or domain in url.lower() for text, url in links.items())
