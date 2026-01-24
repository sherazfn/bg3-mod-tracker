"""Comprehensive test suite for mod changelog scenarios."""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import pytest
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from changelog_data import (
    get_mods,
    get_platform_version,
    parse_logo_url,
    parse_timestamp,
    Mod,
    ModUpdate,
)


class TestModScenarios:
    """Test suite for various mod update scenarios."""

    def test_new_mod_scenario(self, temp_dir, sample_mod_base):
        """Test: New mod appears for the first time (should create 'added' event)."""
        print("\n=== Testing: New Mod Scenario ===")
        print("What we're testing: Mod appears for the first time in version 1")
        print("Expected: Creates 'added' event with version 1")
        
        mod = sample_mod_base.copy()
        mod["platforms"] = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        mod["modfile"]["platforms"] = mod["platforms"].copy()
        
        # Create data.json
        data_file = temp_dir / "data.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump([mod], f)
        
        # Simulate git-history processing by creating DB entry manually
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create table structure similar to git-history
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        # Insert version 1 (new mod)
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mod["id"],
            1,
            datetime.now(timezone.utc).isoformat(),
            mod["name"],
            mod["summary"],
            mod["profile_url"],
            json.dumps(mod["logo"]) if mod["logo"] else None,
            json.dumps(mod["platforms"])
        ))
        
        conn.commit()
        conn.close()
        
        # Test the get_mods function
        mods = get_mods(str(db_file))
        
        print(f"Got: Found {len(mods)} mod(s) in database")
        
        assert mod["id"] in mods, f"Expected mod ID {mod['id']} to be in database, but it wasn't found"
        mod_obj = mods[mod["id"]]
        print(f"Got: Mod name = '{mod_obj.name}'")
        assert mod_obj.name == mod["name"], f"Expected mod name '{mod['name']}', got '{mod_obj.name}'"
        
        print(f"Got: {len(mod_obj.updates)} update event(s)")
        assert len(mod_obj.updates) == 1, f"Expected 1 update event, got {len(mod_obj.updates)}"
        
        print(f"Got: Update type = '{mod_obj.updates[0].update_type}'")
        assert mod_obj.updates[0].update_type == "added", f"Expected 'added' event, got '{mod_obj.updates[0].update_type}'"
        
        print(f"Got: Update version = {mod_obj.updates[0].version}")
        assert mod_obj.updates[0].version == 1, f"Expected version 1, got {mod_obj.updates[0].version}"
        
        print("[PASS] Test passed: New mod correctly creates 'added' event")

    def test_console_version_bump_scenario(self, temp_dir, sample_mod_base):
        """Test: PS5 version increases (should create 'updated' event)."""
        print("\n=== Testing: Console Version Bump Scenario ===")
        print("What we're testing: PS5 version increases from 1 to 2")
        print("Expected: Creates 'added' event (v1) and 'updated' event (v2)")
        
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: PS5 version 1
        platforms_v1 = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: PS5 version 2 (bump!)
        platforms_v2 = [{"platform": "ps5", "status": 1, "modfile_live": 2}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v2)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        print(f"Got: {len(mod_obj.updates)} update event(s)")
        assert len(mod_obj.updates) == 2, f"Expected 2 update events (added + updated), got {len(mod_obj.updates)}"
        
        print(f"Got: Event 1 type = '{mod_obj.updates[0].update_type}', version = {mod_obj.updates[0].version}")
        assert mod_obj.updates[0].update_type == "added", f"Expected first event to be 'added', got '{mod_obj.updates[0].update_type}'"
        
        print(f"Got: Event 2 type = '{mod_obj.updates[1].update_type}', version = {mod_obj.updates[1].version}")
        assert mod_obj.updates[1].update_type == "updated", f"Expected second event to be 'updated', got '{mod_obj.updates[1].update_type}'"
        assert mod_obj.updates[1].version == 2, f"Expected updated event at version 2, got version {mod_obj.updates[1].version}"
        
        print("[PASS] Test passed: PS5 version bump correctly creates 'updated' event")

    def test_description_only_change_scenario(self, temp_dir, sample_mod_base):
        """Test: Only description changes, no version bump (should NOT create 'updated' event)."""
        print("\n=== Testing: Description Only Change Scenario ===")
        print("What we're testing: Summary changes but PS5 version stays at 1")
        print("Expected: NO 'updated' event (only metadata updates), summary should update")
        
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: PS5 version 1
        platforms = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Original summary", "https://mod.io/m/test", None, json.dumps(platforms)))
        
        # Version 2: Same PS5 version, but summary changed
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Updated summary", "https://mod.io/m/test", None, json.dumps(platforms)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        print(f"Got: {len(mod_obj.updates)} update event(s)")
        # Should only have "added" event, no "updated" event
        assert len(mod_obj.updates) == 1, f"Expected 1 update event (only 'added'), got {len(mod_obj.updates)}"
        
        print(f"Got: Event type = '{mod_obj.updates[0].update_type}'")
        assert mod_obj.updates[0].update_type == "added", f"Expected only 'added' event, got '{mod_obj.updates[0].update_type}'"
        
        print(f"Got: Summary = '{mod_obj.summary}'")
        assert mod_obj.summary == "Updated summary", f"Expected summary to update to 'Updated summary', got '{mod_obj.summary}'"
        
        print("[PASS] Test passed: Description-only change does NOT create 'updated' event")

    def test_pc_version_only_change_scenario(self, temp_dir, sample_mod_base):
        """Test: Only PC/Windows version changes, PS5 unchanged (should NOT create 'updated' event)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: PS5 version 1, Windows version 1
        platforms_v1 = [
            {"platform": "ps5", "status": 1, "modfile_live": 1},
            {"platform": "windows", "status": 1, "modfile_live": 1}
        ]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: PS5 version still 1, Windows version 2 (bump!)
        platforms_v2 = [
            {"platform": "ps5", "status": 1, "modfile_live": 1},
            {"platform": "windows", "status": 1, "modfile_live": 2}
        ]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v2)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        # Should only have "added" event, no "updated" event (PS5 version didn't change)
        assert len(mod_obj.updates) == 1
        assert mod_obj.updates[0].update_type == "added"

    def test_multiple_console_updates_scenario(self, temp_dir, sample_mod_base):
        """Test: Multiple PS5 version bumps (should create multiple 'updated' events)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: PS5 version 1
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, 
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 1}])))
        
        # Version 2: PS5 version 2
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Summary", "https://mod.io/m/test", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 2}])))
        
        # Version 3: PS5 version 3
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 3, now, "Test Mod", "Summary", "https://mod.io/m/test", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 3}])))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        assert len(mod_obj.updates) == 3
        assert mod_obj.updates[0].update_type == "added"
        assert mod_obj.updates[1].update_type == "updated"
        assert mod_obj.updates[2].update_type == "updated"
        assert mod_obj.updates[1].version == 2
        assert mod_obj.updates[2].version == 3

    def test_name_change_only_scenario(self, temp_dir, sample_mod_base):
        """Test: Only name changes, no version bump (should NOT create 'updated' event)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        platforms = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        
        # Version 1
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Original Name", "Summary", "https://mod.io/m/test", None, json.dumps(platforms)))
        
        # Version 2: Name changed, but PS5 version same
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "New Name", "Summary", "https://mod.io/m/test", None, json.dumps(platforms)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        assert len(mod_obj.updates) == 1  # Only "added"
        assert mod_obj.name == "New Name"  # Name should update

    def test_platform_version_parsing(self):
        """Test: Platform version parsing helper function."""
        platforms_json = json.dumps([
            {"platform": "ps5", "status": 1, "modfile_live": 5},
            {"platform": "windows", "status": 1, "modfile_live": 3}
        ])
        
        assert get_platform_version(platforms_json, "ps5") == 5
        assert get_platform_version(platforms_json, "windows") == 3
        assert get_platform_version(platforms_json, "xboxseriesx") == 0
        assert get_platform_version(None, "ps5") == 0
        assert get_platform_version("invalid json", "ps5") == 0

    def test_mixed_platform_updates(self, temp_dir, sample_mod_base):
        """Test: PS5 and Windows versions both change, but only PS5 matters."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: PS5=1, Windows=1
        platforms_v1 = [
            {"platform": "ps5", "status": 1, "modfile_live": 1},
            {"platform": "windows", "status": 1, "modfile_live": 1}
        ]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: PS5=2, Windows=2 (both bump, but only PS5 matters)
        platforms_v2 = [
            {"platform": "ps5", "status": 1, "modfile_live": 2},
            {"platform": "windows", "status": 1, "modfile_live": 2}
        ]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v2)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        # Should have "added" and "updated" because PS5 version bumped
        assert len(mod_obj.updates) == 2
        assert mod_obj.updates[1].update_type == "updated"

    def test_no_ps5_platform_scenario(self, temp_dir, sample_mod_base):
        """Test: Mod with no PS5 platform (should still create 'added' but no 'updated' on changes)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: Only Windows platform
        platforms_v1 = [{"platform": "windows", "status": 1, "modfile_live": 1}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: Windows version bumps
        platforms_v2 = [{"platform": "windows", "status": 1, "modfile_live": 2}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v2)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        # Should only have "added" (no PS5 platform, so no updates tracked)
        assert len(mod_obj.updates) == 1
        assert mod_obj.updates[0].update_type == "added"

    def test_version_decrease_scenario(self, temp_dir, sample_mod_base):
        """Test: PS5 version decreases (should NOT create 'updated' event - only increases matter)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: PS5 version 3
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 3}])))
        
        # Version 2: PS5 version 2 (decreased!)
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "Test Mod", "Summary", "https://mod.io/m/test", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 2}])))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        # Should only have "added" (version decreased, not increased)
        assert len(mod_obj.updates) == 1
        assert mod_obj.updates[0].update_type == "added"

    def test_ps5_version_same_other_changes(self, temp_dir, sample_mod_base):
        """Test: PS5 version stays same, but other fields change (should NOT create 'updated' event)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        platforms = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        
        # Version 1
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms)))
        
        # Version 2: Everything changed except PS5 version
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 2, now, "New Name", "New Summary", "https://mod.io/m/new", 
              json.dumps({"thumb_320x180": "https://example.com/logo.png"}), json.dumps(platforms)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        # Should only have "added" (PS5 version didn't increase)
        assert len(mod_obj.updates) == 1
        assert mod_obj.updates[0].update_type == "added"
        # But metadata should update
        assert mod_obj.name == "New Name"
        assert mod_obj.summary == "New Summary"

    def test_multiple_mods_scenario(self, temp_dir, sample_mod_base):
        """Test: Multiple mods with different update patterns."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Mod 1: New mod (version 1)
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 1, now, "Mod 1", "Summary", "https://mod.io/m/1", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 1}])))
        
        # Mod 2: New mod (version 1)
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 1, now, "Mod 2", "Summary", "https://mod.io/m/2", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 1}])))
        
        # Mod 1: Version 2 (PS5 version bump)
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 2, now, "Mod 1", "Summary", "https://mod.io/m/1", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 2}])))
        
        # Mod 2: Version 2 (no PS5 version bump)
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 2, now, "Mod 2 Updated", "New Summary", "https://mod.io/m/2", None,
              json.dumps([{"platform": "ps5", "status": 1, "modfile_live": 1}])))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        
        assert len(mods) == 2
        
        # Mod 1 should have "added" and "updated"
        assert len(mods[1].updates) == 2
        assert mods[1].updates[0].update_type == "added"
        assert mods[1].updates[1].update_type == "updated"
        
        # Mod 2 should only have "added"
        assert len(mods[2].updates) == 1
        assert mods[2].updates[0].update_type == "added"
        assert mods[2].name == "Mod 2 Updated"  # Name should update

    def test_mod_removed_scenario(self, temp_dir, sample_mod_base):
        """Test: Mod appears then is removed from data.json (should still exist in DB with last version)."""
        print("\n=== Testing: Mod Removed Scenario ===")
        print("What we're testing: Mod appears in version 1, then is removed (no version 2 entry)")
        print("Expected: Mod still exists in DB with last known state (version 1), only 'added' event")
        
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: Mod appears
        platforms_v1 = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: Mod removed (not in data.json anymore)
        # In git-history, removed items don't create new rows - they just stop appearing
        # So we simulate this by NOT inserting a version 2 for this mod
        # But we insert version 2 for a different mod to show version progression
        other_mod_id = mod_id + 1
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (other_mod_id, 1, now, "Other Mod", "Summary", "https://mod.io/m/other", None, json.dumps(platforms_v1)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        
        print(f"Got: Found {len(mods)} mod(s) in database")
        
        # Removed mod should still exist in database with its last known state
        assert mod_id in mods, f"Expected removed mod ID {mod_id} to still exist in database"
        mod_obj = mods[mod_id]
        
        print(f"Got: {len(mod_obj.updates)} update event(s) for removed mod")
        assert len(mod_obj.updates) == 1, f"Expected 1 update event (only 'added'), got {len(mod_obj.updates)}"
        
        print(f"Got: Event type = '{mod_obj.updates[0].update_type}'")
        assert mod_obj.updates[0].update_type == "added", f"Expected 'added' event, got '{mod_obj.updates[0].update_type}'"
        
        print(f"Got: Mod name = '{mod_obj.name}'")
        assert mod_obj.name == "Test Mod", f"Expected last known name 'Test Mod', got '{mod_obj.name}'"
        
        print("[PASS] Test passed: Removed mod still exists in DB with last known state")

    def test_mod_reappears_scenario(self, temp_dir, sample_mod_base):
        """Test: Mod removed then reappears (should continue tracking or create new entry)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        platforms_v1 = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        
        # Version 1: Mod appears
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Test Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: Mod removed (no entry for this mod)
        # Version 3: Mod reappears (git-history would create version 3, not version 2)
        platforms_v3 = [{"platform": "ps5", "status": 1, "modfile_live": 2}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 3, now, "Test Mod Reappeared", "New Summary", "https://mod.io/m/test", None, json.dumps(platforms_v3)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        mod_obj = mods[mod_id]
        
        # Mod should have "added" and "updated" (version 3 has PS5 version bump)
        assert len(mod_obj.updates) == 2
        assert mod_obj.updates[0].update_type == "added"
        assert mod_obj.updates[1].update_type == "updated"
        assert mod_obj.updates[1].version == 3
        assert mod_obj.name == "Test Mod Reappeared"  # Updated name

    def test_mod_removed_with_other_mods(self, temp_dir, sample_mod_base):
        """Test: One mod removed while others continue (verify other mods unaffected)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        now = datetime.now(timezone.utc).isoformat()
        platforms_v1 = [{"platform": "ps5", "status": 1, "modfile_live": 1}]
        
        # Mod 1: Version 1
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 1, now, "Mod 1", "Summary", "https://mod.io/m/1", None, json.dumps(platforms_v1)))
        
        # Mod 2: Version 1
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 1, now, "Mod 2", "Summary", "https://mod.io/m/2", None, json.dumps(platforms_v1)))
        
        # Version 2: Mod 1 removed, Mod 2 continues with version bump
        platforms_v2 = [{"platform": "ps5", "status": 1, "modfile_live": 2}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 2, now, "Mod 2", "Summary", "https://mod.io/m/2", None, json.dumps(platforms_v2)))
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        
        # Mod 1 should still exist (removed but in DB)
        assert 1 in mods
        assert len(mods[1].updates) == 1
        assert mods[1].updates[0].update_type == "added"
        
        # Mod 2 should have "added" and "updated" (version bumped)
        assert 2 in mods
        assert len(mods[2].updates) == 2
        assert mods[2].updates[0].update_type == "added"
        assert mods[2].updates[1].update_type == "updated"

    def test_mod_removed_no_ps5_platform(self, temp_dir, sample_mod_base):
        """Test: Mod without PS5 platform is removed (should still be tracked)."""
        db_file = temp_dir / "mods.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE item_version_detail (
                _item INTEGER,
                _version INTEGER,
                _commit_at TEXT,
                name TEXT,
                summary TEXT,
                profile_url TEXT,
                logo TEXT,
                platforms TEXT
            )
        """)
        
        mod_id = sample_mod_base["id"]
        now = datetime.now(timezone.utc).isoformat()
        
        # Version 1: Mod with Windows only (no PS5)
        platforms_v1 = [{"platform": "windows", "status": 1, "modfile_live": 1}]
        cursor.execute("""
            INSERT INTO item_version_detail 
            (_item, _version, _commit_at, name, summary, profile_url, logo, platforms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mod_id, 1, now, "Windows Only Mod", "Summary", "https://mod.io/m/test", None, json.dumps(platforms_v1)))
        
        # Version 2: Mod removed (no entry)
        
        conn.commit()
        conn.close()
        
        mods = get_mods(str(db_file))
        
        # Mod should still exist in database
        assert mod_id in mods
        mod_obj = mods[mod_id]
        assert len(mod_obj.updates) == 1  # Only "added"
        assert mod_obj.updates[0].update_type == "added"
        assert mod_obj.name == "Windows Only Mod"
