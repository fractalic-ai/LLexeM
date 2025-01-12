import os
import hashlib
from datetime import datetime
from pathlib import Path
import git
import shutil
import traceback

# Custom utility function for opening text files with UTF-8 encoding
def open_utf8(file_path, mode='r'):
    """
    Opens a file in text mode with UTF-8 encoding.
    Does not affect binary mode operations.
    
    Args:
        file_path (str): The path to the file.
        mode (str): The mode in which to open the file.
    
    Returns:
        file object: The opened file.
    """
    # Define binary mode indicators
    binary_modes = {'b', 'B'}
    # Check if any binary mode character is present in the mode string
    if any(m in mode for m in binary_modes):
        # Binary mode; do not set encoding
        return open(file_path, mode)
    else:
        # Text mode; set encoding to UTF-8
        return open(file_path, mode, encoding='utf-8')

def is_false(value):
    """
    Determines if the provided value represents a boolean 'false'.
    
    Args:
        value (str or bool): The value to check.
    
    Returns:
        bool: True if the value represents 'false', False otherwise.
    """
    if isinstance(value, bool):
        return not value  # True -> False, False -> True
    elif isinstance(value, str):
        return value.strip().lower() == 'false'
    else:
        # For any other type, consider it not 'false'
        return False

def reset_to_main_branch(repo_path):
    """Switch back to the main branch (or master)."""
    try:
        with git.Repo(repo_path) as repo:
            if 'master' in repo.heads:
                main_branch = 'master'
            elif 'main' in repo.heads:
                main_branch = 'main'
            else:
                raise Exception("No 'master' or 'main' branch found.")

            repo.git.checkout(main_branch)
            # Optional: Uncomment the next line if you want to pull the latest changes
            # repo.remotes.origin.pull()
            # Log success if needed
    except git.exc.GitError as e:
        print(f"[fractalic.git] Error resetting to main branch: {e}")
        traceback.print_exc()
        raise
    except Exception as e:
        print(f"[fractalic.git-e1] {e}")
        traceback.print_exc()
        raise

def ensure_git_repo(repo_path):
    """
    Ensures a Git repository exists at the specified path, creating it if necessary.
    Returns True if a new repo was created, False if it already existed.
    """
    repo_path = os.path.abspath(repo_path)
    git_dir = os.path.join(repo_path, '.git')

    if not os.path.exists(git_dir):
        try:
            os.makedirs(repo_path, exist_ok=True)
            with git.Repo.init(repo_path) as repo:
                configure_git_user(repo_path)
                create_gitignore(repo_path)
                # Initial commit
                repo.index.commit("Initial commit")
            return True
        except git.exc.GitError as e:
            print(f"[fractalic.git] Error initializing repository: {e}")
            traceback.print_exc()
            raise
        except Exception as e:
            print(f"[fractalic.git] Unexpected error initializing repository: {e}")
            traceback.print_exc()
            raise
    else:
        try:
            configure_git_user(repo_path)
            ensure_gitignore(repo_path)
            return False
        except git.exc.GitError as e:
            print(f"[fractalic.git] Error accessing existing repository: {e}")
            traceback.print_exc()
            raise
        except Exception as e:
            print(f"[fractalic.git] Unexpected error accessing repository: {e}")
            traceback.print_exc()
            raise

def cleanup_git_locks(repo_path):
    """Clean up any stale Git lock files."""
    config_lock = os.path.join(repo_path, '.git', 'config.lock')
    if os.path.exists(config_lock):
        try:
            os.remove(config_lock)
            print(f"[fractalic.git] Removed stale lock file: {config_lock}")
        except Exception as e:
            print(f"[fractalic.git] Error removing lock file {config_lock}: {e}")

