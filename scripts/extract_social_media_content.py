import sys
import os
from pathlib import Path
import yaml
from openai import OpenAI

# Import the SocialMediaPoster to get available platforms
from posting import SocialMediaPoster

# Import the ImageGenerator for automatic image generation
from image_generation import ImageGenerator

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=api_key)

def extract_markdown_content(filepath):
    """
    Extract front matter and content from a markdown file.
    
    Args:
        filepath: Path to the markdown file
        
    Returns:
        Tuple of (front_matter, content)
    """
    with open(filepath, 'r') as f:
        content = f.read()
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            # Return raw markdown content instead of converting to HTML
            markdown_content = parts[2].strip()
            return front_matter, markdown_content
        else:
            return {}, content

def get_prompt_for_platform(platform, content):
    """
    Get the prompt for a platform from a file.
    
    Args:
        platform: Platform name
        content: Content to include in the prompt
        
    Returns:
        str: Prompt for the platform
    """
    # Check if a prompt file exists for this platform
    prompt_file = os.path.join("prompts", f"{platform}.txt")
    
    if os.path.exists(prompt_file):
        # Read prompt from file
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Replace {content} placeholder with actual content
        prompt = prompt_template.replace("{content}", content)
    else:
        # Use default prompt if no file exists
        prompt = f"""
        Summarize the following blog post into an engaging {platform} post.
        
        Blog Post:
        {content}
        
        {platform} post:
        """
    
    return prompt

def generate_social_media_content(content, platform):
    # Get prompt for this platform
    prompt = get_prompt_for_platform(platform, content)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7
    )

    summary = response.choices[0].message.content.strip()
    return summary

def get_page_name(filepath):
    # Extract the filename without extension
    filename = os.path.basename(filepath)
    page_name = os.path.splitext(filename)[0]
    
    # Keep the date prefix - don't remove it
    # Ensure the page name is properly escaped for use in folder names
    # This preserves spaces and special characters in the folder name
    return page_name

def save_social_media_content(page_name, platform, content):
    # Base directory for this page and platform
    base_dir = os.path.join("social_media", page_name, platform)
    
    # Find the latest version number
    latest_version = 0
    if os.path.exists(base_dir):
        # Get all version directories
        version_dirs = [d for d in os.listdir(base_dir) if d.startswith('v') and os.path.isdir(os.path.join(base_dir, d))]
        
        # Extract version numbers
        version_numbers = []
        for d in version_dirs:
            try:
                # Extract number from 'v1', 'v2', etc.
                version_num = int(d[1:])
                version_numbers.append(version_num)
            except ValueError:
                # Skip directories that don't follow the pattern
                continue
        
        # Find the highest version number
        if version_numbers:
            latest_version = max(version_numbers)
    
    # Create new version directory
    new_version = latest_version + 1
    version_dir = os.path.join(base_dir, f"v{new_version}")
    os.makedirs(version_dir, exist_ok=True)
    
    # Save content to file
    filepath = os.path.join(version_dir, "content.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Generate image for this version
    try:
        image_generator = ImageGenerator()
        if image_generator.process_social_media_version(version_dir):
            print(f"✅ Image generated for {platform} v{new_version}")
        else:
            print(f"⚠️ Failed to generate image for {platform} v{new_version}")
    except Exception as e:
        print(f"⚠️ Error generating image for {platform} v{new_version}: {e}")
    
    return filepath

def get_available_platforms():
    """
    Get available platforms from the SocialMediaPoster.
    
    Returns:
        List of platform names
    """
    # Create a temporary poster to get available platforms
    platforms = SocialMediaPoster.get_platforms(keys_only=True)
    return platforms

def process_page(filepath, platforms=None):
    """
    Process a page and generate social media content for each platform.
    
    Args:
        filepath: Path to the markdown file
        platforms: List of platforms to generate content for (default: all available platforms)
        
    Returns:
        Dict of platform to output path
    """
    if platforms is None:
        # Get all available platforms
        platforms = get_available_platforms()
    
    # Extract content from markdown file
    front_matter, content = extract_markdown_content(filepath)
    
    # Get page name
    page_name = get_page_name(filepath)
    
    results = {}
    
    # Generate and save content for each platform
    for platform in platforms:
        social_content = generate_social_media_content(content, platform)
        output_path = save_social_media_content(page_name, platform, social_content)
        results[platform] = output_path
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_social_media_content.py <markdown_file> [platform1,platform2,...]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Check if specific platforms are requested
    platforms = None
    if len(sys.argv) > 2:
        platforms = sys.argv[2].split(',')
    
    # Process the page
    results = process_page(filepath, platforms)
    
    # Print results
    for platform, path in results.items():
        print(f"✅ {platform} content saved to {path}")
