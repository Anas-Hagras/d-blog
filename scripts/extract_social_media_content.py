import sys
import os
from pathlib import Path
import yaml
import markdown
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_markdown_content(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            markdown_content = markdown.markdown(parts[2])
            return front_matter, markdown_content
        else:
            return {}, content

def generate_social_media_content(content, platform):
    prompt = f"""
    Summarize the following blog post into an engaging and exciting {platform} post. Use a direct, thoughtful, concise, and reflective style. Start with an intriguing hook or bold statement. Include a short personal anecdote or surprising insight. End with a provocative question or actionable takeaway that encourages interaction.

    For LinkedIn, Email List, Reddit, and Telegram: Maintain a professional, wise, and thoughtful tone. Avoid emojis entirely.

    For X (Twitter), TikTok, and Instagram: Be playful and adventurous. Emojis may be used sparingly.

    Blog Post:
    {content}

    {platform} post:
    """

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
    
    # Remove the date prefix if it exists (YYYY-MM-DD-)
    if len(page_name) > 11 and page_name[4] == '-' and page_name[7] == '-' and page_name[10] == '-':
        page_name = page_name[11:]
    
    return page_name

def save_social_media_content(page_name, platform, content):
    # Create directory structure if it doesn't exist
    directory = os.path.join("Social_media", page_name, platform)
    os.makedirs(directory, exist_ok=True)
    
    # Save content to file
    filepath = os.path.join(directory, "content.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def process_page(filepath, platforms=None):
    if platforms is None:
        platforms = ["X"]  # Default to X only
    
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
    
    platforms = None
    if len(sys.argv) > 2:
        platforms = sys.argv[2].split(',')
    
    results = process_page(filepath, platforms)
    
    for platform, path in results.items():
        print(f"✅ {platform} content saved to {path}")
