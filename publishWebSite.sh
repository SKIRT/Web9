#!/bin/bash
# (use "chmod +rx scriptname" to make script executable)
#
# This script publishes the SKIRT web site to the Ghent University web host.
#
# Instructions:
#   - use on Mac OS X only
#   - you need write access to the SKIRT area of the Ghent University web host share
#   - first run the stageWebSite.sh script with the master branch checked out for SKIRT and PTS
#   - run this script with "git" as default directory
#
# Usage:
#   publishWebSite.sh                runs both steps below, in sequence (the normal case)
#   publishWebSite.sh --local-only   runs step 1 only
#   publishWebSite.sh --remote-only  runs step 2 only, reusing the change list left behind by
#                                    the last --local-only (or plain) run -- use this to retry
#                                    after step 2 fails partway through, WITHOUT re-running step 1
#                                    first: re-running step 1 would compare stage against the
#                                    already-updated public dir, see no differences, and silently
#                                    forget about whatever step 2 hadn't transferred yet
#
# This script assumes that:
#    (a) the stage directory contains the possibly updated web site to be published
#    (b) the public directory contains an exact mirror (including time stamps) of the currently published web site
#
# The script proceeds in two steps:
#   (1) copy the contents from stage to public, updating only files that were actually changed,
#       using checksums to verify this rather than time stamps -- and record exactly which paths
#       were added, updated or removed while doing so
#   (2) mount the web host and replay that pre-computed list of adds/updates/removals directly,
#       instead of letting rsync rediscover what changed by comparing against the remote tree
#

CHANGED=../rsync-changed.txt
DELETED=../rsync-deleted.txt
ITEMIZE=../rsync-itemize.log

MODE=both
case "$1" in
  --local-only)  MODE=local ;;
  --remote-only) MODE=remote ;;
  "") ;;
  *) echo "usage: $0 [--local-only | --remote-only]"; exit 1 ;;
esac

# ---- Step 1: figure out what changed (local only, no mount needed) ----
if [ "$MODE" = both ] || [ "$MODE" = local ]; then

  if [ -f "$CHANGED" ] || [ -f "$DELETED" ]; then
    echo "A change list from a previous run is still pending ($CHANGED / $DELETED)."
    echo "Run '$0 --remote-only' first to finish publishing it, or remove those two files"
    echo "to discard it and recompute from scratch."
    exit 1
  fi

  # remove hidden files created by Mac OS finder
  find ../stage -name "*.DS_Store" -type f -delete
  find ../public -name "*.DS_Store" -type f -delete

  # Make local copy, using checksums to update only files that were actually changed,
  # capturing exactly which paths were touched or removed. (--itemize-changes isn't usable
  # on this rsync build, so this parses plain -v output instead.)
  rsync -chr --delete -v ../stage/ ../public/ > "$ITEMIZE"
  grep '^deleting ' "$ITEMIZE" | sed 's/^deleting //' > "$DELETED"
  grep -v '^Transfer starting:' "$ITEMIZE" \
    | grep -v '^deleting ' \
    | grep -v '^sent ' \
    | grep -v '^total size is ' \
    | grep -v '^$' \
    | grep -v '/$' > "$CHANGED"
  rm -f "$ITEMIZE"

  echo "Local step done: $(wc -l < "$CHANGED" | tr -d ' ') file(s) to copy, $(wc -l < "$DELETED" | tr -d ' ') to remove."
fi

# ---- Step 2: replay that change list on the web host ----
if [ "$MODE" = both ] || [ "$MODE" = remote ]; then

  if [ ! -f "$CHANGED" ] || [ ! -f "$DELETED" ]; then
    echo "No pending change list found ($CHANGED / $DELETED)."
    echo "Run '$0' or '$0 --local-only' first."
    exit 1
  fi

  # Mount the webhost at a local mount point
  mkdir -p ../webhost
  mount -t smbfs -o nostreams //UGENT\;$USER@files.ugent.be/$USER/www/shares/skirt ../webhost
  if [ $? -ne 0 ]
    then exit
  fi

  # Copy exactly the files step 1 identified as added/updated
  rsync -htv --ignore-times --files-from="$CHANGED" --exclude '.htaccess' --exclude '.default.html' ../public/ ../webhost/WWW/
  COPY_STATUS=$?

  # Remove exactly the paths step 1 identified as deleted
  DELETE_STATUS=0
  if [ $COPY_STATUS -eq 0 ]; then
    while IFS= read -r path; do
      case "$path" in
        .htaccess|.default.html) continue ;;
      esac
      rm -rf -- "../webhost/WWW/$path"
      DELETE_STATUS=$?
      echo "deleted $path"
      [ $DELETE_STATUS -ne 0 ] && break
    done < "$DELETED"
  fi

  # Unmount the webhost and remove the mount point
  umount ../webhost
  rm -d ../webhost

  if [ $COPY_STATUS -ne 0 ] || [ $DELETE_STATUS -ne 0 ]; then
    echo "Remote step failed -- change list left in place; retry with '$0 --remote-only'."
    exit 1
  fi

  rm -f "$CHANGED" "$DELETED"
  echo "Remote step done: web site published."
fi
