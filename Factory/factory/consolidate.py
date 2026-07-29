import os
from pathlib import Path

def consolidate(bin_path):
    chunks = []
    for path in sorted(Path(bin_path).iterdir()):
        if path.name == "_CONSOLIDATED.md" or not path.is_file():
            continue
        with path.open("r", encoding="utf-8-sig") as f:
            chunks.append(f.read())

    combined = "\n\n---\n\n".join(chunks)

    with (Path(bin_path) / "_CONSOLIDATED.md").open("w", encoding="utf-8") as f:
        f.write(combined)

if __name__ == "__main__":
    factory_root = Path(__file__).resolve().parent
    repo_root = factory_root.parents[1]
    base_arg = os.environ.get("ACADEMIA_SORT_OUTPUT_DIR", "output_bins")
    base = Path(base_arg).expanduser()
    if not base.is_absolute():
        base = repo_root / base
    base.mkdir(parents=True, exist_ok=True)
    for path in sorted(base.iterdir()):
        if path.is_dir():
            consolidate(path)
            print("Consolidated:", path.name)
