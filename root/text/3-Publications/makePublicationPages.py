#!/usr/bin/env python
# -*- coding: utf8 -*-

# This Python script generates Doxygen input pages from the contents of the PublicationsDatabase.txt file.
# Each page offers a specific "view" of the list of publications in the database, showing a particular subset
# sorted in a particular way. Each page also offer links to the other pages so that the user can navigate between
# views. As a result, the web site maintainer just needs to update a single file (PublicationsDatabase.txt)
# while still offering various ways to display the information.
#
# The script is executed as part of the "makeHTML" process, *before* running Doxygen on this part of the web site.
# It accepts two optional command line arguments specifying the directory holding the input and output files
# and the directory holding the PDF files containing the publications proper.
#
# Developer note: this script has been developed and tested with Python 3.7.2. However, because it relies on fairly
# basic language features only, it can probably be easily adjusted for earlier Python versions.
#

# -----------------------------------------------------------------

import sys
import os.path
import PIL.Image

# -----------------------------------------------------------------

# get the working directory
wdir = sys.argv[1] if len(sys.argv)>1 else "."
if not wdir.endswith("/"): wdir += "/"

# get the pdf file directory
pdfdir = sys.argv[2] if len(sys.argv)>2 else None
if pdfdir is not None and not pdfdir.endswith("/"): pdfdir += "/"

# -----------------------------------------------------------------

categories = ["Technical", "Application"]
fields = ['title', 'author', 'journal', 'monthyear', 'category', 'pdfname', 'adsname']

def warn(record, message):
    print ("Publication record starting at line nr " + str(record['linenr']) + ": " + message)

# read the publication database
with open(wdir+"PublicationsDatabase.txt", 'r') as db:
    # read blocks of 8 lines into a list of records; each record being a dictionary
    records = []
    linenr = 1
    while True:
        # end the loop if the next line is really empty (not even a newline), meaning EOF
        firstline = db.readline()
        if len(firstline)==0: break;

        record = {}
        record['linenr'] = linenr
        record['title'] = firstline.strip()
        for field in fields[1:]:
            record[field] = db.readline().strip()
        db.readline() # empty separator line

        # skip the header block
        if not record['title'].startswith('#'): records.append(record)
        linenr += 8

# verify the contents of the records
for record in records:
    for field in fields:
        if len(record[field])==0: warn(record, field + " field is empty")
    if not record['category'] in categories: warn(record, "unknown category '" + record['category'] + "'")
    if pdfdir is not None:
        pdfpath = pdfdir + record['pdfname'] + ".pdf"
        if not os.path.exists(pdfpath): warn(record, "PDF file does not exist '" + record['pdfname'] + "'")
    record['month'] = 0
    record['year'] = 0
    try:
        seg = record['monthyear'].split()
        record['month'] = int(seg[0])
        record['year'] = int(seg[1])
    except IndexError:
        warn(record, "Month and/or year have incorrect format '" + record['monthyear'] + "'")
    except ValueError:
        warn(record, "Month and/or year have incorrect format '" + record['monthyear'] + "'")

# -----------------------------------------------------------------

categories = ["All"] + categories
orderings = ["Date", "Author"]
months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# function to generate a text-oriented Doxygen page
def makePage(records, mycateg, myorder):
    with open(wdir+"PublicationsPage"+mycateg+myorder+".txt", 'w') as pg:
        # write page header
        pg.write("/**\n")
        pg.write("\\page Publications" + mycateg + myorder + " " + mycateg + " Publications by " + myorder +"\n")
        pg.write("\n")

        # write links to other pages
        pg.write("- \\ref PublicationsGallery\n")
        pg.write("<p>\n")
        for categ in categories:
            for order in orderings:
                pg.write("- \\ref Publications" + categ + order + "\n")
        pg.write("\n")

        # write table header
        pg.write("| Title | Author(s) | Date | Journal | Category | PDF | ADS |\n")
        pg.write("|--|--|--|--|--|--|--|\n")

        # write the records
        for record in records:
            date = months[record['month']] + " " + str(record['year'])
            pdflink = "[PDF](https://sciences.ugent.be/skirtextdat/SKIRTC/Publications/" + record['pdfname'] + ".pdf)"
            adslink = "[ADS](https://ui.adsabs.harvard.edu/abs/" + record['adsname'] + "/abstract)"
            pg.write("| " + record['title'] + " | " + record['author'] + " | " + date +
                     " | " + record['journal'] + " | " + record['category'] +
                     " | " + pdflink + " | " + adslink + " |\n")

        # write page footer
        pg.write("\n")
        pg.write("*/\n")

