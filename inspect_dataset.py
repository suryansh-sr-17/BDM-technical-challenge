# intial process

import pandas as pd
import numpy as np
from datasets import load_dataset
import itertools

def inspect_csv(path, n=5, sample_cats=True):
    print(f"\n=== Inspecting CSV: {path} ===")
    df = pd.read_csv(path, nrows=5000)   # load partial for speed
    print("\nColumns:", df.columns.tolist())
    print("\nSample rows:\n", df.head(n))

    if sample_cats:
        for col in df.columns:
            if df[col].dtype == "object" and df[col].nunique() < 20:
                print(f"\nDistinct values in '{col}':")
                print(df[col].unique())

def inspect_parquet(path, n_rows=5):
    print(f"\n=== Inspecting Parquet: {path} ===\n")
    df = pd.read_parquet(path)
    print("Columns:", list(df.columns), "\n")
    print("Sample rows:")
    print(df.head(n_rows), "\n")

    for col in df.columns:
        # Convert list/array-like values into strings so nunique() doesn't break
        safe_series = df[col].apply(lambda x: str(x) if isinstance(x, (list, np.ndarray)) else x)

        if safe_series.dtype == "object" and safe_series.nunique() < 20:
            print(f"Column '{col}' unique values:", safe_series.unique())

def inspect_spamassassin(save_path="data/raw/spamassassin"):
    print("\n=== Inspecting SpamAssassin from HF ===")
    ds = load_dataset("talby/spamassassin", "text")  # loads train + test

    print("\nSplits available:", ds.keys())
    print("\nFeatures:", ds["train"].features)
    print("\nSample:", ds["train"][0])

    # Save each split locally as JSON
    import os
    os.makedirs(save_path, exist_ok=True)
    for split in ds.keys():
        out_file = f"{save_path}/{split}.jsonl"
        ds[split].to_json(out_file, orient="records", lines=True, force_ascii=False)
        print(f"Saved {split} split → {out_file}")

if __name__ == "__main__":
    # Enron CSVs (adjust paths for Kaggle vs HF copies)
    inspect_csv("data/raw/enron_k.csv")
    inspect_csv("data/raw/enron_hf.csv")

    # OPP-115 privacy dataset
    inspect_parquet("data/raw/opp115.parquet")

    # SpamAssassin
    inspect_spamassassin()
