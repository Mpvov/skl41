import csv

with open('d:/skylink/data/skl41/sample_user_log.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    events = {'skl_ad_request': [], 'skl_ad_response': [], 'skl_ad_click': [], 'ad_revenue_sdk': [], 'skl_ad_close': []}
    for row in reader:
        if row['event_name'] in events and len(events[row['event_name']]) < 2:
            events[row['event_name']].append(row)
            
    for event, rows in events.items():
        print(f"--- {event} ---")
        for row in rows:
            print({k: v for k, v in row.items() if v != ''})
