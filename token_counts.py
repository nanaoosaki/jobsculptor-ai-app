from pathlib import Path
import tiktoken               # pip install tiktoken
import sys
enc = tiktoken.get_encoding("cl100k_base")   # same used by GPT-4o
total = 0
for p in Path(".").rglob("*.py"):
    total += len(enc.encode(p.read_text()))
print(f"{total:,} tokens")
print(sys.executable)
