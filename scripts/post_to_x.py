import os
import sys
import tweepy
import time
import json
from pathlib import Path

def get_twitter_api():
    # Get Twitter API credentials from environment variables
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    
    # Check if all credentials are available
    if not all([api_key, api_secret, access_token, access_secret]):
        raise ValueError("Twitter API credentials not found in environment variables")
    
    # Authenticate with Twitter API
    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret, access_token, access_secret
    )
    
    # Create API object
    api = tweepy.API(auth)
    
    return api

def post_to_twitter(content_path):
    """
    Post content from a file to Twitter
    
    Args:
        content_path: Path to the content file
    
    Returns:
        dict: Information about the posted tweet
    """
    try:
        # Read content from file
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Get Twitter API
        api = get_twitter_api()
        
        # Post to Twitter
        tweet = api.update_status(content)
        
        # Return tweet information
        return {
            "id": tweet.id,
            "text": tweet.text,
            "created_at": str(tweet.created_at),
            "url": f"https://twitter.com/user/status/{tweet.id}"
        }
    
    except Exception as e:
        print(f"Error posting to Twitter: {str(e)}")
        raise

def process_social_media_content(directory, specific_files=None):
    """
    Process social media content in the given directory
    
    Args:
        directory: Path to the Social_media directory
        specific_files: List of specific files to process (optional)
    
    Returns:
        list: Information about all posted content
    """
    results = []
    
    if specific_files:
        # Process only specific files
        for file_path in specific_files:
            if not file_path.endswith("content.txt"):
                continue
                
            # Get directory structure from file path
            parts = file_path.split(os.sep)
            if len(parts) < 3 or parts[-1] != "content.txt" or parts[-2] != "X":
                continue
                
            # Get page name from directory structure
            page_name = parts[-3]
            
            print(f"Posting content for {page_name} to X...")
            
            try:
                # Post to Twitter
                tweet_info = post_to_twitter(file_path)
                
                # Add page name to tweet info
                tweet_info["page_name"] = page_name
                
                # Add to results
                results.append(tweet_info)
                
                print(f"✅ Posted to X: {tweet_info['url']}")
                
                # Sleep to avoid rate limiting
                time.sleep(5)
            
            except Exception as e:
                print(f"❌ Failed to post {page_name} to X: {str(e)}")
    else:
        # Walk through the Social_media directory
        for root, dirs, files in os.walk(directory):
            # Check if this is an X directory with content.txt
            if os.path.basename(root) == "X" and "content.txt" in files:
                content_path = os.path.join(root, "content.txt")
                
                # Get page name from directory structure
                page_name = os.path.basename(os.path.dirname(root))
                
                print(f"Posting content for {page_name} to X...")
                
                try:
                    # Post to Twitter
                    tweet_info = post_to_twitter(content_path)
                    
                    # Add page name to tweet info
                    tweet_info["page_name"] = page_name
                    
                    # Add to results
                    results.append(tweet_info)
                    
                    print(f"✅ Posted to X: {tweet_info['url']}")
                    
                    # Sleep to avoid rate limiting
                    time.sleep(5)
                
                except Exception as e:
                    print(f"❌ Failed to post {page_name} to X: {str(e)}")
    
    return results

def save_results(results, output_path):
    """
    Save posting results to a JSON file
    
    Args:
        results: List of posting results
        output_path: Path to save the results
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_to_x.py <social_media_directory> [output_file] [file1,file2,...]")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # Default output file
    output_file = "posting_results.json"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Check for specific files
    specific_files = None
    if len(sys.argv) > 3:
        specific_files = sys.argv[3].split(',')
    
    # Process social media content
    results = process_social_media_content(directory, specific_files)
    
    # Save results
    save_results(results, output_file)
    
    print(f"✅ Posted {len(results)} items to X")
    print(f"✅ Results saved to {output_file}")
