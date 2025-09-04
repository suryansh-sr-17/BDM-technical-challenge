import json
import random

def merge_datasets(
    enron_path="../data/processed/enron_hf.jsonl",
    spamassassin_path="../data/processed/spamassassin_mapped.jsonl",
    opp115_path="../data/processed/opp115_mapped.jsonl",
    output_path="../data/processed/all_datasets.jsonl",
    seed=42
):
    files = [enron_path, spamassassin_path, opp115_path]
    data = []

    # Load all lines into memory
    for file in files:
        with open(file, "r", encoding="utf-8") as fin:
            for line in fin:
                data.append(line.strip())

    # Shuffle with fixed seed for reproducibility
    random.seed(seed)
    random.shuffle(data)

    # Write merged + shuffled data
    with open(output_path, "w", encoding="utf-8") as fout:
        for line in data:
            fout.write(line + "\n")

    print(f"✅ Merged & shuffled {len(data)} samples → {output_path}")


if __name__ == "__main__":
    merge_datasets()
