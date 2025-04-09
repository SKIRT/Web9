#!/usr/bin/env python
# -*- coding: utf8 -*-

# This Python script generates a Doxygen input page that allows manual download of the
# SKIRT resource packs. The page automatically adjusts to include all available packs.
#
# The script is executed as part of the make HTML process, *before* running Doxygen on
# this part of the web site. It accepts two mandatory command line arguments:
#  - a local directory holding the resource packs (Archives) and definitions (Definitions);
#  - the directory where the text file to be consumed by Doxygen will be placed.
#

# -----------------------------------------------------------------

import sys
import pathlib

# -----------------------------------------------------------------

# get the directories
if len(sys.argv) != 3: raise ValueError("This script requires 2 arguments; refer to the script header")
zipdir = pathlib.Path(sys.argv[1]) / "Archives"
defdir = pathlib.Path(sys.argv[1]) / "Definitions"
outdir = pathlib.Path(sys.argv[2])

# -----------------------------------------------------------------

# get the resource pack names, including version, in reverse alphabetical order
zipnames = sorted([path.name for path in zipdir.glob("*.zip")], reverse=True)

# construct the Doxygen text file
with open(outdir/"DownloadResourcePacks.txt", 'w') as pg:
    # write page header
    pg.write("/**\n")
    pg.write("\\page DownloadResourcePacks Download SKIRT resource packs (Windows)\n")
    pg.write("This page provides links to allow manual download of the SKIRT resource packs.\n")
    pg.write("This is needed only when installing SKIRT on Microsoft Windows; see \\ref InstallSKIRTWindowsResource.\n")
    pg.write("On Unix and macOS platforms, use the automated procedure instead; see \\ref InstallSKIRTUnixResource.\n")
    pg.write("\n")

    # write table header
    pg.write("| Resource pack | Size | Description |\n")
    pg.write("|--|--|--|\n")

    # write links to the resource packs
    for zipname in zipnames:
        zipsize = (zipdir / zipname).stat().st_size
        ziplink = "https://sciences.ugent.be/skirtextdat/SKIRT9/Resources/" + zipname
        resourcename = zipname.split("_")[2]
        with open(defdir/resourcename/"history.txt") as history:
            zipdesc = history.readline().strip()
        pg.write("| [{}]({}) | {:1.1f} MB | {} |\n".format(zipname, ziplink, zipsize/(1024**2), zipdesc))

    # write page footer
    pg.write("\n")
    pg.write("*/\n")

# -----------------------------------------------------------------
