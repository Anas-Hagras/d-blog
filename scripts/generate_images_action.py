#!/usr/bin/env python3
"""
Git post-commit hook to regenerate images when prompts change.
This script should be called from a git post-commit hook.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_changed_files():
    """Get list of files changed in the last commit"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []

def find_affected_versions(changed_files):
    """Find version directories that need image regeneration"""
    affected_versions = set()
    
    for file_path in changed_files:
        file_path = Path(file_path)
        
        # Check if general image prompt changed
        if str(file_path) == 'prompts/image_generation.txt':
            # If general prompt changed, regenerate all versions
            print("General image prompt changed, marking all versions for regeneration")
            return "all"
        
        # Check if specific version media_prompt.txt changed
        if file_path.name == 'media_prompt.txt' and 'social_media' in file_path.parts:
            version_dir = file_path.parent
            affected_versions.add(str(version_dir))
            print(f"Media prompt changed for: {version_dir}")
        
        # Check if content.txt changed (might affect media prompt)
        if file_path.name == 'content.txt' and 'social_media' in file_path.parts:
            version_dir = file_path.parent
            affected_versions.add(str(version_dir))
            print(f"Content changed for: {version_dir}")
    
    return list(affected_versions)

def regenerate_images(affected_versions):
    """Regenerate images for affected versions"""
    script_path = Path(__file__).parent.parent / "image_generation.py"
    
    if affected_versions == "all":
        print("Regenerating images for all versions...")
        try:
            subprocess.run([sys.executable, str(script_path), "--all"], check=True)
            print("✓ Successfully regenerated all images")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error regenerating all images: {e}")
            return False
    else:
        success_count = 0
        for version_path in affected_versions:
            print(f"Regenerating image for: {version_path}")
            try:
                subprocess.run([sys.executable, str(script_path), version_path], check=True)
                success_count += 1
                print(f"✓ Successfully regenerated image for {version_path}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Error regenerating image for {version_path}: {e}")
        
        print(f"Regenerated images for {success_count}/{len(affected_versions)} versions")
        return success_count == len(affected_versions)
    
    return True

def commit_generated_images():
    """Commit any newly generated images and media history"""
    try:
        # Add all generated images and media history
        subprocess.run(['git', 'add', 'social_media/*/*/v*/media/'], check=True)
        subprocess.run(['git', 'add', 'social_media/*/*/v*/media_history/'], check=True)
        subprocess.run(['git', 'add', 'social_media/*/*/v*/media_prompt.txt'], check=True)
        
        # Check if there are any changes to commit
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            # Commit the changes
            subprocess.run([
                'git', 'commit', 
                '-m', 'Auto-regenerate images after prompt changes (with media history)'
            ], check=True)
            print("✓ Committed regenerated images and media history")
            return True
        else:
            print("No new images to commit")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error committing generated images: {e}")
        return False

def main():
    """Main function for the git hook"""
    print("Checking for prompt changes that require image regeneration...")
    
    # Get changed files
    changed_files = get_changed_files()
    if not changed_files:
        print("No files changed")
        return
    
    print(f"Changed files: {changed_files}")
    
    # Find affected versions
    affected_versions = find_affected_versions(changed_files)
    if not affected_versions:
        print("No prompt changes detected")
        return
    
    # Regenerate images
    if regenerate_images(affected_versions):
        # Commit the generated images
        commit_generated_images()
    else:
        print("Some image regenerations failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
