# import json
# import os

# def debug_jsonl(file_path="../data/processed/all_datasets.jsonl"):
#     if not os.path.exists(file_path):
#         print(f"❌ File not found: {file_path}")
#         return
    
#     with open(file_path, "r", encoding="utf-8") as f:
#         first_chars = f.read(100).strip()
#         f.seek(0)  # reset file pointer
    
#         # Case 1: File starts with '[' => JSON array instead of JSONL
#         if first_chars.startswith("["):
#             print("⚠️ Detected JSON array format instead of JSONL.")
#             return

#         # Case 2: Should be JSONL, validate each line
#         print("🔍 Checking JSONL line-by-line...")
#         errors_found = 0
#         for i, line in enumerate(f, start=1):
#             line = line.strip()
#             if not line:
#                 print(f"⚠️ Empty line at {i}")
#                 continue
#             try:
#                 json.loads(line)
#             except Exception as e:
#                 print(f"❌ Invalid JSON at line {i}: {e}")
#                 print(f"   Line content: {line[:200]}...")
#                 errors_found += 1
#                 if errors_found >= 5:
#                     print("⚠️ Stopping after 5 errors for readability.")
#                     break
        
#         if errors_found == 0:
#             print("✅ All lines are valid JSON. File seems fine!")

# if __name__ == "__main__":
#     debug_jsonl()


import json

def inspect_jsonl(file_path="../data/processed/all_datasets.jsonl", max_lines=5):
    print(f"🔍 Inspecting {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if i > max_lines:
                break
            obj = json.loads(line)
            print(f"\n--- Entry {i} ---")
            print("Keys:", list(obj.keys()))
            if "conversations" in obj:
                print("Conversations sample:", obj["conversations"][:1])

if __name__ == "__main__":
    inspect_jsonl()