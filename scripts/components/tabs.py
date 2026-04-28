"""Tab components for the mod tracker interface."""

from typing import Optional


# Map mod.io platform identifiers to display labels.
PLATFORM_LABELS = {
    "windows": "PC",
    "mac": "Mac",
    "linux": "Linux",
    "ps5": "PS5",
    "ps4": "PS4",
    "xboxseriesx": "XSX",
    "xboxone": "XB1",
    "switch": "Switch",
    "android": "Android",
    "ios": "iOS",
}


def sort_bar() -> str:
    """Sort selector for re-ordering mod rows within each date section."""
    return """
        <div class="sort-bar">
            <label class="sort-label" for="sort-select">Sort</label>
            <select id="sort-select" class="sort-select" onchange="setSortMode(this.value)">
                <option value="default">Default</option>
                <option value="recent">Most recently updated</option>
                <option value="popular">Most popular</option>
                <option value="downloads">Downloads today</option>
                <option value="subscribers">Most subscribed</option>
                <option value="name-asc">Name A–Z</option>
                <option value="name-desc">Name Z–A</option>
                <option value="author-asc">Author A–Z</option>
            </select>
        </div>
    """


def platform_filter_bar() -> str:
    """Filter chip row above the changelog (All / PC / Console)."""
    return """
        <div class="platform-filter" role="tablist" aria-label="Filter by platform">
            <button class="platform-chip active" data-filter="all" onclick="setPlatformFilter('all')" role="tab" aria-selected="true">All</button>
            <button class="platform-chip" data-filter="pc" onclick="setPlatformFilter('pc')" role="tab" aria-selected="false">PC</button>
            <button class="platform-chip" data-filter="console" onclick="setPlatformFilter('console')" role="tab" aria-selected="false">Console</button>
        </div>
    """


def tab_bar(new_count: int, updated_count: int, active_tab: str = "new") -> str:
    """
    Generate the tab bar with New and Updated tabs.

    Args:
        new_count: Number of new mods
        updated_count: Number of updated mods
        active_tab: Which tab is active ('new' or 'updated')

    Returns:
        HTML string for the tab bar
    """
    new_active = "active" if active_tab == "new" else ""
    updated_active = "active" if active_tab == "updated" else ""

    return f"""
        <div class="tab-bar">
            <div class="tab-group">
                <button class="tab-button {new_active}" data-tab="new" onclick="switchTab('new')">
                    <span>New</span>
                    <span class="tab-count">{new_count}</span>
                </button>
                <button class="tab-button {updated_active}" data-tab="updated" onclick="switchTab('updated')">
                    <span>Updated</span>
                    <span class="tab-count">{updated_count}</span>
                </button>
            </div>
        </div>
    """


def mod_card(
    title: str,
    summary: str,
    image_url: Optional[str] = None,
    profile_url: Optional[str] = None,
    timestamp: Optional[str] = None,
    platforms: Optional[list] = None,
    author: Optional[str] = None,
    date_updated: int = 0,
    popularity_rank: int = 0,
    downloads_today: int = 0,
    subscribers: int = 0,
) -> str:
    """
    Generate a compact mod row.

    Args:
        title: Mod name
        summary: Mod description
        image_url: URL to the mod's thumbnail
        profile_url: URL to the mod's page
        timestamp: Formatted timestamp string
        platforms: List of mod.io platform identifiers (e.g. ["windows", "ps5"])

    Returns:
        HTML string for the mod row
    """
    fallback_image = "https://placehold.co/80x45/e2e8f0/64748b?text=No+Image"
    img_src = image_url or fallback_image

    # Build as a link if profile_url exists
    tag = "a" if profile_url else "div"
    href = (
        f'href="{profile_url}" target="_blank" rel="noopener noreferrer"'
        if profile_url
        else ""
    )

    # Link icon (external link)
    link_icon = (
        """<svg class="mod-link-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 10L14 2m0 0h-5m5 0v5M8 4H3a1 1 0 00-1 1v8a1 1 0 001 1h8a1 1 0 001-1V9"/></svg>"""
        if profile_url
        else ""
    )

    platform_list = platforms or []
    badges_html = ""
    if platform_list:
        chips = "".join(
            f'<span class="mod-badge mod-badge-{p}">{PLATFORM_LABELS.get(p, p)}</span>'
            for p in platform_list
            if p in PLATFORM_LABELS
        )
        if chips:
            badges_html = f'<div class="mod-badges">{chips}</div>'
    data_platforms = " ".join(platform_list)

    sort_key_name = (title or "").lower().replace('"', "&quot;")
    sort_key_author = (author or "").lower().replace('"', "&quot;")

    return f"""<{tag} class="mod-row" data-platforms="{data_platforms}" data-name="{sort_key_name}" data-author="{sort_key_author}" data-date-updated="{date_updated}" data-popularity="{popularity_rank}" data-downloads-today="{downloads_today}" data-subscribers="{subscribers}" {href}>
            <img class="mod-thumb" src="{img_src}" alt="" loading="lazy" onerror="this.src='{fallback_image}'">
            <div class="mod-info">
                <div class="mod-title">{title}</div>
                <div class="mod-summary">{summary}</div>
                {badges_html}
            </div>
            {link_icon}
        </{tag}>"""


