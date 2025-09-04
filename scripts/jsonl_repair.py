import json
import re
from pathlib import Path

INPUT_FILE = "../data/processed/all_datasets_fixed.jsonl"   # broken dataset
OUTPUT_FILE = "../data/processed/all_datasets_repaired.jsonl"  # cleaned dataset

def clean_email_text(raw_text: str) -> str:
    """
    Remove Python list-like wrappers [' ... '] and return clean email text.
    """
    # Match [' ... '] or [" ... "]
    match = re.match(r"^\[(['\"])(.*)\1\]$", raw_text.strip(), re.DOTALL)
    if match:
        return match.group(2)  # inner content
    return raw_text  # return unchanged if not wrapped

def repair_line(line: str):
    """
    Fix a single JSON line into proper fine-tune format.
    """
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None  # skip bad lines

    if "conversations" not in obj:
        return None

    convos = obj["conversations"]

    # Extract user message
    user_msg = convos[0].get("content", "").strip()
    # Clean any list-like artifacts inside the user content
    user_msg = re.sub(r"\[(['\"])(.*)\1\]", r"\2", user_msg, flags=re.DOTALL)

    # --- 🔑 ASSUMPTION ---
    # If your labels are missing, add a placeholder.
    # Replace "LABEL_MISSING" with your real logic if labels exist elsewhere.
    label = convos[0].get("label", "LABEL_MISSING")

    return {
        "conversations": [
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": label}
        ]
    }

def main():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    with input_path.open("r", encoding="utf-8") as infile, \
         output_path.open("w", encoding="utf-8") as outfile:

        for i, line in enumerate(infile, start=1):
            fixed = repair_line(line)
            if fixed:
                outfile.write(json.dumps(fixed, ensure_ascii=False) + "\n")
            else:
                print(f"⚠️ Skipping bad line {i}")

    print(f"✅ Repaired dataset written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
