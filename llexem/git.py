import os
import subprocess
import hashlib
from datetime import datetime

def init_git_repo(repo_path):
    subprocess.run(['git', 'config', 'user.email', 'llexem_core_agent@llexem_core_agent.com'], cwd=repo_path)
    subprocess.run(['git', 'config', 'user.name', 'llexem process'], cwd=repo_path)
  
    if not os.path.exists(os.path.join(repo_path, '.git')):
        subprocess.run(['git', 'init'], cwd=repo_path)
        print(f"[llexem.git] Initialized empty Git repository in {repo_path}")
    else:
        print(f"[llexem.git] Git repository already exists in {repo_path}")

def create_session_branch(repo_path, task_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_digest = hashlib.md5(task_name.encode()).hexdigest()[:8]
    branch_name = f"{timestamp}_{hash_digest}_{task_name}"
    subprocess.run(['git', 'checkout', '-b', branch_name], cwd=repo_path)
    print(f"[llexem.git] Created and switched to new branch {branch_name}")
    return branch_name

def modify_markdown_file(file_path, content):
    with open(file_path, 'a') as file:
        file.write(content)

def commit_changes(repo_path, commit_message, trigger_file, metadata):
    full_commit_message = f"{commit_message}\n\nTrigger File: {trigger_file}\nMetadata: {metadata}"
    subprocess.run(['git', 'add', '.'], cwd=repo_path)
    subprocess.run(['git', 'commit', '-m', full_commit_message], cwd=repo_path)

def get_commit_history(repo_path, branch_name):
    result = subprocess.run(['git', 'log', '--pretty=format:%h %ad %s', '--date=short', branch_name], cwd=repo_path, capture_output=True, text=True)
    return result.stdout.split('\n')

def get_file_commit_history(repo_path, branch_name, file_path):
    result = subprocess.run(['git', 'log', '--pretty=format:%h %ad %s', '--date=short', branch_name, '--', file_path],
                            cwd=repo_path, capture_output=True, text=True)
    return result.stdout.split('\n')

def get_commit_diff(repo_path, commit_hash):
    result = subprocess.run(['git', 'show', commit_hash], cwd=repo_path, capture_output=True, text=True)
    return result.stdout