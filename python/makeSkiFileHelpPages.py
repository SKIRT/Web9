#!/usr/bin/env python
# -*- coding: utf8 -*-

# This Python script generates Doxygen input pages from the contents of the skirt.smile schema definition file.
# To be completed.
#
# The script is executed as part of the "makeHTML" process, *before* running Doxygen on this part of the web site.
# It accepts two optional command line arguments specifying the directory holding the skirt.smile file
# and the directory holding the output file(s) of this script (i.e. input for Doxygen).
#
# Developer note: this script has been developed and tested with Python 3.7.2.
#

# -----------------------------------------------------------------

import sys
import lxml.etree as etree

# -----------------------------------------------------------------

# This function returns an attribute value or element tag as a string. The first argument is an XPath expression
# relative to the document root that selects exactly one element. The second argument is an attribute name string
# or None. In the latter case, the element tag (corresponding to the SMILE property or type name) is returned.
# If the element is not found, there are multiple elements, or the selected element does not have the specified
# attribute, an error is raised.
def getStringAttribute(smiletree, xpath, attribute):
    # get the element(s) and verify there is exactly one
    elems = smiletree.xpath(xpath)
    if len(elems) == 0: raise ValueError("Smile file has no element for xpath '{}'".format(xpath))
    if len(elems) > 1: raise ValueError("Smile file has multiple elements for xpath '{}'".format(xpath))
    elem = elems[0]
    if not etree.iselement(elem): raise ValueError("Smile file xpath '{}' returns a non-element".format(xpath))

    # get the attribute value or the element tag
    value = elem.get(attribute) if attribute is not None else elem.tag
    if not isinstance(value, str): raise ValueError("Smile file element for xpath '{}' has no attribute '{}'" \
                                                    .format(xpath, attribute))
    return value

# This function returns a list including the string values of a particular attribute for a number of elements.
# The first argument is an XPath expression relative to the document root that selects one or more elements.
# The second argument is the attribute name (the attribute must be present for all selected elements).
# If the attribute argument is None, the element tags (corresponding to SMILE type names) are returned instead.
# If no elements are found, the function returns an empty list. If one or more of the selected element does
# not have the specified attribute, an error is raised.
def getStringAttributes(smiletree, xpath, attribute):
    values = []
    # loop over the element(s)
    for elem in smiletree.xpath(xpath):
        if not etree.iselement(elem): raise ValueError("Smile file xpath '{}' returns a non-element".format(xpath))
        # get the attribute value or the element tag
        value = elem.get(attribute) if attribute is not None else elem.tag
        if not isinstance(value, str): raise ValueError("Smile file element for xpath '{}' has no attribute '{}'" \
                                                        .format(xpath, attribute))
        values.append(value)
    return values

# -----------------------------------------------------------------

# This function returns True if the candidate item inherits the base item, or False if not.
def inheritsItem(smiletree, candidate, base):

    while True:
        # if the candidate matches the base type (possibly after iteration), there is inheritance
        if candidate == base:
            return True
        # if the candidate matches the topmost type (usually after iteration), there is no inheritance
        if candidate == "SimulationItem":
            return False
        # replace the candidate by the candidate's base type and try again
        candidate = getStringAttribute(smiletree, "//Type[@name='{}']".format(candidate), "base")

# -----------------------------------------------------------------

# This function returns the title string for the given item
def titleForItem(smiletree, item):
    title = getStringAttribute(smiletree, "//Type[@name='{}']".format(item), "title")
    return title.replace("SED", "%SED")  # avoid hyperlink to the SED class

# -----------------------------------------------------------------

# This function returns a list of XML elements representing the properties of the given item,
# including inherited properties, in the order they would appear in the Q&A
def propertiesForItem(smiletree, item):
    propelems = [ ]

    while len(item) > 0:
        # get the XML element for the given item
        itemelem = smiletree.xpath("//Type[@name='{}']".format(item))[0]

        # get the index of the first base property that should be added *after* the sub-properties, or None
        subPropertyIndex = itemelem.get("subPropertyIndex")

        # get the properties for this item
        propelemsbase = itemelem.xpath("properties/*".format(item))

        if subPropertyIndex is None:
            propelems = propelemsbase + propelems
        else:
            subPropertyIndex = int(subPropertyIndex)
            propelems = propelemsbase[:subPropertyIndex] + propelems + propelemsbase[subPropertyIndex:]

        # replace the item by the item's base type and loop again
        item = itemelem.get("base")

    return propelems

# -----------------------------------------------------------------

# get the directory holding the skirt.smile file
smiledir = sys.argv[1] if len(sys.argv)>1 else "."
if not smiledir.endswith("/"): smiledir += "/"

# get the output file directory
outdir = sys.argv[2] if len(sys.argv)>2 else "."
if not outdir.endswith("/"): outdir += "/"

# -----------------------------------------------------------------

# load the XML tree from the smile file
smiletree = etree.parse(smiledir+"skirt.smile")

# get the SKIRT version
version = getStringAttribute(smiletree, "//smile-schema", "producer")

