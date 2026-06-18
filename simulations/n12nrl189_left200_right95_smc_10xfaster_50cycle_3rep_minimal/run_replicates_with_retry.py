from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
DEFAULT_LAMMPS = "/Applications/LAMMPS_GUI.app/Contents/bin/lmp"
REPLICATES = [
    "replicate_01_seed20260618",
    "replicate_02_seed20260619",
    "replicate_03_seed20260620",
]
ERROR_MARKERS = [
    "ERROR",
    "Lost atoms",
    "lost atoms",
    "missing bond atoms",
    "Bad FENE",
    "Non-numeric atom coords",
    "nan",
    "NaN",
]


def read_text_if_exists(path):
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def log_has_failure(rep_dir, tag, stdout_path, stderr_path, screen_path):
    texts = [
        read_text_if_exists(rep_dir / f"log.{tag}"),
        read_text_if_exists(stdout_path),
        read_text_if_exists(stderr_path),
        read_text_if_exists(screen_path),
    ]
    merged = "\n".join(texts)
    return any(marker in merged for marker in ERROR_MARKERS)


def run_lammps(rep_dir, input_name, tag, lammps_bin, threads):
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)
    stdout_path = rep_dir / f"launcher.{tag}.stdout"
    stderr_path = rep_dir / f"launcher.{tag}.stderr"
    screen_path = rep_dir / f"screen.{tag}.txt"
    cmd = [
        lammps_bin,
        "-sf",
        "omp",
        "-pk",
        "omp",
        str(threads),
        "-in",
        input_name,
        "-screen",
        str(screen_path.name),
    ]
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        proc = subprocess.run(cmd, cwd=rep_dir, env=env, stdout=stdout, stderr=stderr)
    failed = proc.returncode != 0 or log_has_failure(rep_dir, tag, stdout_path, stderr_path, screen_path)
    return proc.returncode, failed


def archive_failed_attempt(rep_dir, tag, attempt):
    failed_dir = rep_dir / "failed_attempts"
    failed_dir.mkdir(exist_ok=True)
    for filename in [
        f"log.{tag}",
        f"screen.{tag}.txt",
        f"launcher.{tag}.stdout",
        f"launcher.{tag}.stderr",
    ]:
        src = rep_dir / filename
        if src.exists():
            shutil.move(src, failed_dir / f"{src.name}.attempt{attempt}")


def ensure_generated():
    missing = [name for name in REPLICATES if not (HERE / name).exists()]
    if missing:
        subprocess.check_call([sys.executable, "generate_random50cycle_replicates.py"], cwd=HERE)


def run_replicate(rep_name, lammps_bin, threads, max_retries):
    rep_dir = HERE / rep_name
    if not rep_dir.exists():
        raise RuntimeError(f"Missing replicate directory: {rep_dir}")

    report = rep_dir / "runner_report.txt"
    with report.open("a") as out:
        out.write(f"running {rep_name}\n")

    if not (rep_dir / "restart.after_prep").exists():
        tag = f"{rep_name}_prep"
        rc, failed = run_lammps(rep_dir, "in.prep_loading_relax", tag, lammps_bin, threads)
        with report.open("a") as out:
            out.write(f"prep rc={rc} failed={failed}\n")
        if failed:
            raise RuntimeError(f"{rep_name} prep failed; inspect {rep_dir}")

    for cycle in range(1, 51):
        done = rep_dir / f"restart.after_cycle_{cycle:03d}"
        if done.exists():
            continue
        input_name = f"in.cycle_{cycle:03d}"
        tag = f"{rep_name}_cycle_{cycle:03d}"
        for attempt in range(1, max_retries + 2):
            rc, failed = run_lammps(rep_dir, input_name, tag, lammps_bin, threads)
            with report.open("a") as out:
                out.write(f"cycle={cycle} attempt={attempt} rc={rc} failed={failed}\n")
            if not failed and done.exists():
                break
            archive_failed_attempt(rep_dir, tag, attempt)
            if done.exists():
                done.unlink()
            if attempt > max_retries:
                (rep_dir / "failure_report.txt").write_text(
                    f"{rep_name} failed at cycle {cycle} after {attempt} attempts\n"
                )
                raise RuntimeError(f"{rep_name} failed at cycle {cycle}; inspect {rep_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lammps", default=os.environ.get("LAMMPS_BIN", DEFAULT_LAMMPS))
    parser.add_argument("--threads", type=int, default=int(os.environ.get("OMP_NUM_THREADS", "4")))
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--replicate", choices=REPLICATES + ["all"], default="all")
    args = parser.parse_args()

    ensure_generated()
    reps = REPLICATES if args.replicate == "all" else [args.replicate]
    for rep_name in reps:
        run_replicate(rep_name, args.lammps, args.threads, args.max_retries)


if __name__ == "__main__":
    main()
