import csv

with open('d:/skylink/data/skl41/sample_user_log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    events = {'skl_ad_show': []}
    for row in reader:
        if row['event_name'] in events and len(events[row['event_name']]) < 5:
            events[row['event_name']].append(row)
            
    for event, rows in events.items():
        print(f"--- {event} ---")
        for row in rows:
            print({k: v for k, v in row.items() if v != ''})
