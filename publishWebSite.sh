#!/bin/bash
# (use "chmod +rx scriptname" to make script executable)
#
# This script publishes the SKIRT web site to the Ghent University web host.
#
# Instructions:
#   - use on Mac OS X only
#   - you need write access to the SKIRT area of the Ghent University web host
#   - first run the stageWebSite.sh script
#   - run this script with "git" as default directory
#
# This script assumes that:
#    (a) the stage directory contains the possibly updated web site to be published
#    (b) the public directory contains an exact mirror (including time stamps) of the currently published web site
#
# The script proceeds in two steps:
#   (1) copy the contents from stage to public, updating only files that were actually changed,
#       using checksums to verify this rather than time stamps
#   (2) copy the contents from public to the web host, updating only files with a different time stamp
#
# This procedure allows the expensive step (calculating the checksums) to happen on the local file system,
# while still restricting the remote copy operation to files that actually did change.
#

# Mount the webhost at a local mount point
mkdir -p ../webhost
read -s -p "Password for web host user $USER: " PASSWORD
echo
#mount -t smbfs //UGENT\;$USER:$PASSWORD@files.ugent.be/$USER/www/shares/skirt ../webhost
mount -t smbfs //UGENT\;$USER@files.ugent.be/$USER/www/shares/skirt ../webhost
if [ $? -ne 0 ]
  then exit
fi

# Make local copy, using checksums to update only files that were actually changed
rsync -chr --delete ../stage/ ../public/
find ../public -name "*.DS_Store" -type f -delete  # remove hidden files created by Mac OS finder

# Make remote copy, updating only files with a different time stamp
rsync -hrtv --delete-after --exclude '.htaccess' --exclude '.default.html' ../public/ ../webhost/WWW/

# Unmount the webhost and remove the mount point
umount ../webhost
rm -d ../webhost
