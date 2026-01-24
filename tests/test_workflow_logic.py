"""Test suite for workflow change detection logic."""

import json
import tempfile
from pathlib import Path
import subprocess
import pytest


class TestWorkflowChangeDetection:
    """Test workflow change detection logic."""

    def test_no_changes_detected(self, temp_dir):
        """Test: No changes in data.json should be detected correctly."""
        print("\n=== Testing: No Changes Detected ===")
        print("What we're testing: Git detects when data.json hasn't changed")
        print("Expected: git diff --staged --quiet returns 0 (no changes)")
        
        data_file = temp_dir / "data.json"
        
        # Create initial data
        initial_data = [{"id": 1, "name": "Test Mod"}]
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "data.json"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Stage the same file again (no changes)
        subprocess.run(["git", "add", "data.json"], cwd=temp_dir, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            cwd=temp_dir,
            capture_output=True
        )
        
        print(f"Got: git diff exit code = {result.returncode}")
        assert result.returncode == 0, f"Expected exit code 0 (no changes), got {result.returncode}"
        print("[PASS] Test passed: No changes correctly detected")

    def test_changes_detected(self, temp_dir):
        """Test: Changes in data.json should be detected correctly."""
        print("\n=== Testing: Changes Detected ===")
        print("What we're testing: Git detects when data.json has changed")
        print("Expected: git diff --staged --quiet returns non-zero (changes detected)")
        
        data_file = temp_dir / "data.json"
        
        # Create initial data
        initial_data = [{"id": 1, "name": "Test Mod"}]
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "data.json"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Modify data
        modified_data = [{"id": 1, "name": "Test Mod Updated"}, {"id": 2, "name": "New Mod"}]
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(modified_data, f)
        
        print(f"Modified: Changed mod name and added new mod (total: {len(modified_data)} mods)")
        
        # Stage changes
        subprocess.run(["git", "add", "data.json"], cwd=temp_dir, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            cwd=temp_dir,
            capture_output=True
        )
        
        print(f"Got: git diff exit code = {result.returncode}")
        assert result.returncode != 0, f"Expected non-zero exit code (changes detected), got {result.returncode}"
        print("[PASS] Test passed: Changes correctly detected")

    def test_combined_files_staging(self, temp_dir):
        """Test: Staging both data.json and index.html together."""
        print("\n=== Testing: Combined Files Staging ===")
        print("What we're testing: Both data.json and index.html can be staged together")
        print("Expected: Both files appear in staged files list")
        
        data_file = temp_dir / "data.json"
        html_file = temp_dir / "index.html"
        
        # Create files
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump([{"id": 1}], f)
        html_file.write_text("<html></html>")
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        
        # Stage both files
        subprocess.run(["git", "add", "data.json", "index.html"], cwd=temp_dir, check=True, capture_output=True)
        
        # Check staged files
        result = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        staged_files = result.stdout.strip().split("\n")
        print(f"Got: Staged files = {staged_files}")
        
        assert "data.json" in staged_files, f"Expected 'data.json' in staged files, got {staged_files}"
        assert "index.html" in staged_files, f"Expected 'index.html' in staged files, got {staged_files}"
        print("[PASS] Test passed: Both files correctly staged together")
