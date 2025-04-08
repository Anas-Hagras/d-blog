"""
Twitter (X) platform implementation.
"""
import os
import tweepy
from typing import Dict, Any

from ..platforms import SocialMediaPlatform


class TwitterPlatform(SocialMediaPlatform):
    """Twitter (X) platform implementation."""
    
    def __init__(self):
        """Initialize the Twitter platform."""
        super().__init__("X")
    
    def get_client(self):
        """Initialize Twitter v2 API client."""
        return tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
            wait_on_rate_limit=True
        )
    
    def post_content(self, content: str, page_name: str) -> Dict[str, Any]:
        """
        Post content to Twitter.
        
        Args:
            content: The content to post
            page_name: The name of the page
            
        Returns:
            Dict containing the result of the posting operation
        """
        try:
            client = self.get_client()
            response = client.create_tweet(text=content)  # Uses v2 endpoint
            
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            
            return self.create_success_result(page_name, content, tweet_id, tweet_url)
        except Exception as e:
            error_message = str(e)
            print(f"Error posting to Twitter: {error_message}")
            
            return self.create_error_result(page_name, content, error_message)
