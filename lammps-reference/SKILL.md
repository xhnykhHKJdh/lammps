---
name: lammps-reference
description: Local LAMMPS 22Jul2025 reference workflow backed by the user's Manual.pdf, the structured LAMMPS doc/src Sphinx source tree, and the lammpstutorials.github.io tutorial sources. Use when Codex needs to answer, debug, write, modify, or validate LAMMPS input scripts; look up command syntax, fixes, computes, pair styles, molecule/data file formats, error messages, build/run guidance, developer/programmer documentation, or examples from the LAMMPS tutorials.
---

# LAMMPS Reference

## Core Workflow

Use local sources before answering version-sensitive LAMMPS questions. Prefer the structured LAMMPS `doc/src` `.rst` files for command syntax and documentation details, use the extracted manual text as a broad-search fallback, and use the tutorial repository for runnable examples and beginner-oriented patterns.

1. Search `/home/rs4223/Downloads/lammps-22Jul2025/doc/src` first for command syntax, restrictions, defaults, package requirements, howto pages, developer notes, and API/programmer documentation.
2. Search `references/lammps-manual-22Jul2025.txt` when you need a broad manual sweep or table-of-contents line anchors from the generated PDF.
3. Search tutorial text for conceptual walkthroughs and expected workflows.
4. Search tutorial input scripts when adapting or comparing concrete input-file patterns.
5. When giving a technical answer, cite the local file path and line number you used when practical.

## Local Sources

- Source map: `references/source-map.md`
- LAMMPS doc directory: `/home/rs4223/Downloads/lammps-22Jul2025/doc`
- LAMMPS doc source: `/home/rs4223/Downloads/lammps-22Jul2025/doc/src`
- Extracted manual text: `references/lammps-manual-22Jul2025.txt`
- Original manual PDF: `/home/rs4223/Downloads/lammps-22Jul2025/doc/Manual.pdf`
- Tutorial docs: `references/lammpstutorials.github.io/docs/sphinx/source`
- Tutorial input files: `references/lammpstutorials.github.io/.dependencies/lammpstutorials-inputs`

Read `references/source-map.md` when you need LAMMPS doc source mapping, tutorial topic mapping, snapshot versions, or the main manual table-of-contents anchors.

## Search Helper

Use the bundled helper for consistent searches:

```bash
python3 /home/rs4223/.codex/skills/lammps-reference/scripts/lammps_search.py "fix langevin command" --where doc-src -i
python3 /home/rs4223/.codex/skills/lammps-reference/scripts/lammps_search.py "pair_style reaxff" --where doc-src -i -F
python3 /home/rs4223/.codex/skills/lammps-reference/scripts/lammps_search.py "fix langevin" --where manual -i -F
python3 /home/rs4223/.codex/skills/lammps-reference/scripts/lammps_search.py "neighbor" --where tutorials -i
python3 /home/rs4223/.codex/skills/lammps-reference/scripts/lammps_search.py "pair_style reaxff" --where inputs -i -F
```

Use `--where doc-src`, `--where lammps-doc`, `--where manual`, `--where tutorials`, `--where tutorial-text`, or `--where inputs` to narrow scope. Add `-C 8` for larger excerpts and `-F` for exact command strings.

Direct `rg` is also fine when a path-specific search is clearer:

```bash
rg -n -C 5 "Syntax|Examples|Restrictions" /home/rs4223/Downloads/lammps-22Jul2025/doc/src/fix_langevin.rst
rg -n "Developer|Programmer|Library|Python" /home/rs4223/Downloads/lammps-22Jul2025/doc/src
rg -n -C 5 "Syntax|Examples|Restrictions" /home/rs4223/.codex/skills/lammps-reference/references/lammps-manual-22Jul2025.txt
rg -n "fix\\s+nvt|thermo_style" /home/rs4223/.codex/skills/lammps-reference/references/lammpstutorials.github.io/.dependencies/lammpstutorials-inputs
```

## Lookup Patterns

- For a LAMMPS command: open the likely `.rst` file under `doc/src` first, then inspect `Syntax`, `Examples`, `Description`, `Restrictions`, `Related commands`, and `Default` sections.
- For a style command such as `pair_style`, `fix`, `compute`, `dump`, or `thermo_style`: map the command to its source file when possible. Examples: `fix langevin` -> `fix_langevin.rst`, `pair_style reaxff` -> `pair_reaxff.rst`, `compute msd` -> `compute_msd.rst`, `dump custom` -> `dump.rst` or `dump_custom.rst` if present.
- For a runtime error: search the exact message in `doc/src/Errors*.rst` and the extracted manual text, then search local input scripts for nearby command patterns that commonly trigger it.
- For building or running LAMMPS: use manual install/build/run sections and verify local executable/package availability from the actual local LAMMPS build before making strong claims.
- For developer or source-code-oriented questions: use `doc/src/Developer*.rst`, `doc/src/Modify*.rst`, `doc/src/Classes*.rst`, `doc/src/Library*.rst`, and `doc/src/Python*.rst` before reaching for the generated PDF. Treat `doc/src` as documentation source; if implementation behavior is at issue, inspect the real C++ source under `/home/rs4223/Downloads/lammps-22Jul2025/src` as a separate step.
- For adapting a tutorial: read the matching `.rst` walkthrough and the corresponding input scripts/data files. Preserve tutorial file dependencies such as molecule files, data files, force-field files, and restart files.

## Practical Guardrails

- Treat the manual as the authority when a tutorial uses a shorthand or older habit.
- Do not assume a package, pair style, or fix is compiled into the user's local executable. Check with the executable or source tree if package availability matters.
- Keep generated input scripts explicit about `units`, `atom_style`, `boundary`, `read_data` or atom creation, force-field coefficients, neighbor settings, fixes, computes, thermo output, dumps, and timestep/run controls.
- When validating an input file, distinguish syntax validity from physical validity. The manual can confirm syntax; the simulation setup still needs domain checks for force field, units, timestep, equilibration, and boundary conditions.
