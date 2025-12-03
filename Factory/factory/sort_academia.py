import os, json, re, shutil

def load_patterns(patterns_dir):
    patterns = {}
    for fname in os.listdir(patterns_dir):
        key = fname.replace(".txt", "")
        with open(os.path.join(patterns_dir, fname), "r") as f:
            patterns[key] = [line.strip() for line in f if line.strip()]
    return patterns

def load_exclusion_rules(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def assign_bin(text, bins):
    t = text.lower()
    for bin_name, keywords in bins.items():
        for kw in keywords:
            if kw.lower() in t:
                return bin_name
    return "unsorted"

def main():
    with open("factory/config_academia.json") as f:
        config = json.load(f)

    patterns = load_patterns(config["patterns_dir"])
    exclusions = load_exclusion_rules(config["exclusion_rules"])

    os.makedirs(config["output_dir"], exist_ok=True)

    for fname in os.listdir(config["input_dir"]):
        path = os.path.join(config["input_dir"], fname)
        with open(path, "r") as f:
            text = f.read()

        # Skip exclusions
        if any(ex in text.lower() for ex in exclusions):
            continue

        # Assign bin
        bin_name = assign_bin(text, config["bins"])
        out_dir = os.path.join(config["output_dir"], bin_name)
        os.makedirs(out_dir, exist_ok=True)

        # Write raw piece
        with open(os.path.join(out_dir, fname), "w") as out:
            out.write(text)

    print("Sorting complete.")

if __name__ == "__main__":
    main()
