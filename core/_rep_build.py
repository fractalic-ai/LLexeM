import subprocess
from datetime import datetime
import os

# Define the relative Git repository path
git_repo_path = os.path.join(os.getcwd(), "tests", "Basic_Tests", "Shell_test")

# Specify the branch to limit execution to
specific_branch = "20240908183343_0338efda_Testing-git-operations"

def get_git_logs(branch):
    # Get the logs for the current branch with full message and filenames
    log_cmd = [
        "git", "log", "--pretty=format:%ct %h%nAuthor: %an%nCommitter: %cn%nFull Message: %B%n", 
        "--name-only", "--reverse", branch
    ]
    result = subprocess.run(log_cmd, cwd=git_repo_path, stdout=subprocess.PIPE, text=True)
    logs = result.stdout.splitlines()
    return logs

def format_datetime(epoch_time):
    # Convert UNIX epoch to DateTime including milliseconds
    return datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%d %H:%M:%S.%f")

def extract_metadata(commit_lines):
    """Extract metadata such as the trigger file and operation message from commit lines."""
    metadata = {
        "trigger_file": None,
        "operation": None
    }
    for line in commit_lines:
        if line.startswith("   File: Trigger File:"):
            metadata["trigger_file"] = line.split(":")[-1].strip()
        elif line.startswith("   File: Metadata:"):
            metadata["operation"] = line.split("Metadata:")[-1].strip()
    return metadata

def process_logs(branch, logs):
    results = []
    current_commit_hash = ""
    current_epoch_time = ""
    
    commit_data = {"branch": branch, "commits": []}
    
    for line in logs:
        if line.strip() == "":
            continue
        if line.startswith("Author:") or line.startswith("Committer:") or line.startswith("Full Message:"):
            commit_data["commits"][-1].append(line)
        elif line.replace(" ", "").isalnum() and len(line.split()) == 2:
            # New commit starts
            parts = line.split()
            current_epoch_time = float(parts[0])
            current_commit_hash = parts[1]
            
            date_time = format_datetime(current_epoch_time)
            commit_data["commits"].append([f"Commit: {current_commit_hash}", f"Date: {date_time}"])
        else:
            # Changed files
            commit_data["commits"][-1].append(f"   File: {line}")
    
    results.append(commit_data)
    return results

def find_matching_md(commits, ctx_file):
    # Traverse commits from oldest to newest to find a matching .md file for the given .ctx file
    for commit in commits:
        for item in commit["files"]:
            if item.endswith(".md") and item == ctx_file.replace(".ctx", ".md"):
                return commit  # Found matching .md file
    return None

def analyze_commits_for_ctx_md_pairs(commits):
    levels = {}  # Track levels for each file based on its name

    for commit in reversed(commits):  # Traverse from most recent to oldest
        for file in commit["files"]:
            if file.endswith(".ctx"):
                # Extract metadata (e.g., trigger file, operation) from the current commit
                metadata = extract_metadata(commit["lines"])
                parent_file = metadata["trigger_file"]

                # Determine level based on the parent file
                if not parent_file:
                    current_level = 0  # No parent file, level 0
                elif parent_file in levels:
                    current_level = levels[parent_file] + 1  # Increment based on parent's level
                else:
                    current_level = 1  # Default to level 1 if parent file is not tracked

                # Track the current .ctx file's level
                levels[file] = current_level

                # Find the matching .md file and track its level as well
                matching_md_commit = find_matching_md(commits, file)
                if matching_md_commit:
                    md_file = file.replace(".ctx", ".md")
                    levels[md_file] = current_level  # Track the .md file level
                    print(f"Current Level = {current_level}, (File: {file}, {commit['hash']}, {commit['date']}, operation: {metadata['operation']}, parent file: {metadata['trigger_file']}) vs. (File: {md_file}, {matching_md_commit['hash']}, {matching_md_commit['date']})")
                else:
                    print(f"Warning: Corresponding .md file not found for {file}")

def main():
    final_results = []

    # Fetch logs only for the specific branch
    logs = get_git_logs(specific_branch)
    branch_results = process_logs(specific_branch, logs)
    final_results.extend(branch_results)
    
    # Assuming final_results contains a list of commits with file changes
    commits = []
    for result in final_results:
        for commit_data in result["commits"]:
            commit_info = {
                "hash": commit_data[0].split(":")[1].strip(),
                "date": commit_data[1],  # Use the full date from commit data
                "files": [line.strip() for line in commit_data if line.startswith("   File")],
                "lines": commit_data,
            }
            commits.append(commit_info)
    
    # Analyze commits for .ctx and .md file pairs
    analyze_commits_for_ctx_md_pairs(commits)

if __name__ == "__main__":
    main()
