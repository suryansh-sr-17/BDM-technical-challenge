import json
import pandas as pd

# ---------- Enron ----------
def convert_enron_hf(input_path="../data/raw/enron_hf.csv", output_path="../data/processed/enron_hf.jsonl"):
    df = pd.read_csv(input_path)
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            text = row["email"]
            label = "spam" if row["label"] == 1 else "ham"
            justification = "spam — because it contains promotional/unsolicited content" if label == "spam" else "ham — because it is a normal, non-promotional email"
            record = {
                "conversations": [
                    {"role": "user", "content": f"Classify this email as spam or ham:\n\n{text}"},
                    {"role": "assistant", "content": justification}
                ]
            }
            f.write(json.dumps(record) + "\n")
    print(f"✅ Saved Enron HF → {output_path}")


# ---------- SpamAssassin ----------
def convert_spamassassin(input_path="../data/raw/spamassassin/train.jsonl", output_path="../data/processed/spamassassin_mapped.jsonl"):
    with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            row = json.loads(line)
            text = row["text"]
            label_val = row["label"]

            if label_val in [0, "0", "ham"]:
                label, justification = "ham", "ham — because the content appears to be a normal, non-promotional message"
            elif label_val in [1, "1", "spam"]:
                label, justification = "spam", "spam — because the content is unsolicited or promotional"
            else:
                continue

            record = {
                "conversations": [
                    {"role": "user", "content": f"Classify this email as spam or ham:\n\n{text}"},
                    {"role": "assistant", "content": justification}
                ]
            }
            fout.write(json.dumps(record) + "\n")
    print(f"✅ Saved SpamAssassin → {output_path}")


# ---------- OPP-115 ----------
def convert_opp115(parquet_path="../data/raw/opp115.parquet", output_path="../data/processed/opp115_mapped.jsonl"):
    opp115_mapping = {
        1: "CCPA Disclosure — Security & Breach Notification",
        2: "CCPA Disclosure — Consumer Rights (Do Not Track)",
        3: "CCPA Disclosure — Data Collection & Cookies",
        4: "CCPA Disclosure — Personal Data Use & User Rights",
        5: "CCPA Disclosure — Third-Party Sharing",
        6: "CCPA Disclosure — Policy Changes",
        7: "CCPA Disclosure — Special Cases / Promotions",
        8: "CCPA Disclosure — Compliance & Dispute Resolution",
        9: "CCPA Disclosure — Legal Compliance",
        10: "CCPA Disclosure — Deletion & Data Subject Rights",
        11: "CCPA Disclosure — Opt-Out / Communication Control",
        12: "CCPA Disclosure — Data Retention & Access"
    }

    df = pd.read_parquet(parquet_path)
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            text = row["text"]
            labels = row["label"]

            if hasattr(labels, "tolist"):
                labels = labels.tolist()
            if isinstance(labels, (list, tuple)) and len(labels) > 0:
                label_id = labels[0]
            else:
                continue

            label = opp115_mapping.get(label_id, None)
            if label is None:
                continue

            record = {
                "conversations": [
                    {"role": "user", "content": f"Classify this policy statement under the correct CCPA disclosure category:\n\n{text}"},
                    {"role": "assistant", "content": f"{label} — because the statement refers to {label.split('—')[-1].strip().lower()}"}
                ]
            }
            f.write(json.dumps(record) + "\n")
    print(f"✅ Saved OPP-115 → {output_path}")


# ---------- Merge all ----------
def merge_datasets(
    enron_path="../data/processed/enron_hf.jsonl",
    spamassassin_path="../data/processed/spamassassin_mapped.jsonl",
    opp115_path="../data/processed/opp115_mapped.jsonl",
    output_path="../data/processed/all_datasets.jsonl"
):
    files = [enron_path, spamassassin_path, opp115_path]
    with open(output_path, "w", encoding="utf-8") as fout:
        for file in files:
            with open(file, "r", encoding="utf-8") as fin:
                for line in fin:
                    fout.write(line)
    print(f"✅ Merged all datasets → {output_path}")


if __name__ == "__main__":
    convert_enron_hf()
    convert_spamassassin()
    convert_opp115()
    merge_datasets()
