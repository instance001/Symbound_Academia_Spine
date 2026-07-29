import os, json, re, shutil
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parent
REPO_ROOT = FACTORY_ROOT.parents[1]

def resolve_path(path):
    p = Path(path).expanduser()
    return p if p.is_absolute() else FACTORY_ROOT / p

def resolve_output_path(path):
    p = Path(path).expanduser()
    return p if p.is_absolute() else REPO_ROOT / p

def load_patterns(patterns_dir):
    patterns = {}
    for path in sorted(Path(patterns_dir).glob("*.txt")):
        key = path.stem
        with path.open("r", encoding="utf-8") as f:
            patterns[key] = [line.strip() for line in f if line.strip()]
    return patterns

def load_exclusion_rules(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def assign_bin(text, bins):
    t = text.lower()
    for bin_name, keywords in bins.items():
        for kw in keywords:
            if kw.lower() in t:
                return bin_name
    return "unsorted"

def main():
    config_path = Path(os.environ.get("ACADEMIA_SORT_CONFIG", FACTORY_ROOT / "config_academia.json"))
    if not config_path.is_absolute():
        config_path = FACTORY_ROOT / config_path
    with config_path.open("r", encoding="utf-8-sig") as f:
        config = json.load(f)

    patterns = load_patterns(resolve_path(config["patterns_dir"]))
    exclusions = load_exclusion_rules(resolve_path(config["exclusion_rules"]))

    input_dir = resolve_path(config["input_dir"])
    output_dir = resolve_output_path(os.environ.get("ACADEMIA_SORT_OUTPUT_DIR", config["output_dir"]))
    os.makedirs(output_dir, exist_ok=True)

    for path in sorted(input_dir.iterdir()):
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8-sig") as f:
            text = f.read()

        # Skip exclusions
        if any(ex in text.lower() for ex in exclusions):
            continue

        # Assign bin
        bin_name = assign_bin(text, config["bins"])
        out_dir = output_dir / bin_name
        os.makedirs(out_dir, exist_ok=True)

        # Write raw piece
        with (out_dir / path.name).open("w", encoding="utf-8") as out:
            out.write(text)

    print("Sorting complete.")

if __name__ == "__main__":
    main()