def tab_panel(tab_id: str, content: str, is_active: bool = False) -> str:
    """
    Generate a tab panel container.

    Args:
        tab_id: The ID for the tab panel ('new' or 'updated')
        content: The HTML content for the panel
        is_active: Whether this panel is active

    Returns:
        HTML string for the tab panel
    """
    active_class = "active" if is_active else ""

    return f"""
        <div class="tab-panel {active_class}" id="panel-{tab_id}">
            {content}
        </div>
    """


def empty_state(message: str = "No mods to display") -> str:
    """
    Generate an empty state message.

    Args:
        message: The message to display

    Returns:
        HTML string for the empty state
    """
    return f"""
        <div class="empty-state">
            <div class="empty-state-icon">📦</div>
            <div class="empty-state-text">{message}</div>
        </div>
    """


def tabs_script() -> str:
    """
    Generate the JavaScript for tab and date switching.

    Returns:
        JavaScript code for the tab and date navigation functionality
    """
    return """
        <script>
            let currentDateIndex = 0;
            let currentTab = 'new';
            
            function switchTab(tabId) {
                const activeSection = document.querySelector('.date-section.active');
                if (!activeSection) return;
                
                // Check if the tab is disabled, fall back to the other tab
                const tabBtn = activeSection.querySelector(`.tab-button[data-tab="${tabId}"]`);
                if (tabBtn && tabBtn.disabled) {
                    tabId = tabId === 'new' ? 'updated' : 'new';
                }
                
                currentTab = tabId;
                
                // Update tab buttons within the active date section
                activeSection.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.tab === tabId);
                });
                
                // Update panels within the active date section
                activeSection.querySelectorAll('.tab-panel').forEach(panel => {
                    panel.classList.toggle('active', panel.dataset.panel === tabId);
                });
                
                // Save preference
                localStorage.setItem('activeTab', tabId);
            }
            
            function getDaysAgoText(dateStr) {
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                // Parse date like "December 02, 2025"
                const entryDate = new Date(dateStr);
                entryDate.setHours(0, 0, 0, 0);
                
                const diffTime = today - entryDate;
                const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                
                if (diffDays === 0) return 'Today';
                if (diffDays === 1) return '1 day ago';
                return `${diffDays} days ago`;
            }
            
            function updateDateDisplay() {
                const sections = document.querySelectorAll('.date-section');
                const currentLabel = document.querySelector('.date-nav-current');
                const badge = document.querySelector('.date-nav-badge');
                const prevBtn = document.querySelector('.date-nav-btn.prev');
                const nextBtn = document.querySelector('.date-nav-btn.next');
                
                if (!sections.length) return;
                
                // Update visible section
                sections.forEach((section, i) => {
                    section.classList.toggle('active', i === currentDateIndex);
                });
                
                // Update label - show "Start Tracking" for the oldest entry
                const activeSection = sections[currentDateIndex];
                if (currentLabel && activeSection) {
                    const isFirstEntry = currentDateIndex === sections.length - 1;
                    const isMostRecent = currentDateIndex === 0;
                    
                    currentLabel.textContent = isFirstEntry ? 'Started Tracking' : activeSection.dataset.date;
                    
                    // Update badge separately
                    if (badge) {
                        if (isMostRecent && !isFirstEntry) {
                            const daysAgo = getDaysAgoText(activeSection.dataset.date);
                            badge.textContent = `Latest · ${daysAgo}`;
                            badge.style.display = '';
                        } else {
                            badge.style.display = 'none';
                        }
                    }
                }
                
                // Update button states (prev=older, next=newer)
                if (prevBtn) prevBtn.disabled = currentDateIndex === sections.length - 1;
                if (nextBtn) nextBtn.disabled = currentDateIndex === 0;
                
                // Disable empty tabs
                if (activeSection) {
                    const newCount = parseInt(activeSection.dataset.newCount) || 0;
                    const updatedCount = parseInt(activeSection.dataset.updatedCount) || 0;
                    const newBtn = activeSection.querySelector('.tab-button[data-tab="new"]');
                    const updatedBtn = activeSection.querySelector('.tab-button[data-tab="updated"]');
                    if (newBtn) {
                        newBtn.disabled = newCount === 0;
                    }
                    if (updatedBtn) {
                        updatedBtn.disabled = updatedCount === 0;
                    }
                }
                
                // Use section's default tab if current tab is empty for this section
                if (activeSection) {
                    const newCount = parseInt(activeSection.dataset.newCount) || 0;
                    const updatedCount = parseInt(activeSection.dataset.updatedCount) || 0;
                    let tabToShow = currentTab;
                    if (currentTab === 'new' && newCount === 0) {
                        tabToShow = 'updated';
                    } else if (currentTab === 'updated' && updatedCount === 0) {
                        tabToShow = 'new';
                    }
                    switchTab(tabToShow);
                } else {
                    switchTab(currentTab);
                }
            }
            
            function prevDate() {
                const sections = document.querySelectorAll('.date-section');
                if (currentDateIndex < sections.length - 1) {
                    currentDateIndex++;
                    updateDateDisplay();
                }
            }
            
            function nextDate() {
                if (currentDateIndex > 0) {
                    currentDateIndex--;
                    updateDateDisplay();
                }
            }
            
            function formatTimeAgo(date) {
                const now = new Date();
                const diffMs = now - date;
                const diffMins = Math.floor(diffMs / 60000);
                const diffHours = Math.floor(diffMs / 3600000);
                const diffDays = Math.floor(diffMs / 86400000);
                
                if (diffMins < 1) return 'just now';
                if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
                if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
                return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
            }
            
            function showToast(message, duration = 4000) {
                const toast = document.getElementById('toast');
                if (!toast) return;
                
                toast.textContent = message;
                toast.classList.add('show');
                
                setTimeout(() => {
                    toast.classList.remove('show');
                }, duration);
            }
            
            function fetchLastChecked() {
                fetch('https://api.github.com/repos/sherazfn/bg3-mod-tracker/actions/workflows/main.yml/runs?status=success&per_page=1')
                    .then(r => r.json())
                    .then(data => {
                        if (data.workflow_runs && data.workflow_runs.length > 0) {
                            const lastRun = new Date(data.workflow_runs[0].updated_at);
                            showToast(`Last checked: ${formatTimeAgo(lastRun)}`);
                        } else {
                            showToast('Checked hourly');
                        }
                    })
                    .catch(() => {
                        showToast('Checked hourly');
                    });
            }
            
            const PLATFORM_FILTER_KEY = 'bg3-platform-filter';
            const VALID_FILTERS = ['all', 'pc', 'console'];
            const SORT_KEY = 'bg3-sort-mode';
            const VALID_SORTS = ['default', 'recent', 'popular', 'downloads', 'subscribers', 'name-asc', 'name-desc', 'author-asc'];

            function sortValue(row, mode) {
                switch (mode) {
                    case 'recent': return Number(row.dataset.dateUpdated) || 0;
                    case 'popular': {
                        // popularity_rank: lower = more popular; 0 means unknown
                        const v = Number(row.dataset.popularity) || 0;
                        return v === 0 ? Number.POSITIVE_INFINITY : v;
                    }
                    case 'downloads': return Number(row.dataset.downloadsToday) || 0;
                    case 'subscribers': return Number(row.dataset.subscribers) || 0;
                    case 'name-asc':
                    case 'name-desc': return row.dataset.name || '';
                    case 'author-asc': return row.dataset.author || '';
                    default: return 0;
                }
            }

            function compareRows(a, b, mode) {
                const av = sortValue(a, mode);
                const bv = sortValue(b, mode);
                if (mode === 'name-asc' || mode === 'author-asc') {
                    return String(av).localeCompare(String(bv));
                }
                if (mode === 'name-desc') {
                    return String(bv).localeCompare(String(av));
                }
                // numeric, larger first (recent, popular handled by infinity, downloads, subs)
                if (mode === 'popular') return av - bv; // ascending: lower rank first
                return bv - av;
            }

            function applySortMode(mode) {
                if (!VALID_SORTS.includes(mode)) mode = 'default';
                document.querySelectorAll('.mod-list').forEach(list => {
                    const rows = Array.from(list.querySelectorAll('.mod-row'));
                    if (rows.length < 2) return;
                    if (mode === 'default') {
                        // Restore original DOM order from data-original-index
                        rows.sort((a, b) => Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex));
                    } else {
                        rows.sort((a, b) => compareRows(a, b, mode));
                    }
                    rows.forEach(r => list.appendChild(r));
                });
                const sel = document.getElementById('sort-select');
                if (sel && sel.value !== mode) sel.value = mode;
            }

            function setSortMode(mode) {
                if (!VALID_SORTS.includes(mode)) mode = 'default';
                localStorage.setItem(SORT_KEY, mode);
                applySortMode(mode);
            }

            function snapshotOriginalOrder() {
                document.querySelectorAll('.mod-list').forEach(list => {
                    Array.from(list.querySelectorAll('.mod-row')).forEach((row, i) => {
                        row.dataset.originalIndex = String(i);
                    });
                });
            }

            function rowMatchesFilter(row, filter) {
                if (filter === 'all') return true;
                const platforms = (row.dataset.platforms || '').split(/\\s+/);
                if (filter === 'pc') {
                    return platforms.includes('windows') || platforms.includes('mac') || platforms.includes('linux');
                }
                if (filter === 'console') {
                    return platforms.includes('ps5') || platforms.includes('ps4') ||
                           platforms.includes('xboxseriesx') || platforms.includes('xboxone') ||
                           platforms.includes('switch');
                }
                return true;
            }

            function applyPlatformFilter(filter) {
                if (!VALID_FILTERS.includes(filter)) filter = 'all';
                document.querySelectorAll('.mod-row').forEach(row => {
                    row.style.display = rowMatchesFilter(row, filter) ? '' : 'none';
                });
                document.querySelectorAll('.platform-chip').forEach(chip => {
                    const isActive = chip.dataset.filter === filter;
                    chip.classList.toggle('active', isActive);
                    chip.setAttribute('aria-selected', isActive ? 'true' : 'false');
                });
                updateTotalModsCount(filter);
            }

            function setPlatformFilter(filter) {
                if (!VALID_FILTERS.includes(filter)) filter = 'all';
                localStorage.setItem(PLATFORM_FILTER_KEY, filter);
                applyPlatformFilter(filter);
            }

            function updateTotalModsCount(filter) {
                const totalModsEl = document.getElementById('total-mods');
                if (!totalModsEl) return;
                if (filter === 'all') {
                    let total = 0;
                    document.querySelectorAll('.date-section').forEach(s => {
                        total += parseInt(s.dataset.newCount) || 0;
                    });
                    totalModsEl.textContent = total.toLocaleString();
                } else {
                    // Count visible "added" rows across all date sections.
                    const visible = document.querySelectorAll('.tab-panel[data-panel="new"] .mod-row');
                    let count = 0;
                    visible.forEach(row => { if (rowMatchesFilter(row, filter)) count++; });
                    totalModsEl.textContent = count.toLocaleString();
                }
            }

            // Initialize on load
            document.addEventListener('DOMContentLoaded', function() {
                const savedTab = localStorage.getItem('activeTab');
                if (savedTab && ['new', 'updated'].includes(savedTab)) {
                    currentTab = savedTab;
                }

                updateDateDisplay();

                snapshotOriginalOrder();

                const savedFilter = localStorage.getItem(PLATFORM_FILTER_KEY) || 'all';
                applyPlatformFilter(VALID_FILTERS.includes(savedFilter) ? savedFilter : 'all');

                const savedSort = localStorage.getItem(SORT_KEY) || 'default';
                applySortMode(VALID_SORTS.includes(savedSort) ? savedSort : 'default');

                fetchLastChecked();
            });
        </script>
    """
