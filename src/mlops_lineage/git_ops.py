"""
Git operations module

Provides functions for Git operations including:
- Getting current commit hash
- Creating and managing git worktrees for reproducibility

Author: MLOps Team
Date: January 2026
"""

from pathlib import Path
from typing import Optional
from .shell import run_command, print_success, print_info
from .config import config


def get_current_commit() -> str:
    """
    Get the current Git commit hash (short form).
    
    Returns:
        Current commit hash (7 characters)
        
    Raises:
        RuntimeError: If not in a git repository or git command fails
    """
    _, stdout, _ = run_command(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=str(config.REPO_ROOT),
        capture_output=True,
    )
    return stdout.strip()


def get_full_commit(short_hash: str) -> str:
    """
    Get the full commit hash from a short hash.
    
    Args:
        short_hash: Short commit hash (7+ characters)
        
    Returns:
        Full commit hash (40 characters)
        
    Raises:
        RuntimeError: If commit not found
    """
    _, stdout, _ = run_command(
        ["git", "rev-parse", short_hash],
        cwd=str(config.REPO_ROOT),
        capture_output=True,
    )
    return stdout.strip()


def create_worktree(commit: str, worktree_path: Optional[Path] = None) -> Path:
    """
    Create a git worktree for a specific commit.
    
    This is used to pull exact dataset versions without disturbing
    the current working branch.
    
    Args:
        commit: Git commit hash to create worktree for
        worktree_path: Optional custom path for worktree (default: .worktrees/<commit>)
        
    Returns:
        Path to the created worktree
        
    Raises:
        RuntimeError: If worktree creation fails
    """
    # Extract short hash from commit (handle both "git:<hash>" and raw hash)
    if commit.startswith("git:"):
        commit_hash = commit[4:]
    else:
        commit_hash = commit
    
    # Default worktree path
    if worktree_path is None:
        worktree_path = config.REPO_ROOT / ".worktrees" / commit_hash
    
    # Create worktrees directory if it doesn't exist
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if worktree already exists
    if worktree_path.exists():
        print_info(f"Worktree already exists at: {worktree_path}")
        return worktree_path
    
    # Get full commit hash
    full_commit = get_full_commit(commit_hash)
    
    # Create worktree
    print_info(f"Creating worktree for commit {commit_hash}...")
    run_command(
        ["git", "worktree", "add", str(worktree_path), full_commit],
        cwd=str(config.REPO_ROOT),
    )
    
    print_success(f"Created worktree at: {worktree_path}")
    return worktree_path


def remove_worktree(worktree_path: Path) -> None:
    """
    Remove a git worktree.
    
    Args:
        worktree_path: Path to worktree to remove
        
    Raises:
        RuntimeError: If worktree removal fails
    """
    if not worktree_path.exists():
        print_info(f"Worktree does not exist: {worktree_path}")
        return
    
    print_info(f"Removing worktree: {worktree_path}...")
    run_command(
        ["git", "worktree", "remove", str(worktree_path)],
        cwd=str(config.REPO_ROOT),
    )
    print_success(f"Removed worktree: {worktree_path}")


def commit_changes(message: str, files: Optional[list] = None) -> str:
    """
    Commit changes to Git.
    
    Args:
        message: Commit message
        files: Optional list of files to add (default: add all)
        
    Returns:
        New commit hash
        
    Raises:
        RuntimeError: If commit fails
    """
    # Add files
    if files:
        for file in files:
            run_command(
                ["git", "add", file],
                cwd=str(config.REPO_ROOT),
            )
    else:
        run_command(
            ["git", "add", "-A"],
            cwd=str(config.REPO_ROOT),
        )
    
    # Commit
    run_command(
        ["git", "commit", "-m", message],
        cwd=str(config.REPO_ROOT),
    )
    
    # Get new commit hash
    return get_current_commit()
