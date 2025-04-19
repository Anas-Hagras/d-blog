import requests 

access_token = "aa"

headers = {
    "Authorization": f"Bearer {access_token}",
    "X-Restli-Protocol-Version": "2.0.0",
}

# Fetch user profile
profile_response = requests.get("https://api.linkedin.com/v2/me", headers=headers)

if profile_response.status_code == 200:
    user_id = profile_response.json().get("id")  # Format: "urn:li:person:123456"
    print(f"User ID: {user_id}")
else:
    print(f"Error fetching profile: {profile_response.text}")