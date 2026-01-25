"""
Shell utilities for subprocess execution

Provides helper functions to run shell commands with nice formatting
and friendly error messages.

Author: MLOps Team
Date: January 2026
"""

import subprocess
import sys
import os
from typing import List, Optional, Tuple
from rich.console import Console

console = Console()


def run_command(
    cmd: List[str],
    cwd: Optional[str] = None,
    capture_output: bool = False,
    check: bool = True,
    env: Optional[dict] = None,
) -> Tuple[int, str, str]:
    """
    Run a shell command with nice formatting and error handling.
    
    Args:
        cmd: Command and arguments as list
        cwd: Working directory for command execution
        capture_output: If True, capture stdout/stderr instead of printing
        check: If True, raise exception on non-zero exit code
        env: Optional environment variables to pass to command
        
    Returns:
        Tuple of (returncode, stdout, stderr)
        
    Raises:
        RuntimeError: If command fails and check=True
    """
    console.print(f"[cyan]Running:[/cyan] {' '.join(cmd)}")
    
    # On Windows, use shell=True to properly resolve .cmd and .bat files
    use_shell = sys.platform == "win32"
    
    # Merge environment variables
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                env=process_env,
                shell=use_shell,
            )
            
            if check and result.returncode != 0:
                console.print(f"[red]Command failed with exit code {result.returncode}[/red]")
                if result.stdout:
                    process_env,
                shell=use_shellsole.print(f"[yellow]STDOUT:[/yellow]\n{result.stdout}")
                if result.stderr:
                    console.print(f"[red]STDERR:[/red]\n{result.stderr}")
                raise RuntimeError(f"Command failed: {' '.join(cmd)}")
            
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
            )
            
            if check and result.returncode != 0:
                console.print(f"[red]Command failed with exit code {result.returncode}[/red]")
                raise RuntimeError(f"Command failed: {' '.join(cmd)}")
            
            return result.returncode, "", ""
            
    except FileNotFoundError as e:
        # Handle case where command is not found
        cmd_name = cmd[0]
        
        if cmd_name in ["az", "az.cmd"]:
            error_msg = (
                f"Azure CLI not found. Please install it:\n"
                f"  1. Download from: https://aka.ms/installazurecliwindows\n"
                f"  2. Install and restart your terminal/IDE\n"
                f"  3. Verify with: az --version"
            )
        elif cmd_name in ["git", "git.exe"]:
            error_msg = (
                f"Git not found. Please install it:\n"
                f"  1. Download from: https://git-scm.com/download/win\n"
                f"  2. Install and restart your terminal/IDE\n"
                f"  3. Verify with: git --version"
            )
        elif cmd_name in ["dvc", "dvc.exe"]:
            error_msg = (
                f"DVC not found. Please ensure your conda environment is activated:\n"
                f"  conda activate mlops-lineage"
            )
        else:
            error_msg = f"Command '{cmd_name}' not found. Please ensure it is installed and in your PATH."
        
        console.print(f"[red]{error_msg}[/red]")
        raise RuntimeError(error_msg) from e


def check_command_exists(cmd: str) -> bool:
    """
    Check if a command exists in PATH.
    
    Args:
        cmd: Command name to check
        
    Returns:
        True if command exists, False otherwise
    """
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["where", cmd],
                capture_output=True,
                check=True,
            )
        else:
            subprocess.run(
                ["which", cmd],
                capture_output=True,
                check=True,
            )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[red]✗[/red] {message}")
