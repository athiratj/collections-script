import pandas as pd
import requests
import time
import re

# Ask for the file containing the IDs you want to remove
filename = input("Enter the filename of IDs to REMOVE (with .csv extension): ")

# --- CONFIGURATION ---
CSV_FILE = filename
API_URL = "https://api.{chatbot name}.glific.com/api"
GROUP_ID = "19898"
BATCH_SIZE = 1000  # Removal is often safer in smaller batches depending on server load

HEADERS = {
    'Authorization': '{authorization key}',
    'Content-Type': 'application/json'
}

# The mutation remains the same as it handles both adding and deleting
QUERY = """mutation updateGroupContacts($input: GroupContactsInput!) {
  updateGroupContacts(input: $input) {
    numberDeleted
    __typename
  }
}"""

def remove_group_contacts():
    try:
        # Load the CSV
        df = pd.read_csv(CSV_FILE)
        
        # Assume WA IDs are in the first column
        wa_ids = df.iloc[:, 0].dropna().astype(str).tolist()
        # Clean the IDs (keep only digits)
        wa_ids = [re.sub(r'\D', '', wid) for wid in wa_ids if re.sub(r'\D', '', str(wid))]

        print(f"Total WA IDs to remove: {len(wa_ids)}")
        print(f"Target Group ID: {GROUP_ID}")
        print("-" * 40)

        for i in range(0, len(wa_ids), BATCH_SIZE):
            batch = wa_ids[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (len(wa_ids) + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"Processing Batch {batch_num}/{total_batches}...", end=" ", flush=True)

            payload = {
                "operationName": "updateGroupContacts",
                "variables": {
                    "input": {
                        "addContactIds": [],        # Leave this empty
                        "groupId": GROUP_ID,
                        "deleteContactIds": batch   # Put IDs here to remove them
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
                        # The API returns 'numberDeleted' for removals
                        deleted_count = data.get("data", {}).get("updateGroupContacts", {}).get("numberDeleted", 0)
                        print(f"✅ SUCCESS ({deleted_count} contacts removed)")
                else:
                    print(f"❌ HTTP Error {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ CONNECTION ERROR: {e}")

            time.sleep(1) # Short delay to avoid rate limiting

        print("-" * 40)
        print("Removal Process Complete!")

    except FileNotFoundError:
        print(f"Error: Could not find '{CSV_FILE}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    remove_group_contacts()