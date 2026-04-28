import sqlite3
import os
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "mods.db")


@dataclass
class ModUpdate:
    """Represents a single update event for a mod."""

    timestamp: datetime
    update_type: str  # 'added' or 'updated'
    version: int


@dataclass
class Mod:
    """Represents a mod with its metadata and update history."""

    item_id: int
    name: str
    summary: Optional[str] = None
    profile_url: Optional[str] = None
    logo_url: Optional[str] = None
    updates: list[ModUpdate] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)


def parse_logo_url(logo_json: Optional[str]) -> Optional[str]:
    """Extract thumbnail URL from logo JSON."""
    if not logo_json:
        return None
    try:
        logo = json.loads(logo_json)
        return logo.get("thumb_320x180") or logo.get("original")
    except (json.JSONDecodeError, TypeError):
        return None


def parse_timestamp(commit_at: Optional[str]) -> datetime:
    """Parse ISO timestamp string to datetime."""
    if not commit_at:
        return datetime.now(timezone.utc)
    try:
        # Handle ISO format with timezone
        return datetime.fromisoformat(commit_at.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def get_platform_version(
    platforms_json: Optional[str], platform_name: str = "ps5"
) -> int:
    """Extract the modfile_live version for a specific platform."""
    if not platforms_json:
        return 0
    try:
        platforms = json.loads(platforms_json)
        for platform in platforms:
            if platform.get("platform") == platform_name:
                return platform.get("modfile_live", 0) or 0
    except (json.JSONDecodeError, TypeError):
        return 0
    return 0


def get_all_platform_versions(platforms_json: Optional[str]) -> dict[str, int]:
    """Extract {platform_name: modfile_live} for every platform present."""
    if not platforms_json:
        return {}
    try:
        platforms = json.loads(platforms_json)
    except (json.JSONDecodeError, TypeError):
        return {}
    result: dict[str, int] = {}
    for platform in platforms:
        name = platform.get("platform")
        if name:
            result[name] = platform.get("modfile_live", 0) or 0
    return result


def has_any_version_bump(
    old_versions: dict[str, int], new_versions: dict[str, int]
) -> bool:
    """True if any platform's modfile_live increased between the two snapshots."""
    for name, new_ver in new_versions.items():
        if new_ver > old_versions.get(name, 0):
            return True
    return False


def get_mods(db_path: Optional[str] = None) -> dict[int, Mod]:
    """
    Fetch all mods with their update history from the database.

    Returns:
        Dictionary mapping item_id to Mod objects with their updates.
    """
    if db_path is None:
        db_path = DB_PATH

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Fetch all versions of all items, ordered by item and version
    query = """
    SELECT 
        _item,
        _version,
        _commit_at,
        name,
        summary,
        profile_url,
        logo,
        platforms
    FROM item_version_detail
    ORDER BY _item, _version
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    # Build mod dictionary with updates
    mods: dict[int, Mod] = {}
    # Track previous {platform_name: modfile_live} per item for version bump detection
    previous_versions: dict[int, dict[str, int]] = {}

    for row in rows:
        item_id = row["_item"]
        version = row["_version"]
        platforms_json = row["platforms"]
        current_versions = get_all_platform_versions(platforms_json)
        current_platform_names = sorted(current_versions.keys())

        if version == 1:
            # First version - this is when the mod was added
            mod = Mod(
                item_id=item_id,
                name=row["name"] or f"Mod #{item_id}",
                summary=row["summary"],
                profile_url=row["profile_url"],
                logo_url=parse_logo_url(row["logo"]),
                platforms=current_platform_names,
            )
            mod.updates.append(
                ModUpdate(
                    timestamp=parse_timestamp(row["_commit_at"]),
                    update_type="added",
                    version=version,
                )
            )
            mods[item_id] = mod
            previous_versions[item_id] = current_versions
        else:
            # Subsequent version - check if any platform's modfile_live increased
            mod = mods.get(item_id)
            if mod is None:
                # Orphan update without a version 1 - create the mod
                mod = Mod(
                    item_id=item_id,
                    name=row["name"] or f"Mod #{item_id}",
                    summary=row["summary"],
                    profile_url=row["profile_url"],
                    logo_url=parse_logo_url(row["logo"]),
                    platforms=current_platform_names,
                )
                mods[item_id] = mod

            # Update mod metadata if we have newer info
            if row["name"]:
                mod.name = row["name"]
            if row["summary"]:
                mod.summary = row["summary"]
            if row["profile_url"]:
                mod.profile_url = row["profile_url"]
            if row["logo"]:
                mod.logo_url = parse_logo_url(row["logo"])
            if current_platform_names:
                mod.platforms = current_platform_names

            # Update event if any platform's modfile_live increased
            old_versions = previous_versions.get(item_id, {})
            if has_any_version_bump(old_versions, current_versions):
                mod.updates.append(
                    ModUpdate(
                        timestamp=parse_timestamp(row["_commit_at"]),
                        update_type="updated",
                        version=version,
                    )
                )

            # Update tracked versions (keep the highest seen per platform)
            if current_versions:
                merged = dict(old_versions)
                for name, ver in current_versions.items():
                    merged[name] = max(merged.get(name, 0), ver)
                previous_versions[item_id] = merged

    return mods


if __name__ == "__main__":
    mods = get_mods()

    print(f"Found {len(mods)} mods\n")

    for mod_id, mod in list(mods.items())[:5]:
        print(f"Mod {mod_id}: {mod.name}")
        for update in mod.updates:
            print(f"  - {update.update_type} at {update.timestamp}")
        print()
