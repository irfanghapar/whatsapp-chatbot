import requests
import os

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

def list_records():
    base_url = "https://api.airtable.com/v0/appYPBlFp1Xibe5oX/Leads"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    check_url = f"{base_url}?maxRecords=100&view=Grid%20view"
    response = requests.get(check_url, headers=headers)

    if response.status_code == 200:
        return response.json().get('records', [])
    else:
        print(f"Failed to fetch records: {response.text}")
        return None