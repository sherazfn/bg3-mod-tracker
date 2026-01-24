#!/usr/bin/env python3
"""Task runner for local development and builds.

Usage:
    python task.py <command> [options]

Commands:
    test           Run all tests
    test-unit      Run unit tests only
    test-integration  Run integration tests only
    build          Run full build (update_history + generate_html)
    update-db      Update database from git history
    generate-html  Generate HTML from database
    clean          Clean temporary files (mods.db)
    install        Install dependencies
    help           Show this help message
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, cwd=cwd)
    return result.returncode


def install_dependencies():
    """Install project dependencies."""
    print("=== Installing Dependencies ===")
    
    # Install git-history (required for builds)
    print("\nInstalling git-history...")
    run_command([sys.executable, "-m", "pip", "install", "git-history"])
    
    # Install test dependencies
    test_reqs = Path("requirements-test.txt")
    if test_reqs.exists():
        print("\nInstalling test dependencies...")
        run_command([sys.executable, "-m", "pip", "install", "-r", str(test_reqs)])
    
    print("\n[PASS] Dependencies installed")


def run_tests(unit_only=False, integration_only=False, verbose=False, coverage=False):
    """Run tests."""
    print("=== Running Tests ===")
    
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # Always verbose for clarity
    
    if coverage:
        cmd.extend(["--cov=scripts", "--cov-report=html"])
    
    if unit_only:
        cmd.append("tests/test_mod_scenarios.py")
        cmd.append("tests/test_workflow_logic.py")
    elif integration_only:
        cmd.append("tests/test_integration_pipeline.py")
    else:
        cmd.append("tests/")
    
    exit_code = run_command(cmd, check=False)
    
    if exit_code == 0:
        print("\n[PASS] All tests passed")
    else:
        print("\n[FAIL] Some tests failed")
        sys.exit(exit_code)


def update_database():
    """Update database from git history."""
    print("=== Updating Database ===")
    print("What we're doing: Running update_history.py to generate mods.db from git history")
    
    try:
        from scripts.update_history import update_history
        update_history()
        print("\n[PASS] Database updated successfully")
    except SystemExit as e:
        print(f"\n[FAIL] Database update failed with exit code {e.code}")
        sys.exit(e.code)
    except Exception as e:
        print(f"\n[FAIL] Database update failed: {e}")
        sys.exit(1)


def generate_html_output():
    """Generate HTML from database."""
    print("=== Generating HTML ===")
    print("What we're doing: Running generate_html.py to create index.html")
    
    db_path = Path("mods.db")
    if not db_path.exists():
        print("[WARN] mods.db not found. Run 'python task.py update-db' first.")
        sys.exit(1)
    
    try:
        from scripts.generate_html import generate_html
        mod_count = generate_html()
        print(f"\n[PASS] Generated index.html with {mod_count} mod(s)")
    except Exception as e:
        print(f"\n[FAIL] HTML generation failed: {e}")
        sys.exit(1)


def build():
    """Run full build pipeline."""
    print("=== Running Full Build ===")
    print("What we're doing: Update database -> Generate HTML")
    
    # Step 1: Update database
    print("\n--- Step 1: Updating Database ---")
    update_database()
    
    # Step 2: Generate HTML
    print("\n--- Step 2: Generating HTML ---")
    generate_html_output()
    
    print("\n[PASS] Build completed successfully")


def clean():
    """Clean temporary files."""
    print("=== Cleaning Temporary Files ===")
    
    files_to_remove = [
        "mods.db",
        ".pytest_cache",
        "htmlcov",
        "__pycache__",
    ]
    
    removed = []
    for file_pattern in files_to_remove:
        path = Path(file_pattern)
        if path.exists():
            if path.is_file():
                path.unlink()
                removed.append(file_pattern)
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
                removed.append(file_pattern)
    
    if removed:
        print(f"Removed: {', '.join(removed)}")
    else:
        print("No temporary files to clean")
    
    print("[PASS] Cleanup completed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Task runner for local development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "command",
        choices=["test", "test-unit", "test-integration", "build", "update-db", 
                 "generate-html", "clean", "install", "help"],
        help="Command to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    
    args = parser.parse_args()
    
    if args.command == "help":
        parser.print_help()
        return
    
    # Change to project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    # Execute command
    if args.command == "install":
        install_dependencies()
    elif args.command == "test":
        run_tests(verbose=args.verbose, coverage=args.coverage)
    elif args.command == "test-unit":
        run_tests(unit_only=True, verbose=args.verbose, coverage=args.coverage)
    elif args.command == "test-integration":
        run_tests(integration_only=True, verbose=args.verbose)
    elif args.command == "update-db":
        update_database()
    elif args.command == "generate-html":
        generate_html_output()
    elif args.command == "build":
        build()
    elif args.command == "clean":
        clean()


if __name__ == "__main__":
    main()
