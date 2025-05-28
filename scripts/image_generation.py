import openai
import requests
import os
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
PROMPT = "A futuristic cityscape at sunset with flying cars and neon lights"
MODEL = "dall-e-3"  # or "dall-e-2"
SIZE = "1024x1024"  # For DALL-E 3: "1024x1024", "1024x1792", or "1792x1024"
QUALITY = "standard"  # or "hd" (for DALL-E 3)
OUTPUT_DIR = "generated_images"  # Directory to save images

def generate_and_save_image():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate the image
    try:
        response = openai.images.generate(
            model=MODEL,
            prompt=PROMPT,
            size=SIZE,
            quality=QUALITY,
            n=1,
        )
        image_url = response.data[0].url
        
        # Download and save the image
        image_data = requests.get(image_url).content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/image_{timestamp}.png"
        
        with open(filename, "wb") as f:
            f.write(image_data)
        
        print(f"Image successfully saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error generating/saving image: {e}")
        return None

if __name__ == "__main__":
    openai.api_key = OPENAI_API_KEY
    print("Starting image generation...")
    generate_and_save_image()