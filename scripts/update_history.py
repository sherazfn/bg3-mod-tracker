"""Update the mods database from git history."""

import subprocess


def update_history(db_path: str = "mods.db", data_path: str = "data.json") -> None:
    """
    Update the mods database using git-history.

    Args:
        db_path: Path to the SQLite database
        data_path: Path to the JSON data file
    """
    import re
    import sys

    # Regex to catch the specific error from git-history
    # Example: Error: Commit: 00fe965ed11d5b8db5bc621ba929d1d6e09ceff0 - found multiple items with the same ID:
    error_pattern = re.compile(r"Error: Commit: ([0-9a-f]+) - found multiple items with the same ID")

    full_command = ["git-history", "file", db_path, data_path, "--id", "id", "--ignore-duplicate-ids"]
    
    print(f"Running command: {' '.join(full_command)}")
    
    # Run process and capture output
    result = subprocess.run(
        full_command,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        print("Successfully updated mods.db")
        return

    # Print output even on failure so we can see what happened
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    print("Command failed with an error.")
    sys.exit(result.returncode)


def main():
    """CLI entry point."""
    update_history()
    print("Updated mods.db from git history")


if __name__ == "__main__":
    main()
