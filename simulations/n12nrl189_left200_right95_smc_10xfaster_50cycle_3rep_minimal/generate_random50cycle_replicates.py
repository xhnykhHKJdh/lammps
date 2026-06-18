from pathlib import Path
import csv
import random
import shutil


HERE = Path(__file__).resolve().parent

REPLICATES = [
    ("replicate_01_seed20260618", 20260618),
    ("replicate_02_seed20260619", 20260619),
    ("replicate_03_seed20260620", 20260620),
]

DT_FS = 10.0
CYCLES = 50
PRE_DNA_STEPS = 2_000_000
PRE_SMC_STEPS = 2_000_000
TENSION_PN = 0.1
DUMPFREQ = 1_000_000
THERMOFREQ = 1_000_000
BELT_STRENGTH_SCALE = 1.0
APO_RETURN_RAMP_STEPS = 100_000
APO_RETURN_RAMP_CHUNKS = 10

LEFT_TERMINAL_ID = 499
RIGHT_TERMINAL_ID = 498
TARGET_LINKER_ID = 598
BELT_LINKER_ID = 560

MEAN_STEPS = {
    "APO_PRE": 2_000_000,
    "ATP_BOUND": 16_000_000,
    "ADP_BOUND": 4_000_000,
    "APO_RETURN": 2_000_000,
}

STAGE_ORDER = ["APO_PRE", "ATP_BOUND", "ADP_BOUND", "APO_RETURN"]


def sample_schedule(seed):
    rng = random.Random(seed)
    cumulative = PRE_DNA_STEPS + PRE_SMC_STEPS
    rows = []
    for cycle in range(1, CYCLES + 1):
        for stage in STAGE_ORDER:
            sampled = max(1, int(round(rng.expovariate(1.0 / MEAN_STEPS[stage]))))
            cumulative += sampled
            rows.append(
                {
                    "cycle": cycle,
                    "stage": stage,
                    "sampled_steps": sampled,
                    "cumulative_step": cumulative,
                }
            )
    return rows


def write_schedule(rep_dir, rows):
    with (rep_dir / "random_cycle_schedule.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["cycle", "stage", "sampled_steps", "cumulative_step"],
        )
        writer.writeheader()
        writer.writerows(rows)


def state_block(stage):
    if stage in {"APO_PRE", "APO_RETURN"}:
        return """pair_coeff      1 9    lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 10   lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 11   lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 12   lj/cut ${smc_lower_eps} ${smc_sigma} ${smc_lower_cut}
angle_coeff     4 harmonic ${smc_arm_k} ${smc_arm_apo}
improper_coeff  2 ${smc_improper2_k} ${smc_improper2_apo}
improper_coeff  3 ${smc_improper3_k} ${smc_improper3_apo}"""
    if stage == "ATP_BOUND":
        return """pair_coeff      1 9    lj/cut ${smc_bridge_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 10   lj/cut ${smc_top_eps} ${smc_sigma} ${smc_site_cut}
pair_coeff      1 11   lj/cut ${smc_middle_eps} ${smc_sigma} ${smc_site_cut}
pair_coeff      1 12   lj/cut ${smc_lower_eps} ${smc_sigma} ${smc_lower_cut}
angle_coeff     4 harmonic ${smc_arm_k} ${smc_arm_atp}
improper_coeff  2 ${smc_improper2_k} ${smc_improper2_atp}
improper_coeff  3 ${smc_improper3_k} ${smc_improper3_atp}"""
    if stage == "ADP_BOUND":
        return """pair_coeff      1 9    lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 10   lj/cut ${smc_top_eps} ${smc_sigma} ${smc_site_cut}
pair_coeff      1 11   lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 12   lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
angle_coeff     4 harmonic ${smc_arm_k} ${smc_arm_atp}
improper_coeff  2 ${smc_improper2_k} ${smc_improper2_apo}
improper_coeff  3 ${smc_improper3_k} ${smc_improper3_apo}"""
    raise ValueError(stage)


def apo_return_run_block(total_steps):
    ramp_steps = min(APO_RETURN_RAMP_STEPS, total_steps)
    remaining = total_steps - ramp_steps
    base = ramp_steps // APO_RETURN_RAMP_CHUNKS
    remainder = ramp_steps % APO_RETURN_RAMP_CHUNKS
    chunks = [
        """pair_coeff      1 9    lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 10   lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 11   lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      1 12   lj/cut ${smc_lower_eps} ${smc_sigma} ${smc_lower_cut}"""
    ]
    for index in range(1, APO_RETURN_RAMP_CHUNKS + 1):
        steps = base + (1 if index <= remainder else 0)
        if steps <= 0:
            continue
        frac = index / APO_RETURN_RAMP_CHUNKS
        arm = 130.0 + (81.3730734413 - 130.0) * frac
        improper2 = 20.0 + (135.0 - 20.0) * frac
        improper3 = 70.0 + (45.0 - 70.0) * frac
        chunks.append(
            f"""angle_coeff     4 harmonic ${{smc_arm_k}} {arm:.10f}
improper_coeff  2 ${{smc_improper2_k}} {improper2:.10f}
improper_coeff  3 ${{smc_improper3_k}} {improper3:.10f}
run             {steps}"""
        )
    chunks.append(state_block("APO_RETURN"))
    if remaining > 0:
        chunks.append(f"run             {remaining}")
    return "\n".join(chunks)


