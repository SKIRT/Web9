# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This repository holds the hand-written source for the SKIRT project web site (https://www.skirt.ugent.be) — the community/documentation pages, published as HTML via Doxygen. It does **not** contain the SKIRT/PTS API reference documentation itself; that's generated directly from Doxygen comments and the SMILE schema in the separate `SKIRT9` and `PTS9` repositories (sibling directories, normally at `../../SKIRT9/git` and `../../PTS9/pts`) as part of the build below.

The Web9 repository does not follow the fork-and-pull workflow used by `SKIRT9`/`PTS9` — it currently has a single (administrator) contributor, so changes are pushed directly to `master`.

## Content structure (`root/`)

- `root/text/` — the hand-written page source, in Doxygen-flavored text files (`\page`, `\section`, etc.), organized into numbered top-level sections that map directly to the site's navigation:
  - `10-Home`, `20-Community` (`21-Publications`, `22-Benchmarks`, `23-Contributing`, `24-Legal`, `25-Contact`)
  - `30-Documentation`, with four guides as subsections: `31-InstallationGuide`, `32-UserGuide` (with `Reading`/`Tutorials` subdirectories), `33-DeveloperGuide`, `34-AdministratorGuide`
  - `40-Reference` — a landing page only; the actual reference content is generated (see below)
- `root/text-generated/` — Doxygen input pages that are *generated* (by Python scripts run from `stageWebSite.sh`, not hand-edited) from other sources: the publications database, the SKIRT resource-pack directory listing, and — most relevantly for SKIRT/PTS development — `SkiFileHelpProperties.txt`/`SkiFileHelpSubclasses.txt`, derived from the SMILE schema produced by the SKIRT build.
- `root/images/` — embedded images, mirroring the `text/` section structure. Use PNG (or JPEG for photos); do not embed PDFs.

Each `.txt` page file is a single Doxygen `\page` (occasionally with `\section`/`\subsection`); the page's symbolic name (used in `\ref` cross-links elsewhere) is the first identifier after `\page`, not the filename.

## Building and publishing

From the repo root (`git/` — scripts assume this as the working directory):

```bash
./makeHTML.sh          # macOS only: builds just this repo's own hand-written pages into a sibling ../html, for a quick local preview (skips reference docs generated from SKIRT9/PTS9 source and Python-generated pages)
./stageWebSite.sh       # full build: generates the Python-derived pages, then runs Doxygen over this repo plus the SKIRT9/PTS9 source trees, into ../stage
./publishWebSite.sh     # copies ../stage to the production web server
```

Before staging, `SKIRT9` (including `doxstyle` and `MakeUp`) must be built for the current `master`, since the ski-file reference and some Doxygen tooling depend on it. After staging, open `../stage/index.html` locally and check updated pages before publishing.

## When working on the SKIRT9/PTS9 code instead

If you're in this repo because a code change elsewhere needs a matching documentation update, the most likely places to touch are in `root/text/33-DeveloperGuide/` (architecture/coding-convention docs) or `root/text/32-UserGuide/` (user-facing behavior). The generated `text-generated/SkiFileHelp*.txt` pages update themselves from the SMILE schema and should not be hand-edited.
