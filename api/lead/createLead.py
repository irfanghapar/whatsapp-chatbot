import requests
import os

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

def create_lead(name, phone, email, inquiry_type, inquiry_info, rating, review, assignee):
    base_url = "https://api.airtable.com/v0/appYPBlFp1Xibe5oX/Leads"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Create a new lead with all provided information
    data = {
        "records": [{
            "fields": {
                "Name": name,
                "Phone": phone,
                "Email": email,
                "Inquiry Type": inquiry_type,
                "Inquiry Info": inquiry_info,
                "Rating": rating,
                "Review": review,
                "Assignee": assignee
            }
        }]
    }
    response = requests.post(base_url, headers=headers, json=data)

    if response.status_code == 200:
        print("Lead created successfully.")
        return response.json()
    else:
        print(f"Failed to create lead: {response.text}")
        return None