def variable_definitions():
    return f"""variable T    equal 300.0
variable epsr equal 80.0
variable eps0 equal 8.8541878E-12
variable kB   equal 1.3806505E-23
variable NA   equal 6.0221415E23
variable salt equal 150
variable e    equal 1.6021766E-19
variable ldebye_inv equal "1/sqrt( v_epsr * v_eps0 * v_kB * v_T / ( 2. * v_e * v_e * v_NA * v_salt)) * 1.0E-10"
variable ldebye_cut equal "10.0/v_ldebye_inv"
dielectric      ${{epsr}}

variable sigma      equal 35.0
variable lj_cut     equal 79.538
variable lj_cut_min equal 39.286
variable kbond      equal 0.5
variable kangle     equal 8.8
variable kpair      equal 0.115
variable kmorse     equal 2.2
variable alphamorse equal 0.3

variable smc_sigma          equal 25.0
variable smc_shell_eps      equal 0.4317975
variable smc_bridge_eps     equal 1.78848417328
variable smc_top_eps        equal 3.57696834656
variable smc_middle_eps     equal 3.57696834656
variable smc_lower_eps      equal 59.6161391094
variable smc_rep_cut        equal 28.0615512077
variable smc_site_cut       equal 35.0
variable smc_lower_cut      equal 30.0
variable smc_belt_weak_k    equal 0.00894242086641
variable smc_belt_strong_k  equal 0.298080695547
variable smc_belt_cycle_k   equal "v_smc_belt_weak_k + {BELT_STRENGTH_SCALE}*(v_smc_belt_strong_k-v_smc_belt_weak_k)"
variable smc_arm_k          equal 59.6161391094
variable smc_arm_apo        equal 81.3730734413
variable smc_arm_atp        equal 130.0
variable smc_improper2_k    equal 35.7696834656
variable smc_improper2_apo  equal 135.0
variable smc_improper2_atp  equal 20.0
variable smc_improper3_k    equal 59.6161391094
variable smc_improper3_apo  equal 45.0
variable smc_improper3_atp  equal 70.0

variable        tension_pN equal {TENSION_PN}
variable        pull equal v_tension_pN*0.01439325
variable        pull_left equal -v_pull
"""


def runtime_definitions():
    return f"""group           chromatin type 1:7
group           smc type 8:13
group           left_terminal_linker id {LEFT_TERMINAL_ID}
group           right_terminal_linker id {RIGHT_TERMINAL_ID}
group           belt_linker id {BELT_LINKER_ID}
group           smc_active_sites type 9:12
neigh_modify    exclude group smc_active_sites belt_linker

comm_modify     cutoff 250.0

fix             chrom_nve chromatin nve
fix             chrom_lan chromatin langevin ${{T}} ${{T}} 1000.0 12345
fix             smc_rigid smc rigid molecule langevin ${{T}} ${{T}} 100000.0 67890
fix             left_pull left_terminal_linker addforce v_pull_left 0.0 0.0
fix             right_pull right_terminal_linker addforce v_pull 0.0 0.0

thermo          {THERMOFREQ}
thermo_style    custom step temp pe epair ebond eangle eimp
thermo_modify   flush yes lost error

dump            hybrid all custom {DUMPFREQ} dump.${{tag}}.lammpstrj id type x y z
dump_modify     hybrid sort id

timestep        {DT_FS}
"""


def read_data_force_field():
    return """pair_style      hybrid lj/cut/coul/debye ${ldebye_inv} ${lj_cut} ${ldebye_cut} lj/cut 80.0
bond_style      hybrid harmonic morse fene/expand
angle_style     hybrid cosine harmonic
improper_style  harmonic
special_bonds   lj/coul 0.0 1.0 1.0

pair_coeff      1*7 1*7 lj/cut/coul/debye ${kpair} ${sigma}
pair_coeff      1 1   lj/cut/coul/debye ${kpair} ${sigma} ${lj_cut_min} ${ldebye_cut}
pair_coeff      1*7 8*13 lj/cut ${smc_shell_eps} ${smc_sigma} ${smc_rep_cut}
pair_coeff      8*13 8*13 lj/cut 0.0 1.0 1.0

""" + state_block("APO_PRE") + """

include         in.bond_settings
bond_coeff      25 fene/expand 61.8852655115 17.0 0.0 0.0 17.0
bond_coeff      26 fene/expand 114.46298709 12.5 0.0 0.0 0.0
bond_coeff      27 harmonic    0.03815432903 50.2170161853
bond_coeff      28 harmonic    0.7630865806 70.7106781084
bond_coeff      29 harmonic    ${smc_belt_weak_k} 0.0

angle_coeff     1 cosine ${kangle}
angle_coeff     2 cosine 17.5341585616
angle_coeff     3 harmonic 17.8848417328 180.0
angle_coeff     4 harmonic ${smc_arm_k} ${smc_arm_apo}

improper_coeff  1 ${smc_arm_k} 0.0
improper_coeff  2 ${smc_improper2_k} ${smc_improper2_apo}
improper_coeff  3 ${smc_improper3_k} ${smc_improper3_apo}
"""


