# Copyright (C) 2012 Alex Nisnevich
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
import subprocess

from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform

#
# autoshotre = re.compile(r"^!AUTOSHOT\s+(?:\"([^\"]+)\"|'([^']+)')"
#                         r"\s*(?:,\s*(\d+))?\s*$")

# Matches !AUTOSHOT "http://example.com/whatever" "path/to/screenshot.png"
autoshotre = re.compile(r"^!AUTOSHOT\s+(?:\"([^\"]+)\"\s+\"([^\"]+)\")")

codere = re.compile(r"^(    |\t)")
fencedcodere = re.compile(r"^```\w*$")

class Autoshot(Module):
    """
    Does Autoshot things.
    """

    def transform(self, data):
        transforms = []
        in_fenced_code_block = False
        linenum = 0

        for line in data:
            # Handle fenced code blocks (for Github-flavored markdown)
            if fencedcodere.search(line):
                if in_fenced_code_block:
                    in_fenced_code_block = False
                else:
                    in_fenced_code_block = True

            # Only proceed if we're not in a code block.
            if not in_fenced_code_block and not codere.search(line):
                match = autoshotre.search(line)
                if match:
                    autoshot_script = match.group(1)
                    dest_image_filename = match.group(2)

                    # Generate the screenshot.
                    # Example: $ nodejs scripts/shot001.js -o build/assets/shot001.png

                    p = subprocess.call(["nodejs", autoshot_script, dest_image_filename])

                    # Transform the !AUTOSHOT directive into an image tag.
                    image_embed = ('![](%s)\n' % (dest_image_filename))
                    transforms.append(Transform(linenum, "swap", image_embed))

            linenum += 1

        return transforms
