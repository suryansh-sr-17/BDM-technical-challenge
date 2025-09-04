import os
import json
import re
import pandas as pd

# =============================
# CONFIG - raw dataset paths
# =============================
SPAMASSASSIN_DIR = "../data/raw/spamassassin/train.jsonl"   # raw SpamAssassin folder
OPP115_FILE = "../data/raw/opp115.parquet"      # raw OPP-115 parquet
ENRON_FILE = "../data/raw/enron_hf.csv"            # raw Enron CSV
OUTPUT_FILE = "../data/processed/all_datasets.jsonl"  # final merged dataset

# =============================
# OPP115 Category Mapping
# =============================
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

# =============================
# HELPERS
# =============================
def clean_text(text: str) -> str:
    """Clean text for consistency in fine-tuning dataset."""
    if not isinstance(text, str):
        return ""

    # Normalize whitespace and remove control characters
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()

    # Remove non-printable chars
    text = "".join(ch for ch in text if ch.isprintable())

    # Neutralize raw URLs (keep domain but avoid broken JSON/formatting)
    text = re.sub(r"http[s]?://\S+", "[LINK]", text)

    # Neutralize email addresses
    text = re.sub(r"\S+@\S+", "[EMAIL]", text)

    return text


def make_conversation(user_prompt: str, assistant_reply: str) -> dict:
    """Return dict with conversations in correct format."""
    return {
        "conversations": [
            {"role": "user", "content": clean_text(user_prompt)},
            {"role": "assistant", "content": clean_text(assistant_reply)},
        ]
    }

# =============================
# 1. Process SpamAssassin dataset
# =============================
def process_spamassassin(jsonl_path: str = "data/raw/spamassassin/train.jsonl"):
    data = []
    if not os.path.exists(jsonl_path):
        print(f"❌ SpamAssassin file not found at {jsonl_path}")
        return data

    print(f"📂 Reading SpamAssassin JSONL from {jsonl_path}")

    # Common mapping: adjust if your dataset uses opposite convention
    label_map = {
        0: "ham",
        1: "spam",
        "ham": "ham - It is a genuine mail",
        "spam": "spam - It is a spam mail"
    }

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            try:
                entry = json.loads(line.strip())
                content = str(entry.get("text", "")).strip()
                raw_label = entry.get("label")

                label = label_map.get(raw_label)
                if not content or label is None:
                    print(f"⚠️ Skipping invalid entry at line {i}: {entry}")
                    continue

                reason = f"{label} — because the content matches patterns typical of {label} emails."
                user_prompt = f"Classify this email as spam or ham:\n\n{content[:300]}..."

                data.append({
                    "conversations": [
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": reason},
                    ]
                })

            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON at line {i}: {line[:100]}...")
                continue

    print(f"✅ SpamAssassin processed: {len(data)} entries")
    return data
# =============================
# 2. Process OPP-115 Privacy Policies
# =============================
def process_opp115(parquet_file: str):
    data = []
    df = pd.read_parquet(parquet_file)
    for _, row in df.iterrows():
        statement = row.get("SegmentText", "")
        label_id = row.get("DataPractice", None)
        label = opp115_mapping.get(label_id, "Uncategorized Disclosure")
        user_prompt = f"Classify this policy statement under the correct CCPA disclosure category:\n\n{statement}"
        assistant_reply = f"{label} — because the statement reflects practices related to {label.lower()}."
        data.append(make_conversation(user_prompt, assistant_reply))
    return data

# =============================
# 3. Process Enron Emails
# =============================
def process_enron(csv_file: str):
    data = []
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        subject = row.get("subject", "")
        body = row.get("body", "")
        label = row.get("label", "ham")  # default fallback
        user_prompt = f"Classify this email as spam or ham:\n\nSubject: {subject}\nBody: {body[:300]}..."
        assistant_reply = f"{label} — because the content matches typical patterns of {label} emails."
        data.append(make_conversation(user_prompt, assistant_reply))
    return data

# =============================
# MAIN MERGE
# =============================
if __name__ == "__main__":
    print("🚀 Processing datasets...")
    merged = []

    # SpamAssassin
    sa_data = process_spamassassin(SPAMASSASSIN_DIR)
    print(f"✔ SpamAssassin processed: {len(sa_data)} entries")
    merged.extend(sa_data)

    # OPP-115
    opp_data = process_opp115(OPP115_FILE)
    print(f"✔ OPP-115 processed: {len(opp_data)} entries")
    merged.extend(opp_data)

    # Enron
    enron_data = process_enron(ENRON_FILE)
    print(f"✔ Enron processed: {len(enron_data)} entries")
    merged.extend(enron_data)

    # ✨ Save final combined dataset
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)  # make sure folder exists
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for entry in merged:
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Final log
    print(f"🎉 Final dataset written to {OUTPUT_FILE} with {len(merged)} total entries.")
