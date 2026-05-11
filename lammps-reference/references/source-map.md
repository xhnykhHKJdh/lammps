# LAMMPS Reference Source Map

## Local Sources

- LAMMPS manual PDF: `/home/rs4223/Downloads/lammps-22Jul2025/doc/Manual.pdf`
- LAMMPS documentation directory: `/home/rs4223/Downloads/lammps-22Jul2025/doc`
- LAMMPS documentation source: `/home/rs4223/Downloads/lammps-22Jul2025/doc/src`
- Extracted manual text: `references/lammps-manual-22Jul2025.txt`
- Manual release line: `Release 22 Jul 2025 Update 1`
- Manual size: 3010 PDF pages, 159741 extracted text lines
- Tutorial site repository: `references/lammpstutorials.github.io`
- Tutorial site commit: `d2812da`, dated `2025-10-02 08:50:40 +0200`, subject `removed accolades`
- Tutorial inputs repository: `references/lammpstutorials.github.io/.dependencies/lammpstutorials-inputs`
- Tutorial inputs commit: `dd3dce7`, dated `2025-10-01 08:41:24 +0200`, subject `updated DOI`

## LAMMPS Doc Source Map

Use `/home/rs4223/Downloads/lammps-22Jul2025/doc/src` as the preferred structured source for manual content. It contains 1031 `.rst` files and is easier to inspect than the extracted PDF text.

- `Manual.rst`: top-level Sphinx table of contents for User Guide, Programmer Guide, and Command Reference.
- `commands_list.rst`: toctree list of general LAMMPS input commands.
- `fixes.rst`, `computes.rst`, `pairs.rst`, `bonds.rst`, `angles.rst`, `dihedrals.rst`, `impropers.rst`, `dumps.rst`: command-family index pages.
- `fix_*.rst`: 229 fix command/style pages.
- `compute_*.rst`: 154 compute command/style pages.
- `pair_*.rst`: 167 pair style pages.
- `bond_*.rst`: 28 bond style/command pages.
- `angle_*.rst`: 30 angle style/command pages.
- `dihedral_*.rst`: 20 dihedral style/command pages.
- `improper_*.rst`: 17 improper style/command pages.
- `dump_*.rst`: 8 dump style pages.
- `Developer*.rst`, `Modify*.rst`, `Programmer*.rst`, `Classes*.rst`, `Library*.rst`, `Python*.rst`: implementation, extension, API, and code-organization guidance.
- `Howto_*.rst`: applied workflows such as thermostatting, barostats, restart files, visualization, Python, walls, diffusion, viscosity, and force-field setup.
- `Build*.rst`, `Install*.rst`, `Run*.rst`: build, install, and execution guidance.

When a command has a natural source file, go directly to it. Examples: `fix_langevin.rst` for `fix langevin`, `pair_reaxff.rst` for `pair_style reaxff`, `read_data.rst` for `read_data`, and `thermo_style.rst` for `thermo_style`.

## Tutorial Text Map

- `docs/sphinx/source/non-tutorials/`: prerequisites, command line usage, running LAMMPS, GUI usage, glossary, solutions, contact, bibliography.
- `docs/sphinx/source/tutorial1/`: Lennard-Jones fluid, beginner input scripts, basic minimization and MD, exercises.
- `docs/sphinx/source/tutorial2/`: pulling/breaking a carbon nanotube.
- `docs/sphinx/source/tutorial3/`: polymer in water.
- `docs/sphinx/source/tutorial4/`: nanosheared electrolyte.
- `docs/sphinx/source/tutorial5/`: reactive silicon dioxide with ReaxFF.
- `docs/sphinx/source/tutorial6/`: water adsorption in silica, GCMC.
- `docs/sphinx/source/tutorial7/`: free energy calculation, umbrella sampling, WHAM.
- `docs/sphinx/source/tutorial8/`: reactive molecular dynamics and polymerization.

## Top-Level Tutorial Input Scripts

- `tutorial1/initial.lmp`
- `tutorial1/improved.min.lmp`
- `tutorial1/improved.md.lmp`
- `tutorial2/unbreakable.lmp`
- `tutorial2/breakable.lmp`
- `tutorial2/breakable-with-tip.lmp`
- `tutorial3/merge.lmp`
- `tutorial3/water.lmp`
- `tutorial3/pull.lmp`
- `tutorial3/pull-with-tip.lmp`
- `tutorial4/create.lmp`
- `tutorial4/equilibrate.lmp`
- `tutorial4/shearing.lmp`
- `tutorial5/relax.lmp`
- `tutorial5/decorate.lmp`
- `tutorial5/deform.lmp`
- `tutorial6/generate.lmp`
- `tutorial6/cracking.lmp`
- `tutorial6/gcmc.lmp`
- `tutorial7/free-sampling.lmp`
- `tutorial7/umbrella-sampling.lmp`
- `tutorial8/mixing.lmp`
- `tutorial8/polymerize.lmp`

There are 73 tutorial input scripts matching `*.lmp`, `*.lammps`, or `*.in` across the inputs repository, including exercise and video examples.

## Manual Table Of Contents Anchors

The extracted manual begins with a full table of contents. Useful line anchors:

- Line 22: `I User Guide`
- Line 538: `II Programmer Guide`
- Line 766: `III Command Reference`
- Line 196: User guide `5 Commands`
- Line 485: User guide `11 Errors`
- Line 4860: Command reference `4 Pair Styles`
- Line 6370: Command reference `5 Bond Styles`
- Line 6570: Command reference `6 Angle Styles`
- Line 6773: Command reference `7 Dihedral Styles`
- Line 6907: Command reference `8 Improper Styles`
- Line 7019: Command reference `9 Dump Styles`
