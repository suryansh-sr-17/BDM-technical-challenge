# # import json
# # import re

# # input_file = "../data/processed/all_datasets.jsonl"          # Your current dataset
# # output_file = "../data/processed/all_datasets_cleaned.jsonl" # New cleaned dataset

# # def clean_email_text(text):
# #     """Remove Python list-like wrappers and normalize whitespace."""
# #     # Remove [' ... '] pattern if present
# #     text = re.sub(r"^\[\s*'(.*)'\s*\]$", r"\1", text.strip())
# #     # Remove extra quotes if left over
# #     text = text.strip("'\"")
# #     # Normalize multiple spaces/newlines
# #     text = re.sub(r"\s+", " ", text).strip()
# #     return text

# # def clean_label(content):
# #     """Ensure labels follow 'LABEL — justification' format."""
# #     content = content.strip()
# #     if not content:
# #         return "ham — no justification provided"

# #     # Extract label (first word: spam/ham, case-insensitive)
# #     match = re.match(r"^(spam|ham)", content, re.IGNORECASE)
# #     if match:
# #         label = match.group(1).lower()
# #         justification = content[len(match.group(0)):].strip(" —:-")
# #         if not justification:
# #             justification = "no justification provided"
# #         return f"{label} — {justification}"
# #     else:
# #         # Default fallback
# #         return f"ham — {content}"

# # def process_dataset(input_file, output_file):
# #     with open(input_file, "r", encoding="utf-8") as infile, \
# #          open(output_file, "w", encoding="utf-8") as outfile:

# #         for i, line in enumerate(infile, start=1):
# #             try:
# #                 obj = json.loads(line)
# #                 if "conversations" not in obj:
# #                     print(f"⚠️ Skipping line {i}: missing 'conversations'")
# #                     continue

# #                 new_convos = []
# #                 for conv in obj["conversations"]:
# #                     role = conv.get("role")
# #                     content = conv.get("content", "")

# #                     if role == "user":
# #                         content = clean_email_text(content)
# #                     elif role == "assistant":
# #                         content = clean_label(content)

# #                     new_convos.append({"role": role, "content": content})

# #                 cleaned = {"conversations": new_convos}
# #                 outfile.write(json.dumps(cleaned, ensure_ascii=False) + "\n")

# #             except json.JSONDecodeError:
# #                 print(f"❌ Invalid JSON on line {i}, skipping.")
# #                 continue

# #     print(f"\n✅ Cleaning complete! Fixed dataset saved to: {output_file}")

# # if __name__ == "__main__":
# #     process_dataset(input_file, output_file)

# import json
# import re

# input_file = "../data/processed/all_datasets_cleaned.jsonl"
# output_file = "../data/processed/all_datasets_final.jsonl"

# def clean_text(text):
#     # Remove leading/trailing list-like wrappers: [' ... ']
#     text = re.sub(r"^\[\s*'(.+)'\s*\]$", r"\1", text.strip())
#     text = re.sub(r'^\["(.+)"\]$', r"\1", text.strip())

#     # Replace escaped \n with real newlines
#     text = text.replace("\\n", "\n")

#     # Remove weird escaped characters like \x01
#     text = re.sub(r'\\x[0-9a-fA-F]{2}', '', text)

#     # Strip any leftover multiple spaces
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text

# with open(input_file, "r", encoding="utf-8") as infile, \
#      open(output_file, "w", encoding="utf-8") as outfile:
    
#     for line in infile:
#         try:
#             data = json.loads(line)
#             conversations = data.get("conversations", [])

#             for conv in conversations:
#                 if conv.get("role") == "user":
#                     conv["content"] = clean_text(conv["content"])

#             json.dump(data, outfile, ensure_ascii=False)
#             outfile.write("\n")

#         except json.JSONDecodeError:
#             continue

# print(f"✅ Cleaning complete! New dataset saved as {output_file}")


import json
import re

def clean_user_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text)

    # Remove Python list-style brackets if they exist
    text = re.sub(r"^\s*\[\'|\'\]\s*$", "", text)

    # Normalize multiple spaces/newlines
    text = re.sub(r"\s+", " ", text).strip()

    # Fix malformed URLs (example: "http: //example.com" → "http://example.com")
    text = text.replace(":// ", "://").replace("http: //", "http://").replace("https: //", "https://")

    return text

def repair_jsonl(input_path="../data/processed/all_datasets_final.jsonl",
                 output_path="../data/processed/all_datasets_new.jsonl"):
    fixed = 0
    total = 0

    with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            total += 1
            try:
                obj = json.loads(line)
                if "conversations" in obj:
                    new_convos = []
                    for msg in obj["conversations"]:
                        if msg["role"] == "user":
                            cleaned = clean_user_text(msg["content"])
                            if cleaned != msg["content"]:
                                fixed += 1
                            new_convos.append({"role": "user", "content": cleaned})
                        else:
                            # Leave assistant untouched
                            new_convos.append(msg)
                    obj["conversations"] = new_convos

                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

            except json.JSONDecodeError:
                print(f"❌ Skipped invalid line {total}")

    print(f"✅ Repair complete → {output_path}")
    print(f"🔧 Cleaned {fixed} user messages out of {total} total lines.")

if __name__ == "__main__":
    repair_jsonl()
