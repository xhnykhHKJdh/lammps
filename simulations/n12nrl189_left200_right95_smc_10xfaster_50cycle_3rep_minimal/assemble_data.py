from pathlib import Path


HERE = Path(__file__).resolve().parent
CHUNK_DIR = HERE / "data_chunks"
OUT = HERE / "data.hybrid_smc_nicg"


def main():
    parts = sorted(CHUNK_DIR.glob("data.hybrid_smc_nicg.part_*"))
    if not parts:
        raise SystemExit(f"No chunks found in {CHUNK_DIR}")
    with OUT.open("w") as out:
        for part in parts:
            out.write(part.read_text())
    print(OUT)


if __name__ == "__main__":
    main()