def configure_git_user(repo_path):
    """Configure Git user settings for the repository."""
    try:
        # Clean up any existing locks first
        cleanup_git_locks(repo_path)
        
        with git.Repo(repo_path) as repo:
            with repo.config_writer() as config:
                config.set_value('user', 'email', 'fractalic_core_agent@fractalic_core_agent.com')
                config.set_value('user', 'name', 'fractalic process')
                config.set_value('core', 'autocrlf', 'false')
                config.set_value('core', 'safecrlf', 'false')
                config.set_value('core', 'ignorecase', 'false')

            with repo.config_reader() as config_reader:
                core_autocrlf = config_reader.get_value('core', 'autocrlf')
                core_safecrlf = config_reader.get_value('core', 'safecrlf')
                core_ignorecase = config_reader.get_value('core', 'ignorecase')

            # Correct configurations if they do not match expected values
            if not is_false(core_autocrlf):
                print(f"[fractalic.git] Warning: core.autocrlf is set to '{core_autocrlf}' (expected 'false')")
                with repo.config_writer() as config_writer:
                    config_writer.set_value('core', 'autocrlf', 'false')

            if not is_false(core_safecrlf):
                print(f"[fractalic.git] Warning: core.safecrlf is set to '{core_safecrlf}' (expected 'false')")
                with repo.config_writer() as config_writer:
                    config_writer.set_value('core', 'safecrlf', 'false')

            if not is_false(core_ignorecase):
                print(f"[fractalic.git] Warning: core.ignorecase is set to '{core_ignorecase}' (expected 'false')")
                with repo.config_writer() as config_writer:
                    config_writer.set_value('core', 'ignorecase', 'false')

    except git.exc.GitError as e:
        print(f"[fractalic.git] Error configuring Git user: {e}")
        traceback.print_exc()
        raise
    except Exception as e:
        print(f"[fractalic.git] Unexpected error configuring Git user: {e}")
        traceback.print_exc()
        raise

def create_gitignore(repo_path):
    """Create .gitignore file with common patterns."""
    gitignore_path = os.path.join(repo_path, '.gitignore')
    if not os.path.exists(gitignore_path):
        try:
            with open_utf8(gitignore_path, 'w') as f:
                f.write(".DS_Store\n")
                f.write("*.pyc\n")
                f.write("__pycache__/\n")
                f.write(".idea/\n")
                f.write(".vscode/\n")
            with git.Repo(repo_path) as repo:
                repo.index.add(['.gitignore'])
                repo.index.commit("Add .gitignore")
            # Log creation if needed
        except Exception as e:
            print(f"[fractalic.git] Warning: Failed to create .gitignore: {e}")
            traceback.print_exc()

def ensure_gitignore(repo_path):
    """Ensure .gitignore exists and contains necessary patterns."""
    gitignore_path = os.path.join(repo_path, '.gitignore')
    needed_patterns = [".DS_Store", "*.pyc", "__pycache__/", ".idea/", ".vscode/"]

    if not os.path.exists(gitignore_path):
        create_gitignore(repo_path)
    else:
        try:
            with open_utf8(gitignore_path, 'r') as f:
                content = f.read()
            missing_patterns = [p for p in needed_patterns if p not in content]
            if missing_patterns:
                with open_utf8(gitignore_path, 'a') as f:
                    for pattern in missing_patterns:
                        f.write(f"{pattern}\n")
                with git.Repo(repo_path) as repo:
                    repo.index.add(['.gitignore'])
                    repo.index.commit("Update .gitignore")
                print("[fractalic.git] Updated .gitignore with missing patterns")
        except Exception as e:
            print(f"[fractalic.git] Warning: Failed to update .gitignore: {e}")
            traceback.print_exc()

def is_git_repo(repo_path):
    """Check if the given path is inside a Git repository."""
    try:
        with git.Repo(repo_path, search_parent_directories=True):
            pass
        return True
    except git.exc.InvalidGitRepositoryError:
        return False
    except Exception as e:
        print(f"[fractalic.git] Error checking if path is a Git repository: {e}")
        traceback.print_exc()
        return False

def create_session_branch(repo_path, task_name):
    """
    Creates a new branch for the session.
    Returns the branch name.
    """
    try:
        with git.Repo(repo_path) as repo:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            hash_digest = hashlib.md5(task_name.encode()).hexdigest()[:8]
            # Sanitize branch name to avoid invalid characters
            safe_task_name = ''.join(c for c in task_name if c.isalnum() or c in ('-', '_'))
            branch_name = f"{timestamp}_{hash_digest}_{safe_task_name}"

            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            # Log branch creation if needed
            return branch_name
    except git.exc.GitError as e:
        print(f"[fractalic.git] Error creating session branch: {e}")
        traceback.print_exc()
        raise
    except Exception as e:
        print(f"[fractalic.git] Unexpected error creating session branch: {e}")
        traceback.print_exc()
        raise

