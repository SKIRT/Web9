#!/bin/bash
# (use "chmod +rx scriptname" to make script executable)
#
# This script builds the HTML pages for the portion of the SKIRT web site that
# is defined in the Web9 repository, exluding the portion that is derived from
# the SKIRT and PTS source code and excluding any pages that are generated from
# python scripts (i.e. ski file reference and publication gallery/lists).
# Formulas are includes as images, which forces the LaTeX to be checked.
#
# Execute this script with "git" as default directory; use on Mac OS X only
#

# generate the html documentation in a folder next to the git folder
mkdir -p ../html
/Applications/Doxygen.app/Contents/Resources/doxygen staging/doxygen_html.txt

# copy redirecting index.html file
cp staging/index_root.html ../html/index.html
