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
    # Use --diff-filter=A to only get added files (A = Added)
    # This ensures we only get truly new files, not modified ones
    command = f"git diff --name-only --diff-filter=A {base_ref} {head_ref}"
    output = run_command(command)
    print(f"Git diff added files between {base_ref} and {head_ref}: {output}")
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
    
    # Get detailed file information from the PR
    debug_command = f"gh pr view {pr_number} --json files"
    debug_output = run_command(debug_command)
    print(f"Raw PR files data: {debug_output}")
    
    # Print more detailed debug information about each file
    detailed_debug_command = f"gh pr view {pr_number} --json files --jq '.files[] | {{path: .path, additions: .additions, deletions: .deletions, status: .status}}'"
    detailed_debug_output = run_command(detailed_debug_command)
    print(f"Detailed file information: {detailed_debug_output}")
    
    # Get all files in the PR
    all_files_command = f"gh pr view {pr_number} --json files --jq '.files[].path'"
    all_files_output = run_command(all_files_command)
    if not all_files_output:
        print("No files found in PR")
        return []
    
    all_files = all_files_output.split("\n")
    print(f"All files in PR: {all_files_output}")
    
    # Try to detect truly new files using git diff
    # First, get the base and head commits of the PR
    pr_info_command = f"gh pr view {pr_number} --json baseRefName,headRefName"
    pr_info_output = run_command(pr_info_command)
    print(f"PR info: {pr_info_output}")
    
    # Extract base and head refs
    base_ref_command = f"gh pr view {pr_number} --json baseRefName --jq '.baseRefName'"
    head_ref_command = f"gh pr view {pr_number} --json headRefName --jq '.headRefName'"
    base_ref = run_command(base_ref_command)
    head_ref = run_command(head_ref_command)
    
    if base_ref and head_ref:
        print(f"PR base ref: {base_ref}, head ref: {head_ref}")
        
        # Use git diff with --diff-filter=A to only get added files
        # This is the most reliable way to detect truly new files
        diff_command = f"git diff --name-only --diff-filter=A origin/{base_ref}...origin/{head_ref}"
        diff_output = run_command(diff_command)
        print(f"Git diff added files: {diff_output}")
        
        if diff_output:
            new_files = diff_output.split("\n")
            new_pages = [f for f in new_files if f.startswith("_pages/")]
            if new_pages:
                print(f"New pages detected via git diff: {new_pages}")
                return new_pages
    
    # Fallback to the previous method if git diff didn't work
    print("Falling back to additions/deletions method")
    new_files_command = f"gh pr view {pr_number} --json files --jq '.files[] | select(.additions > 0 and .deletions == 0) | .path'"
    new_files_output = run_command(new_files_command)
    print(f"New files (additions > 0, deletions == 0): {new_files_output}")
    
    # If we found new files, filter them for _pages directory
    if new_files_output:
        new_files = new_files_output.split("\n")
        new_pages = [f for f in new_files if f.startswith("_pages/")]
        print(f"New files in _pages directory: {new_pages}")
        if new_pages:
            return new_pages
    
    # If no new pages found, return empty list
    print("No new pages detected")
    
    return []

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
        # Use newline-separated format for better readability in PR comments
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            # Use the multiline delimiter format for GitHub Actions outputs
            f.write("new_pages<<EOF\n")
            f.write("\n".join(new_pages) + "\n")
            f.write("EOF\n")
    else:
        print("No new pages detected")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            # Use the same multiline format for consistency
            f.write("new_pages<<EOF\n")
            f.write("EOF\n")
