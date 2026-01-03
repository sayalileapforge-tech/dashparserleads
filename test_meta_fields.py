from meta_leads_fetcher import get_fetcher
import json

fetcher = get_fetcher()
leads = fetcher.fetch_leads(limit=1)

print("\n\n=== FIRST LEAD ===")
if leads:
    print(json.dumps(leads[0], indent=2))
