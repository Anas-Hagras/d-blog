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
        return ""
    return process.stdout.strip()

def get_git_references(base_ref=None, head_ref=None):
    """
    Get Git references for comparison
    
    Args:
        base_ref: Base Git reference (default: previous commit)
        head_ref: Head Git reference (default: current commit)
    
    Returns:
        tuple: (base_ref, head_ref)
    """
    if not head_ref:
        head_ref = run_command("git rev-parse HEAD")
    if not base_ref:
        base_ref = run_command(f"git rev-parse {head_ref}~1")
    
    return base_ref, head_ref

def get_added_files_from_git(base_ref, head_ref):
    """
    Get files added between two Git references using git diff
    
    Args:
        base_ref: Base Git reference
        head_ref: Head Git reference
    
    Returns:
        list: List of added files
    """
    # Use --diff-filter=A to only get added files (A = Added)
    command = f"git diff --name-only --diff-filter=A {base_ref} {head_ref}"
    output = run_command(command)
    
    if not output:
        return []
    
    return output.split("\n")

def get_added_files_from_pr():
    """
    Get files added in a PR using GitHub CLI
    
    Returns:
        list: List of added files
    """
    # Get PR number from environment variable
    pr_number = os.getenv("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER environment variable not set")
        return []
    
    # Get the base commit SHA of the PR
    base_sha = run_command(f"gh pr view {pr_number} --json baseRefOid --jq '.baseRefOid'")
    if not base_sha:
        return []
    
    # Get files with additions > 0 and deletions == 0 (likely new files)
    command = f"gh pr view {pr_number} --json files --jq '.files[] | select(.additions > 0 and .deletions == 0) | .path'"
    output = run_command(command)
    
    if not output:
        return []
    
    potential_new_files = output.split("\n")
    
    # Verify each file is truly new by checking if it existed in the base commit
    truly_new_files = []
    for file_path in potential_new_files:
        # Check if the file existed in the base commit
        check_command = f"git cat-file -e {base_sha}:{file_path} 2>/dev/null || echo 'not_exists'"
        result = run_command(check_command)
        
        if result == 'not_exists':
            truly_new_files.append(file_path)
    
    return truly_new_files

def filter_pages(files, pages_dir="_pages"):
    """
    Filter files to only include pages
    
    Args:
        files: List of files
        pages_dir: Directory containing pages
    
    Returns:
        list: List of page files
    """
    # Pattern to match page files (e.g., _pages/YYYY-MM-DD-title.md)
    page_pattern = re.compile(f"^{pages_dir}/.*\\.md$")
    
    # Filter files that match the pattern
    return [f for f in files if page_pattern.match(f)]

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
    # Get added files based on mode
    if pr_mode:
        added_files = get_added_files_from_pr()
    else:
        # Get Git references
        base_ref, head_ref = get_git_references(base_ref, head_ref)
        added_files = get_added_files_from_git(base_ref, head_ref)
    
    # Filter to only include pages
    new_pages = filter_pages(added_files, pages_dir)
    
    if new_pages:
        print(f"Found {len(new_pages)} new pages")
    else:
        print("No new pages detected")
    
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
        
        # Output for GitHub Actions if GITHUB_OUTPUT is set
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write("new_pages<<EOF\n")
                f.write("\n".join(new_pages) + "\n")
                f.write("EOF\n")
    else:
        print("No new pages detected")
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write("new_pages<<EOF\n")
                f.write("EOF\n")