def modify_markdown_file(file_path, content):
    """Modify a markdown file by appending content."""
    try:
        with open_utf8(file_path, 'a') as file:
            file.write(content)
        # Log modification if needed
    except IOError as e:
        print(f"[fractalic.git] Error modifying markdown file: {e}")
        traceback.print_exc()
        raise
    except Exception as e:
        print(f"[fractalic.git] Unexpected error modifying markdown file: {e}")
        traceback.print_exc()
        raise

def get_file_status(repo_path, file_path):
    """
    Check if a file has changes compared to the index.
    Handles files in subdirectories correctly.
    """
    try:
        with git.Repo(repo_path) as repo:
            abs_file_path = os.path.abspath(file_path)
            rel_path = os.path.relpath(abs_file_path, repo.working_tree_dir)

            if not os.path.exists(abs_file_path):
                return "error"

            # Check if the file is untracked
            if rel_path not in repo.untracked_files:
                # Check if the file is modified
                changed_files = [item.a_path for item in repo.index.diff(None)]
                if rel_path in changed_files:
                    return "modified"

                # Check if the file is staged
                staged_changes = [item.a_path for item in repo.index.diff("HEAD")]
                if rel_path in staged_changes:
                    return "staged"

                return "unchanged"
            else:
                return "untracked"

    except Exception as e:
        print(f"[fractalic.git] Error checking file status: {e}")
        traceback.print_exc()
        return "error"

def commit_changes(repo_path, commit_message, files_to_commit, trigger_file=None, metadata=None):
    """Commits changes with proper lock handling."""
    try:
        # Clean up any existing locks before operations
        cleanup_git_locks(repo_path)
        
        with git.Repo(repo_path) as repo:
            # Ensure Git is configured
            configure_git_user(repo_path)
            ensure_gitignore(repo_path)

            # Get current commit hash before changes
            current_hash = repo.head.commit.hexsha

            # Construct commit message
            full_message = commit_message
            if trigger_file or metadata:
                full_message += f"\n\nTrigger File: {trigger_file}\nMetadata: {metadata}"

            if not isinstance(files_to_commit, list):
                files_to_commit = [files_to_commit]

            changes_detected = False
            for file_path in files_to_commit:
                abs_file_path = os.path.abspath(file_path)
                try:
                    rel_path = os.path.relpath(abs_file_path, repo.working_tree_dir)
                except ValueError as e:
                    print(f"[fractalic.git] Error converting path: {e}")
                    traceback.print_exc()
                    continue

                if not os.path.exists(abs_file_path):
                    print(f"[fractalic.git] Warning: File does not exist: {abs_file_path}")
                    continue

                try:
                    target_path = os.path.join(repo.working_tree_dir, rel_path)
                    if not os.path.exists(target_path):
                        # Ensure the directory exists
                        dir_path = os.path.dirname(rel_path)
                        if dir_path and not os.path.exists(os.path.join(repo.working_tree_dir, dir_path)):
                            os.makedirs(os.path.join(repo.working_tree_dir, dir_path), exist_ok=True)
                        # Copy the file
                        shutil.copy2(abs_file_path, target_path)

                    # Check file status
                    status = get_file_status(repo_path, abs_file_path)
                    if status in ["untracked", "modified"]:
                        repo.index.add([rel_path])
                        changes_detected = True
                    elif status == "staged":
                        changes_detected = True
                    else:
                        pass  # File unchanged, nothing to do
                except Exception as e:
                    print(f"[fractalic.git] Error processing file {rel_path}: {e}")
                    traceback.print_exc()
                    continue

            if not changes_detected:
                # Return the current hash if no changes were detected
                return current_hash

            # Perform the commit
            try:
                repo.index.commit(full_message)
            except git.exc.GitError as e:
                print(f"[fractalic.git] Commit failed: {e}")
                traceback.print_exc()
                return current_hash

            # Get new commit hash
            new_hash = repo.head.commit.hexsha
            # Log commit success if needed
            return new_hash

    except Exception as e:
        print(f"[fractalic.git] Error during commit operation: {e}")
        traceback.print_exc()
        return None
