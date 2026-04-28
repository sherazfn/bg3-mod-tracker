"""Generate HTML for mod changelog display."""

from datetime import datetime, date, timezone
from collections import defaultdict

from .components import (
    html_document,
    page_layout,
    date_nav,
    date_section,
    mod_card,
    empty_state,
    tabs_script,
)
from .changelog_data import get_mods, Mod, ModUpdate


def format_date_delta(dt: datetime) -> str:
    """Format the relative day description (Today, Yesterday, X days ago)."""
    now = datetime.now(timezone.utc)
    today = now.date()
    dt_date = dt.date()

    diff_days = (today - dt_date).days

    if diff_days == 0:
        return "Today"
    elif diff_days == 1:
        return "Yesterday"
    elif diff_days < 7:
        return f"{diff_days} days ago"
    elif diff_days < 14:
        return "1 week ago"
    elif diff_days < 30:
        weeks = diff_days // 7
        return f"{weeks} weeks ago"
    else:
        months = diff_days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"


def format_timestamp(dt: datetime) -> str:
    """Format timestamp for display on cards."""
    return dt.strftime("%b %d, %Y")


def flatten_updates(mods: dict[str, Mod]) -> list[tuple[Mod, ModUpdate]]:
    """Flatten mods and their updates into a list of (mod, update) tuples."""
    result = []
    for mod in mods.values():
        for update in mod.updates:
            result.append((mod, update))
    return result


def generate_mod_cards(updates: list[tuple[Mod, ModUpdate]]) -> str:
    """Generate mod cards for a list of updates."""
    if not updates:
        return empty_state("No mods in this category")

    cards = []
    for mod, update in updates:
        cards.append(
            mod_card(
                title=mod.name,
                summary=mod.summary or "",
                image_url=mod.logo_url,
                profile_url=mod.profile_url,
                platforms=mod.platforms,
                author=mod.author,
                date_updated=mod.date_updated,
                popularity_rank=mod.popularity_rank,
                downloads_today=mod.downloads_today,
                subscribers=mod.subscribers,
            )
        )

    return "\n".join(cards)


def generate_changelog_content(mods: dict[str, Mod]) -> str:
    """Generate the HTML content from the mod data."""
    if not mods:
        return "<p>No mods found.</p>"

    # Cutoff date: Before December 1st, 2025 is "Started Tracking" (excluded)
    tracking_cutoff = date(2025, 11, 30)

    # Flatten to (mod, update) pairs
    updates = flatten_updates(mods)

    # Group all updates by date first
    by_date: dict[date, dict[str, list[tuple[Mod, ModUpdate]]]] = {}

    for mod, update in updates:
        update_date = update.timestamp.date()
        # Skip historical data before tracking started
        if update_date <= tracking_cutoff:
            continue

        if update_date not in by_date:
            by_date[update_date] = {"added": [], "updated": []}

        if update.update_type == "added":
            by_date[update_date]["added"].append((mod, update))
        else:
            by_date[update_date]["updated"].append((mod, update))

    if not by_date:
        return empty_state("No mods found"), ""

    # Sort dates descending
    sorted_dates = sorted(by_date.keys(), reverse=True)

    # Generate content
    entries = []

    # Date sections (date nav is handled separately)
    for i, day in enumerate(sorted_dates):
        day_data = by_date[day]
        formatted_date = day.strftime("%B %d, %Y")

        new_mods = day_data["added"]
        updated_mods = day_data["updated"]

        new_content = (
            generate_mod_cards(new_mods) if new_mods else empty_state("No new mods")
        )
        updated_content = (
            generate_mod_cards(updated_mods)
            if updated_mods
            else empty_state("No updates")
        )

        entries.append(
            date_section(
                date_str=formatted_date,
                new_count=len(new_mods),
                updated_count=len(updated_mods),
                content_new=new_content,
                content_updated=updated_content,
                is_first=(i == 0),
            )
        )

    # Add the script
    entries.append(tabs_script())

    return "\n".join(entries), date_nav()


def generate_html(
    db_path: str = "mods.db",
    output_path: str = "index.html",
    hero_image: str = "assets/img/logo.png",
) -> int:
    """
    Generate the HTML file.

    Args:
        db_path: Path to the SQLite database
        output_path: Path for the output HTML file
        hero_image: Path to the hero image

    Returns:
        Number of mods generated
    """
    mods = get_mods(db_path)
    content, nav = generate_changelog_content(mods)
    layout = page_layout(
        title="BG3 Mod Tracker", content=content, hero_image_url=hero_image, date_nav_html=nav
    )
    html = html_document("BG3 Mod Tracker", layout)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return len(mods)


def main():
    """CLI entry point."""
    count = generate_html()
    print(f"Generated index.html with {count} entries")


if __name__ == "__main__":
    main()
