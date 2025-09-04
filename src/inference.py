from transformers import AutoTokenizer
from fastllm import FastLanguageModel  # if using your optimized wrapper

tokenizer = AutoTokenizer.from_pretrained("path/to/model")
model = FastLanguageModel.for_inference("path/to/model")

messages = [
    {
        "role": "user",
        "content": '''You are an expert compliance officer specializing in email and privacy policy classification. 
Your task is to analyze the following text and classify it into the correct category.

Categories:
1 — CCPA Disclosure — Security & Breach Notification  
2 — CCPA Disclosure — Consumer Rights (Do Not Track)  
3 — CCPA Disclosure — Data Collection & Cookies  
4 — CCPA Disclosure — Personal Data Use & User Rights  
5 — CCPA Disclosure — Third-Party Sharing  
6 — CCPA Disclosure — Policy Changes  
7 — CCPA Disclosure — Special Cases / Promotions  
8 — CCPA Disclosure — Compliance & Dispute Resolution  
9 — CCPA Disclosure — Legal Compliance  
10 — CCPA Disclosure — Deletion & Data Subject Rights  
11 — CCPA Disclosure — Opt-Out / Communication Control  
12 — CCPA Disclosure — Data Retention & Access  

Text:
"""
Dear Suryansh Singh Raghuvansh,

Introducing our latest product HP Tiny - EliteDesk 800 G4
Reduce Your Hardware Cost up to 60%
We strive to ensure your complete Satisfaction.
"""

Please output ONLY the best-fitting category number and its full label.'''
    }
]

inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
output = model.generate(inputs, max_new_tokens=128)
print(tokenizer.decode(output[0]))
