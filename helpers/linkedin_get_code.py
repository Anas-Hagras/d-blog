import requests
from urllib.parse import quote

# Replace these with your app's credentials
CLIENT_ID = "aa"
REDIRECT_URI = "https://localhost"  # Must match your app's redirect URI

SCOPES = "openid profile w_member_social"
auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization?"
    f"response_type=code&client_id={CLIENT_ID}&"
    f"redirect_uri={quote(REDIRECT_URI)}&scope={quote(SCOPES)}"
)

print(f"Open this URL in your browser and authenticate:\n{auth_url}")