"""
Social media poster implementation.
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from .platforms import SocialMediaPlatform
from .platforms.twitter import TwitterPlatform


class SocialMediaPoster:
    """Class for posting content to social media platforms."""
    
    def __init__(self, output_path: str = "posting_results.json"):
        """
        Initialize the poster.
        
        Args:
            output_path: Path to save the posting results
        """
        self.output_path = output_path
        self.results = []
        
        # Initialize available platforms
        self.platforms = self._initialize_platforms()
    
    def _initialize_platforms(self) -> Dict[str, SocialMediaPlatform]:
        """
        Initialize available platforms.
        
        Returns:
            Dict of platform name to platform instance
        """
        platforms = {}
        
        # Add Twitter platform
        platforms["X"] = TwitterPlatform()
        
        # Add more platforms here as they are implemented
        # platforms["LinkedIn"] = LinkedInPlatform()
        
        return platforms
    
    def read_content(self, content_path: str) -> str:
        """
        Read content from a file.
        
        Args:
            content_path: Path to the content file
            
        Returns:
            The content as a string
        """
        with open(content_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def post_from_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Post content from a folder to social media platforms.
        
        The folder structure should be:
        folder_path/
            platform1/
                content.txt
            platform2/
                content.txt
            ...
        
        Args:
            folder_path: Path to the folder containing platform folders
            
        Returns:
            List of posting results
        """
        folder = Path(folder_path)
        page_name = folder.name
        
        # Get platform folders
        platform_folders = [p for p in folder.iterdir() if p.is_dir()]
        
        for platform_folder in platform_folders:
            platform_name = platform_folder.name
            content_file = platform_folder / "content.txt"
            
            # Skip if content file doesn't exist
            if not content_file.exists():
                print(f"Content file not found for {page_name}/{platform_name}")
                continue
            
            # Skip if platform is not supported
            if platform_name not in self.platforms:
                print(f"Platform '{platform_name}' is not supported")
                continue
            
            self._post_content(content_file, platform_name, page_name)
        
        # Save results
        self.save_results()
        
        return self.results
    
    def _post_content(self, content_file: Path, platform_name: str, page_name: str):
        """
        Post content from a file to a platform.
        
        Args:
            content_file: Path to the content file
            platform_name: Name of the platform
            page_name: Name of the page
        """
        print(f"Publishing content for {page_name} to {platform_name}...")
        
        try:
            # Get platform instance
            platform = self.platforms.get(platform_name)
            if not platform:
                print(f"Platform '{platform_name}' is not supported")
                return
            
            # Read content
            content = self.read_content(str(content_file))
            
            # Post content
            result = platform.post_content(content, page_name)
            
            # Add to results
            self.results.append(result)
            
            if result.get("status") == "success":
                print(f"✅ Posted to {platform_name}: {result.get('url')}")
            else:
                print(f"❌ Failed to post to {platform_name}: {result.get('error')}")
            
            # Sleep to avoid rate limiting
            time.sleep(5)
        
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error publishing to {platform_name}: {error_message}")
            
            # Add error to results
            self.results.append({
                "platform": platform_name,
                "page_name": page_name,
                "id": "",
                "text": "",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                "status": "error",
                "error": error_message
            })
    
    def save_results(self):
        """Save results to a JSON file."""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
