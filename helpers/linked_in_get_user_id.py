import requests 

access_token = "AQVNzUiQb8zQfxWXhfVzGjV__wakCq-YoMe1VCWdKxuhSoNQiHRrWWGvo4O5wt49h0JZqrw6EXS04y0woRv_t8y2e0d9Rbc_6Bu5VEUjtCF_Y-A7IH5I-N-r1BiQRCqk8gL1XslN9dOKwcB77Z61hEALHlOmOOXvdwa81R9KNtQYQz-x1IcRuqvT2LauVXoKy6wUeFhx6ZONmgTgqIuAcCVV6--NkantY-bc7AXTaLXuBZkfJtaHacAOw6PGHG-XgKGGRnNCcXE7xCqHV_881ztcZzl4u2eX-xbIEDNw9uETVbl_uyIMd9V1Dnm0qiRLi6i2_e_F53wEG2MXy8wYtOBcSZMrRg"

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