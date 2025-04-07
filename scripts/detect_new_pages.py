import os
import sys
import subprocess
import re
from pathlib import Path

def run_command(command):
    """
    Run a shell command and return the output
    
    Args:
        command: Command to run
    
    Returns:
        str: Command output
    """
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {process.stderr}")
        return ""
    return process.stdout.strip()

def get_added_files(base_ref, head_ref):
    """
    Get files added between two Git references
    
    Args:
        base_ref: Base Git reference (e.g., HEAD~1)
        head_ref: Head Git reference (e.g., HEAD)
    
    Returns:
        list: List of added files
    """
    # Use --diff-filter=A to only get added files
    command = f"git diff --name-only --diff-filter=A {base_ref} {head_ref}"
    output = run_command(command)
    if not output:
        return []
    return output.split("\n")

def filter_new_pages(changed_files, pages_dir="_pages"):
    """
    Filter new pages from changed files
    
    Args:
        changed_files: List of changed files
        pages_dir: Directory containing pages
    
    Returns:
        list: List of new pages
    """
    # Pattern to match page files (e.g., _pages/YYYY-MM-DD-title.md)
    page_pattern = re.compile(f"^{pages_dir}/.*\\.md$")
    
    # Filter files that match the pattern
    new_pages = [f for f in changed_files if page_pattern.match(f)]
    
    return new_pages

def get_latest_commit():
    """
    Get the latest commit hash
    
    Returns:
        str: Latest commit hash
    """
    command = "git rev-parse HEAD"
    return run_command(command)

def get_previous_commit(current_commit):
    """
    Get the previous commit hash
    
    Args:
        current_commit: Current commit hash
    
    Returns:
        str: Previous commit hash
    """
    command = f"git rev-parse {current_commit}~1"
    return run_command(command)

def get_pr_added_files():
    """
    Get files added in a PR from GitHub event payload
    
    Returns:
        list: List of added files
    """
    # Get PR number from environment variable
    pr_number = os.getenv("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER environment variable not set")
        return []
    
    print(f"Checking PR #{pr_number} for added files")
    
    # First, get all files in the PR to debug
    debug_command = f"gh pr view {pr_number} --json files"
    debug_output = run_command(debug_command)
    print(f"Raw PR files data: {debug_output}")
    
    # Get all files regardless of status to see what's available
    all_files_command = f"gh pr view {pr_number} --json files --jq '.files[].path'"
    all_files_output = run_command(all_files_command)
    print(f"All files in PR: {all_files_output}")
    
    # Get added files from GitHub API
    # We need to filter for added files only
    command = f"gh pr view {pr_number} --json files --jq '.files[] | select(.status==\"added\") | .path'"
    output = run_command(command)
    print(f"Files with status 'added': {output}")
    
    # Try alternative approach - get all files in _pages directory
    pages_command = f"gh pr view {pr_number} --json files --jq '.files[] | select(.path | startswith(\"_pages/\")) | .path'"
    pages_output = run_command(pages_command)
    print(f"Files in _pages directory: {pages_output}")
    
    # If no added files found, use files in _pages directory as fallback
    if not output and pages_output:
        print("No files with status 'added' found, using files in _pages directory as fallback")
        return pages_output.split("\n")
    
    if not output:
        return []
    
    return output.split("\n")

def detect_new_pages(base_ref=None, head_ref=None, pages_dir="_pages", pr_mode=False):
    """
    Detect new pages between two Git references or in a PR
    
    Args:
        base_ref: Base Git reference (default: previous commit)
        head_ref: Head Git reference (default: current commit)
        pages_dir: Directory containing pages
        pr_mode: Whether to use PR mode (default: False)
    
    Returns:
        list: List of new pages
    """
    if pr_mode:
        # Get added files from PR
        changed_files = get_pr_added_files()
    else:
        # If no references provided, use current and previous commits
        if not head_ref:
            head_ref = get_latest_commit()
        if not base_ref:
            base_ref = get_previous_commit(head_ref)
        
        # Get added files
        changed_files = get_added_files(base_ref, head_ref)
    
    # Filter new pages
    new_pages = filter_new_pages(changed_files, pages_dir)
    
    return new_pages

if __name__ == "__main__":
    # Parse command line arguments
    base_ref = None
    head_ref = None
    pages_dir = "_pages"
    pr_mode = False
    
    # Check for --pr-mode flag
    if "--pr-mode" in sys.argv:
        pr_mode = True
        sys.argv.remove("--pr-mode")
    
    if len(sys.argv) > 1:
        base_ref = sys.argv[1]
    if len(sys.argv) > 2:
        head_ref = sys.argv[2]
    if len(sys.argv) > 3:
        pages_dir = sys.argv[3]
    
    # Detect new pages
    new_pages = detect_new_pages(base_ref, head_ref, pages_dir, pr_mode)
    
    # Print new pages
    if new_pages:
        print("New pages detected:")
        for page in new_pages:
            print(page)
        
        # Print as JSON for GitHub Actions using Environment Files
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"new_pages={','.join(new_pages)}\n")
    else:
        print("No new pages detected")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write("new_pages=\n")
