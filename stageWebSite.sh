#!/bin/bash
# (use "chmod +rx scriptname" to make script executable)
#
# This script builds the HTML pages for the complete SKIRT project web site,
# including the documentation for both SKIRT and PTS. The resulting directory
# and file tree can be copied (published) directly to the SKIRT web site server.
#
# This script DOES NOT stage downloadable/viewable data files (other than images
# that form an integral part of the documentation). Because of size restrictions
# on the UGent web site server and in GitHub repositories, these data files are
# provided for download from a seperate server.
#
# Instructions:
#   - use on macOS only
#   - place the Resources9 and ResourcesC directories next to Web9 in a common parent directory
#   - place the SKIRT9 and PTS9 repositories next to Web9 in a common parent directory
#   - git pull the most recent master branch version of both SKIRT9 and PTS9
#   - build that version of SKIRT9, including MakeUp (to generate the skirt.smile file)
#   - run this script with the directory in which it resides as the current directory
#
# This script resides in the Web9/git directory and should be executed with that
# directory as the current directory. The resulting HTML pages are placed inside
# the Web9/stage directory (which is created if necessary). All internal links are
# relative so they can be tested locally on the staged copy before publishing.
# Links to downloadable/viewable data files are absolute because these files are
# provided on a seperate server. Assuming the data files are properly published to
# that server, these links can be tested locally on the staged copy as well.
#

# Generate Doxygen input pages from publications database and from smile schema file
mkdir -p root/text-generated
python/makePublicationPages.py root/text/21-Publications ../../ResourcesC/Publications root/text-generated
python/makeSkiFileHelpPages.py ../../SKIRT9/release/MakeUp/schemas root/text-generated
python/makeDownloadPage.py ../../Resources9/Publish root/text-generated

# Generate html documentation in the staging area next to our git folder
mkdir -p ../stage
mkdir -p staging/tagfiles-generated
/Applications/Doxygen.app/Contents/Resources/doxygen staging/doxygen_skirt.txt
/Applications/Doxygen.app/Contents/Resources/doxygen staging/doxygen_pts.txt
/Applications/Doxygen.app/Contents/Resources/doxygen staging/doxygen_root.txt

# Copy the 'mouse over' SKIRT logo
cp staging/SkirtLogoSmall-home.png ../stage/skirt9/
cp staging/SkirtLogoSmall-home.png ../stage/pts9/
cp staging/SkirtLogoSmall-home.png ../stage/root/

# Copy redirecting index.html files
cp staging/index_root.html ../stage/index.html
#mkdir -p ../stage/makeup9 && cp staging/index_makeup9.html ../stage/makeup9/index.html

# Copy dustpedia files
rsync -qrt --delete dustpedia ../stage

# Obtain the MathJax repository if it is not yet present
if [ ! -d ../stage/mathjax ]; then

    # Clone the repository and checkout version 3.0.5 (April 2020)
    git clone https://github.com/mathjax/MathJax.git ../stage/mathjaxtmp
    git -C ../stage/mathjaxtmp checkout 3.0.5

    # Move the required files
    mkdir -p ../stage/mathjax
    mv ../stage/mathjaxtmp/es5/tex-chtml.js ../stage/mathjax/MathJax.js
    mv ../stage/mathjaxtmp/es5/input ../stage/mathjax/
    mv ../stage/mathjaxtmp/es5/output ../stage/mathjax/

    # Remove the repository
    rm -rf ../stage/mathjaxtmp
fi
