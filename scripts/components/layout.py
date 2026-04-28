"""Page layout component."""

from .modal import info_button
from .tabs import platform_filter_bar, sort_bar


def page_layout(title: str, content: str, hero_image_url: str = None, date_nav_html: str = "") -> str:
    """Generate the page layout with header, navigation, and main content area."""
    logo_html = (
        f'<img src="{hero_image_url}" alt="Logo" class="header-logo">'
        if hero_image_url
        else ""
    )

    return f"""    <header class="app-header">
        <div class="header-content">
            {logo_html}
            <span class="header-title">{title}</span>
            <div class="header-stat">
                <span class="header-stat-value" id="total-mods">--</span>
                <span>mods</span>
            </div>
            {info_button()}
        </div>
    </header>
    <div class="toast" id="toast" aria-live="polite"></div>
{date_nav_html}
{platform_filter_bar()}
{sort_bar()}
    <main class="changelog-container">
        <div class="changelog-stack">
{content}
        </div>
    </main>"""
