"""
Twitter (X) platform implementation using Tweepy API v2
"""
import os
import tweepy
from typing import Dict, Any

from ..platforms import SocialMediaPlatform

class TwitterPlatform(SocialMediaPlatform):
    """Twitter (X) platform implementation using API v2."""
    
    def __init__(self):
        super().__init__("X")
        self._verify_credentials()
    
    def _verify_credentials(self):
        required_creds = [
            "X_API_KEY",
            "X_API_SECRET",
            "X_ACCESS_TOKEN", 
            "X_ACCESS_SECRET"
        ]
        missing = [cred for cred in required_creds if not os.getenv(cred)]
        if missing:
            raise ValueError(f"Missing credentials: {', '.join(missing)}")
    
    def get_client(self) -> tweepy.Client:
        """Initialize and return Twitter v2 API client."""
        return tweepy.Client(
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_SECRET"),
        )

    def post_content(self, content: str, page_name: str) -> Dict[str, Any]:
        """Post content to Twitter using API v2."""
        try:
            client = self.get_client()
            response = client.create_tweet(text=content)
            tweet_id = response.data['id']
            
            user_info = client.get_me(user_auth=True)
            username = user_info.data.username

            tweet_url = f"https://x.com/{username}/status/{tweet_id}"
            return self.create_success_result(page_name, content, tweet_id, tweet_url)
            
        except tweepy.TweepyException as e:
            error_msg = f"Twitter API Error: {str(e)}"
            return self.create_error_result(page_name, content, error_msg)