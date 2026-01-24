"""Pytest configuration and fixtures for testing mod changelog functionality."""

import json
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmpdir = tempfile.mkdtemp()
    try:
        yield Path(tmpdir)
    finally:
        # Ensure all files are closed before cleanup
        import gc
        gc.collect()
        
        # Try to remove, but ignore errors on Windows (file locks)
        import shutil
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except:
            pass


@pytest.fixture
def sample_mod_base():
    """Base mod data structure."""
    return {
        "id": 1000001,
        "game_id": 6715,
        "name": "Test Mod",
        "name_id": "test-mod",
        "summary": "A test mod",
        "description": "<p>Test description</p>",
        "date_added": 1737763200,
        "date_updated": 1737763200,
        "date_live": 1737763200,
        "visible": 1,
        "status": 1,
        "dependencies": False,
        "profile_url": "https://mod.io/g/baldursgate3/m/test-mod",
        "submitted_by": {
            "id": 12345,
            "name_id": "testuser",
            "username": "TestUser",
            "profile_url": "https://mod.io/u/testuser",
            "profile_img_100x100_url": "https://assets.modcdn.io/images/placeholder/avatar_100x100.png"
        },
        "modfile": {
            "id": 1000001,
            "mod_id": 1000001,
            "version": "1.0.0.0",
            "filename": "test_mod.zip",
            "changelog": "Initial release",
            "date_added": 1737763200,
            "date_updated": 0,
            "date_scanned": 1737763200,
            "filesize": 1000,
            "platforms": []
        },
        "logo": None,
        "tags": [],
        "platforms": []
    }


@pytest.fixture
def create_data_json(temp_dir, mods_data):
    """Create a data.json file with given mod data."""
    data_file = temp_dir / "data.json"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(mods_data, f, indent=2)
    return data_file


@pytest.fixture
def create_db(temp_dir):
    """Create an empty SQLite database."""
    db_file = temp_dir / "mods.db"
    conn = sqlite3.connect(db_file)
    conn.close()
    return db_file


def create_mod_with_platforms(base_mod, ps5_version=1, windows_version=0, xbox_version=0):
    """Helper to create a mod with specific platform versions."""
    mod = base_mod.copy()
    
    platforms = []
    if ps5_version > 0:
        platforms.append({
            "platform": "ps5",
            "status": 1,
            "modfile_live": ps5_version
        })
    if windows_version > 0:
        platforms.append({
            "platform": "windows",
            "status": 1,
            "modfile_live": windows_version
        })
    if xbox_version > 0:
        platforms.append({
            "platform": "xboxseriesx",
            "status": 1,
            "modfile_live": xbox_version
        })
    
    mod["platforms"] = platforms
    mod["modfile"]["platforms"] = platforms.copy()
    
    return mod