def write_prep_input(rep_dir, rep_name):
    tag = f"{rep_name}_prep"
    text = f"""# Loading relax for {rep_name}; lower-only state.
variable        tag string {tag}
log             log.${{tag}}

units           real
dimension       3
atom_style      full
boundary        p p p

neighbor        60.0 nsq
neigh_modify    every 1 delay 0 check yes

{variable_definitions()}
read_data       data.hybrid_smc_nicg
{read_data_force_field()}
{runtime_definitions()}

velocity        chromatin create ${{T}} 24680 mom yes rot yes dist gaussian
velocity        smc set 0.0 0.0 0.0
reset_timestep  0
run             0

print           "stage PRE_DNA_LOWER_ONLY sampled_steps {PRE_DNA_STEPS} cumulative_step {PRE_DNA_STEPS}"
run             {PRE_DNA_STEPS}

print           "stage PRE_SMC_LOWER_ONLY sampled_steps {PRE_SMC_STEPS} cumulative_step {PRE_DNA_STEPS + PRE_SMC_STEPS}"
run             {PRE_SMC_STEPS}

print           "safety_belt_cycle_k ${{smc_belt_cycle_k}}"
bond_coeff      29 harmonic ${{smc_belt_cycle_k}} 0.0
write_restart   restart.after_prep
write_data      data.after_prep
"""
    (rep_dir / "in.prep_loading_relax").write_text(text)


def write_cycle_input(rep_dir, rep_name, cycle, rows):
    start_restart = "restart.after_prep" if cycle == 1 else f"restart.after_cycle_{cycle - 1:03d}"
    tag = f"{rep_name}_cycle_{cycle:03d}"
    chunks = []
    for row in rows:
        if row["stage"] == "APO_RETURN":
            run_block = apo_return_run_block(row["sampled_steps"])
        else:
            run_block = f"""{state_block(row['stage'])}
run             {row['sampled_steps']}"""
        chunks.append(
            f"""print           "cycle {row['cycle']} stage {row['stage']} sampled_steps {row['sampled_steps']} cumulative_step {row['cumulative_step']}"
{run_block}
"""
        )
    text = f"""# Random 50-cycle 10x faster SMC run, {rep_name}, cycle {cycle}.
variable        tag string {tag}
log             log.${{tag}}

units           real
dimension       3
atom_style      full
boundary        p p p

neighbor        60.0 nsq
neigh_modify    every 1 delay 0 check yes

read_restart    {start_restart}
{variable_definitions()}
{runtime_definitions()}

bond_coeff      29 harmonic ${{smc_belt_cycle_k}} 0.0

{"".join(chunks)}

write_restart   restart.after_cycle_{cycle:03d}
write_data      data.after_cycle_{cycle:03d}
"""
    (rep_dir / f"in.cycle_{cycle:03d}").write_text(text)


def copy_static_files(rep_dir):
    for name in ["data.hybrid_smc_nicg", "in.bond_settings"]:
        shutil.copy2(HERE / name, rep_dir / name)


def write_replicate(rep_name, seed):
    rep_dir = HERE / rep_name
    rep_dir.mkdir(exist_ok=True)
    copy_static_files(rep_dir)
    rows = sample_schedule(seed)
    write_schedule(rep_dir, rows)
    write_prep_input(rep_dir, rep_name)
    by_cycle = {cycle: [] for cycle in range(1, CYCLES + 1)}
    for row in rows:
        by_cycle[row["cycle"]].append(row)
    for cycle in range(1, CYCLES + 1):
        write_cycle_input(rep_dir, rep_name, cycle, by_cycle[cycle])
    total_steps = PRE_DNA_STEPS + PRE_SMC_STEPS + sum(row["sampled_steps"] for row in rows)
    (rep_dir / "run_metadata.txt").write_text(
        "\n".join(
            [
                f"replicate = {rep_name}",
                f"seed = {seed}",
                f"cycles = {CYCLES}",
                "dwell_scale = 0.1",
                f"dt_fs = {DT_FS}",
                f"pre_dna_steps = {PRE_DNA_STEPS}",
                f"pre_smc_steps = {PRE_SMC_STEPS}",
                f"total_steps_including_relax = {total_steps}",
                f"target_linker_atom_id = {TARGET_LINKER_ID}",
                f"belt_linker_atom_id = {BELT_LINKER_ID}",
                f"left_terminal_linker_atom_id = {LEFT_TERMINAL_ID}",
                f"right_terminal_linker_atom_id = {RIGHT_TERMINAL_ID}",
                "",
            ]
        )
    )
    return rep_dir


def main():
    for rep_name, seed in REPLICATES:
        rep_dir = write_replicate(rep_name, seed)
        print(rep_dir)


if __name__ == "__main__":
    main()