# get the set of simulation items that are mentioned as a base in Item or ItemList properties
list0 = getStringAttributes(smiletree, "//Schema", "type")
list1 = getStringAttributes(smiletree, "//ItemProperty", "base")
list2 = getStringAttributes(smiletree, "//ItemListProperty", "base")
baseItems = sorted(set(list0+list1+list2))

# get the list of concrete simulation items
concreteItems = sorted(getStringAttributes(smiletree, "//Type[@concrete='true']", "name"))

# -----------------------------------------------------------------

# --- Generate a file offering a list of subclasses for each base class ---

with open(outdir + "SkiFileHelpSubclasses.txt", 'w') as pg:
    # write page header
    pg.write("/**\n")
    pg.write("\\page SkiFileHelpSubclasses List of subclasses for each base class\n")
    pg.write("<em>{}</em>\n".format(version))
    pg.write("\\section SkiFileHelpSubclassesIntro Introduction\n")
    pg.write('''This page lists the subclasses for each SKIRT class that may occur as base class name a ski file. <p>
             The sections are listed alphabetically on class name. To quickly locate the section for a given class,
             use your browser's find function and precede the class name with a - (dash).
             ''')

    # write links to other pages
    #for categ in categories:
    #    for order in orderings:
    #        pg.write("- \\ref Publications" + categ + order + "\n")
    #pg.write("\n")

    # for each base item...
    for baseItem in baseItems:
        # write section header for base item
        pg.write("\n")
        pg.write('\\subsection SkiFileHelpBase{0} -{0}\n[\\ref {0} "docs"] : {1} \n' \
                    .format(baseItem, titleForItem(smiletree, baseItem)))

        # write table header for base item
        pg.write("\n")
        pg.write('| Subclass | | | Description |\n'.format(baseItem, titleForItem(smiletree, baseItem)))
        pg.write("| :-- | :--: | :--: | :-- |\n")

        # write table entry for each concrete inheriting item
        inheritingItems = [item for item in concreteItems if inheritsItem(smiletree, item, baseItem)]
        for item in inheritingItems:
            pg.write('| %{0} | \\ref SkiFileHelpConcrete{0} "props" | \\ref {0} "docs"| {1} |\n' \
                     .format(item, titleForItem(smiletree, item)))

    # write page footer
    pg.write("\n")
    pg.write("*/\n")

# -----------------------------------------------------------------

# --- Generate a file offering a list of properties for each concrete class ---

with open(outdir + "SkiFileHelpProperties.txt", 'w') as pg:
    # write page header
    pg.write("/**\n")
    pg.write("\\page SkiFileHelpProperties List of properties for each concrete class\n")
    pg.write("<em>{}</em>\n".format(version))
    pg.write("\\section SkiFileHelpPropertiesIntro Introduction\n")
    pg.write('''This page lists the properties for each concrete SKIRT class that may occur as an object in a ski file. <p>
             The sections are listed alphabetically on class name. To quickly locate the section for a given class,
             use your browser's find function and precede the class name with a - (dash).
             ''')

    # for each concrete item...
    for item in concreteItems:
        # get a list of XML elements representing the properties of this item, including inherited properties,
        # and split the list into scalar and compound properties
        properties = propertiesForItem(smiletree, item)
        scalarproperties = [ property for property in properties if not "Item" in property.tag]
        compoundproperties = [ property for property in properties if "Item" in property.tag]

        # write section header for item
        pg.write("\n")
        pg.write('\\subsection SkiFileHelpConcrete{0} -{0}\n[\\ref {0} "docs"] : {1} \n' \
                    .format(item, titleForItem(smiletree, item)))

        if len(scalarproperties) > 0:
            # write table header for scalar properties
            pg.write("\n")
            pg.write("| Scalar Property | | Type | Description\n")
            pg.write("| :-- | :--: | :-- | :-- |\n")

            # write scalar properties
            for property in scalarproperties:
                pg.write('| {0} | \\ref {3}::{0}() "docs" | {1} | {2} |\n' \
                         .format(property.get("name"), property.tag[:-8],
                                 property.get("title").replace("SED", "%SED"), item))
                if "Enum" in property.tag:
                    for enumValue in property.xpath("enumValues/*"):
                        pg.write("| | | --> {} | {} |\n" \
                                 .format(enumValue.get("name"), enumValue.get("title").replace("SED", "%SED")))

        if len(compoundproperties) > 0:
            # write table header for compound properties
            pg.write("\n")
            pg.write("| Compound Property | | Type | Base Class | | Description\n")
            pg.write("| :-- | :--: | :-- | :-- | :--: | :-- |\n")

            # write compound properties
            for property in compoundproperties:
                pg.write('| {0} | \\ref {4}::{0}() "docs" | %{1} | %{2} | \\ref SkiFileHelpBase{2} "subclasses" | {3} |\n' \
                         .format(property.get("name"), property.tag[:-8],
                                 property.get("base"), property.get("title").replace("SED", "%SED"), item))

    # write page footer
    pg.write("\n")
    pg.write("*/\n")

# -----------------------------------------------------------------
