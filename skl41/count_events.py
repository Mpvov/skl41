import csv
from collections import Counter

with open('d:/skylink/data/skl41/sample_user_log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    counts = Counter(row['event_name'] for row in reader)

for k, v in counts.items():
    print(f"{k}: {v}")
