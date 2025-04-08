"""
File platform implementation for testing and mocking
"""
import os
import time
from typing import Dict, Any, List
from pathlib import Path

from ..platforms import SocialMediaPlatform

class FilePlatform(SocialMediaPlatform):
    """File platform implementation for testing and mocking."""
    
    def __init__(self):
        super().__init__("File")
        self.output_dir = os.path.join("output", "file_posts")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def post_content(self, content: str, page_name: str, platform_folder: str = None) -> Dict[str, Any]:
        """
        Post content to a file.
        
        Args:
            content: The content to post
            page_name: The name of the page
            platform_folder: Path to the platform folder (for finding media)
            
        Returns:
            Dict containing the result of the posting operation
        """
        try:
            # Create timestamp for unique filename
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
            
            # Create output filename
            filename = f"{page_name}_{timestamp}.txt"
            output_path = os.path.join(self.output_dir, filename)
            
            # Write content to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
                # Add media files if available
                if platform_folder:
                    media_files = self.find_media_files(platform_folder)
                    if media_files:
                        f.write("\n\n--- Media Files ---\n")
                        for media_file in media_files:
                            f.write(f"\n- {os.path.basename(media_file)}")
            
            # Create post ID (just use the filename)
            post_id = filename
            
            # Create URL (just use the file path)
            url = f"file://{os.path.abspath(output_path)}"
            
            print(f"✅ Posted to file: {output_path}")
            
            return self.create_success_result(page_name, content, post_id, url)
            
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error writing to file: {error_message}")
            return self.create_error_result(page_name, content, error_message)
    
    def find_media_files(self, platform_folder: str) -> List[str]:
        """
        Find media files in the platform folder.
        
        Args:
            platform_folder: Path to the platform folder
            
        Returns:
            List of media file paths
        """
        # Get the directory containing the content.txt file
        folder = os.path.dirname(platform_folder) if os.path.isfile(platform_folder) else platform_folder
        
        # Find all media files (images, videos, documents)
        image_extensions = ['jpg', 'jpeg', 'png', 'gif']
        video_extensions = ['mp4', 'mov', 'avi']
        document_extensions = ['pdf', 'doc', 'docx', 'txt']
        
        media_files = []
        
        # Find all files in the folder
        for file in os.listdir(folder):
            # Skip content.txt and posting_results.json
            if file in ['content.txt', 'posting_results.json']:
                continue
                
            # Check if file has a supported extension
            ext = file.split('.')[-1].lower()
            if ext in image_extensions + video_extensions + document_extensions:
                media_files.append(os.path.join(folder, file))
        
        return media_files
