# From https://github.com/stereobutter/jinja2_workarounds
# 
# MIT License

# Copyright (c) 2022 Sascha Desch

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from jinja2 import Environment, TemplateSyntaxError
from jinja2.ext import Extension
import re


def _improved_include_statement(block_start, block_end):
    return re.compile(fr"""
        (^ .*)  # first group: greedy tokens at the beginning of the line
        (?= # second group: positive lookahead of pattern
            (
                {re.escape(block_start)}
                (?P<block_start_modifier> [\+|-]?)
                (?P<statement>
                    \s* include \b   # include keyword
                    \s*? .*?  # fluff
                    indent \s content  # new 'with indentation' option
                    \s*? .*? # fluff
                )
                (?P<block_end_modifier> [\+|-]?)
                {re.escape(block_end)}
            )
        )
        .* $ # rest of the line, required to also include the lookahead in the match
        """,
        flags=re.MULTILINE|re.VERBOSE)


class MultiLineInclude(Extension):

    def preprocess(self, source, name, filename=None):
        env: Environment = self.environment

        block_start: str = env.block_start_string
        block_end: str = env.block_end_string
        pattern = _improved_include_statement(block_start=block_start, block_end=block_end)
        re_newline = re.compile('\n')

        def add_indentation_filter(match):
            line_content_before_statement = match.group(1)
            statement = match.group('statement').replace('indent content', '')  # strip 'with indentation' directive

            # guard against invalid use of improved include statement
            if line_content_before_statement is not None:
                # line before include statement must be indentation only
                if not line_content_before_statement.isspace():
                    start_position = match.start(0)
                    lineno = len(re_newline.findall(source, 0, start_position)) + 1
                    raise TemplateSyntaxError(
                        "line contains non-whitespace characters before include statement",
                        lineno,
                        name,
                        filename,
                    )

            indentation = line_content_before_statement or ''
            block_start_modifier = match.group('block_start_modifier') or ''
            block_end_modifier = match.group('block_end_modifier') or ''

            start_filter = indentation + f'{block_start + block_start_modifier} filter indent({indentation!r}) -{block_end}'
            include_statement = indentation + f'{block_start} {statement} {block_end}'
            end_filter = indentation + f'{block_start}- endfilter {block_end_modifier + block_end}'

            return'\n'.join([start_filter, include_statement, end_filter])

        return pattern.sub(add_indentation_filter, source)

