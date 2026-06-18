# n12nrl189 left200/right95 NICG+SMC 10x-faster 50-cycle minimal package

This directory is the minimal runnable package for another computer.

## Model

- 12 nucleosomes, left terminal linker = 200 beads = 2100 bp.
- Right terminal linker = 95 beads = 997.5 bp.
- SMC has already been inserted into the hybrid data stored in `data_chunks/`.
- Units: LAMMPS `real`, length in Angstrom.
- Timestep: 10 fs.
- Tension: 0.1 pN addforce on atom 499 and atom 498.
- Target linker atom: 598.
- Belt linker atom: 560.
- SMC lower-site target distance: 28.061 Angstrom.

## Files

- `data_chunks/data.hybrid_smc_nicg.part_*`: split starting NICG+SMC hybrid data.
- `assemble_data.py`: rebuilds `data.hybrid_smc_nicg` from the chunks.
- `in.bond_settings`: NICG bond settings included by LAMMPS inputs.
- `generate_random50cycle_replicates.py`: creates 3 replicate run directories and schedules.
- `run_replicates_with_retry.py`: runs prep + 50 cycles with retry from per-cycle checkpoints.
- `.gitignore`: ignores large generated dumps, logs, restarts, and per-cycle data outputs.

## Generate replicate inputs

First assemble the data file, then generate replicate inputs:

```bash
python3 assemble_data.py
python3 generate_random50cycle_replicates.py
```

This creates:

- `replicate_01_seed20260618`
- `replicate_02_seed20260619`
- `replicate_03_seed20260620`

Each replicate contains `in.prep_loading_relax`, `in.cycle_001` to `in.cycle_050`, and `random_cycle_schedule.csv`.

## Run

Set `LAMMPS_BIN` if needed:

```bash
export LAMMPS_BIN=/path/to/lmp
export OMP_NUM_THREADS=4
python3 run_replicates_with_retry.py --replicate all
```

Run one replicate only:

```bash
python3 run_replicates_with_retry.py --replicate replicate_01_seed20260618
```

The runner retries a failed cycle up to 3 times if the log contains ERROR, lost atoms, missing bond atoms, Bad FENE, non-numeric coordinates, or NaN.

## Expected runtime

Mean per replicate: about 1.204 billion steps = about 12.04 us at 10 fs. On the Apple M5 Pro estimate about 21-24 hours per replicate with OpenMP 4 threads. Three sequential replicates: about 63-72 hours. Three concurrent 4-thread replicates: roughly 30-42 hours depending on CPU contention.
