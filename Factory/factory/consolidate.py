import os

def consolidate(bin_path):
    chunks = []
    for fname in sorted(os.listdir(bin_path)):
        with open(os.path.join(bin_path, fname), "r") as f:
            chunks.append(f.read())

    combined = "\n\n---\n\n".join(chunks)

    with open(os.path.join(bin_path, "_CONSOLIDATED.md"), "w") as f:
        f.write(combined)

if __name__ == "__main__":
    base = "output_bins"
    for bin_name in os.listdir(base):
        path = os.path.join(base, bin_name)
        if os.path.isdir(path):
            consolidate(path)
            print("Consolidated:", bin_name)
