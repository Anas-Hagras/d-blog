import requests
from urllib.parse import quote

# Replace these with your app's credentials
CLIENT_ID = "77ry6lekl30di4"
REDIRECT_URI = "https://localhost" 

# Paste the authorization code from the redirect URL
AUTHORIZATION_CODE = "AQQZYtzVPV8FWMT99G13GCgx2LeQDt0PczoxFG2j2RBY2cK1wZCR_jQPELJEutgSxfix03QEJ7oup1ayGjp52g8Lj8idE7cSMUzZiVsyKuiwpl61IQdFJo2m9KmagpF54G0TPuOUnwhujBgBnGS9ixuu0rs4nPUhess4FFluAxibJBGfRa5S7PVEtND3Oyuk47eXugBLgc6WhspBZSs"
CLIENT_SECRET = "WPL_AP1.jioMOLxIVJ3OQ5Eu.f4CSUw==" 

# Request access token
token_url = "https://www.linkedin.com/oauth/v2/accessToken"
data = {
    "grant_type": "authorization_code",
    "code": AUTHORIZATION_CODE,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

response = requests.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

if response.status_code == 200:
    access_token = response.json().get("access_token")
    print(f"Access Token: {access_token}")
else:
    print(f"Error: {response.status_code} - {response.text}")