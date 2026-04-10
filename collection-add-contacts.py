import pandas as pd
import requests
import time
import re

filename = input("Enter the filename (with .csv extension): ")

# --- CONFIGURATION ---
CSV_FILE = filename
API_URL = "https://api.{chatbot name}.glific.com/api"
GROUP_ID = "19898"
BATCH_SIZE = 15000  # Number of WA IDs to send per request

HEADERS = {
    'Authorization': '{authorization key}',
    'Content-Type': 'application/json'
}

QUERY = """mutation updateGroupContacts($input: GroupContactsInput!) {
  updateGroupContacts(input: $input) {
    groupContacts {
      id
      value
      __typename
    }
    numberDeleted
    __typename
  }
}"""

def update_group_contacts():
    try:
        df = pd.read_csv(CSV_FILE)
        wa_ids = df.iloc[:, 0].dropna().astype(str).tolist()
        wa_ids = [re.sub(r'\D', '', wid) for wid in wa_ids if re.sub(r'\D', '', str(wid))]

        print(f"Total WA IDs to add: {len(wa_ids)}")
        print(f"Group/Collection ID: {GROUP_ID}")
        print(f"Batch size: {BATCH_SIZE}")
        print("-" * 40)

        # Process in batches
        for i in range(0, len(wa_ids), BATCH_SIZE):
            batch = wa_ids[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (len(wa_ids) + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"Batch {batch_num}/{total_batches} ({len(batch)} IDs)...", end=" ", flush=True)

            payload = {
                "operationName": "updateGroupContacts",
                "variables": {
                    "input": {
                        "addContactIds": batch,
                        "groupId": GROUP_ID,
                        "deleteContactIds": []
                    }
                },
                "query": QUERY
            }

            try:
                response = requests.post(API_URL, json=payload, headers=HEADERS)

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        print(f"❌ API Error: {data['errors'][0].get('message', 'Unknown error')}")
                    else:
                        contacts_added = len(data.get("data", {}).get("updateGroupContacts", {}).get("groupContacts", []))
                        print(f"✅ SUCCESS ({contacts_added} contacts added)")
                else:
                    print(f"❌ HTTP Error {response.status_code}")

            except requests.exceptions.RequestException:
                print("⚠️ CONNECTION ERROR")

            time.sleep(1)

        print("-" * 40)
        print("Done!")

    except FileNotFoundError:
        print(f"Error: Could not find '{CSV_FILE}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    update_group_contacts()