# generate the Doxygen pages for records sorted on date
records.sort(key=lambda record: str(record['year'])+str(100+record['month'])+record['author'], reverse=True)
makePage(records, "All", "Date")
makePage([ record for record in records if record['category']=="Technical"], "Technical", "Date")
makePage([ record for record in records if record['category']=="Application"], "Application", "Date")

# generate the Doxygen pages for records sorted on author
records.sort(key=lambda record: record['author']+str(record['year'])+str(100+record['month']), reverse=False)
makePage(records, "All", "Author")
makePage([ record for record in records if record['category']=="Technical"], "Technical", "Author")
makePage([ record for record in records if record['category']=="Application"], "Application", "Author")

# -----------------------------------------------------------------

# function to obtain the aspect ratio width/height for the png image associated with the specified record
def imageAspect(record):
    path = pdfdir + record['pdfname'] + ".png"
    image = PIL.Image.open(path)
    width, height = image.size
    return width/height

# function to generate the image-oriented Doxygen page
def makeGalleryPage(records):
    with open(wdir+"PublicationsPageGallery.txt", 'w') as pg:
        # write page header
        pg.write("/**\n")
        pg.write("\\page PublicationsGallery Publications Gallery\n")
        pg.write("\n")

        # write links to other pages
        pg.write("- \\ref PublicationsGallery\n")
        pg.write("<p>\n")
        for categ in categories:
            for order in orderings:
                pg.write("- \\ref Publications" + categ + order + "\n")
        pg.write("\n")

        # write table of images with links
        pg.write("<TABLE>\n")
        for index, record in enumerate(records):
            if index % 4 == 0:      # start a new row after N columns
                pg.write('<TR style="text-align:center;">\n')
            d = {}
            d["imgpath"] = "https://sciences.ugent.be/skirtextdat/SKIRTC/Publications/" + record['pdfname'] + ".png"
            d["maxwidth"] = int(min(1, imageAspect(record)) * 100)
            d["pdfpath"] = "https://sciences.ugent.be/skirtextdat/SKIRTC/Publications/" + record['pdfname'] + ".pdf"
            d["pdflink"] = "[PDF](https://sciences.ugent.be/skirtextdat/SKIRTC/Publications/" + record['pdfname'] + ".pdf)"
            d["adslink"] = "[ADS](https://ui.adsabs.harvard.edu/abs/" + record['adsname'] + "/abstract)"
            d["alttext"] = record['author'] + " " + str(record['year']) + " (" + record['journal'] + ")"
            d["title"] = record['author'] + " " + str(record['year']) + " (" + record['journal'] + "): " + \
                         record['title']
            pg.write(('<TD><IMG src="{imgpath}" style="max-width:{maxwidth}%;" alt="{alttext}" title="{title}" ' + \
                      'onclick="location.href=\'{pdfpath}\';" loading="lazy"/>\n  {pdflink} {adslink}\n').format(**d))
        pg.write("</TABLE>\n")

        # write page footer
        pg.write("\n")
        pg.write("*/\n")

# generate the Doxygen publication gallery page, sorted on date, limited to papers with an associated image
if pdfdir is not None:
    records = [ record for record in records if os.path.exists(pdfdir + record['pdfname'] + ".png") ]
records.sort(key=lambda record: str(record['year'])+str(100+record['month'])+record['author'], reverse=True)
makeGalleryPage(records)

# -----------------------------------------------------------------
