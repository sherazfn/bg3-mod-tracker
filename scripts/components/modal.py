"""Info modal component."""

INFO_MODAL_HTML = """
    <!-- Info Modal -->
    <div class="modal-overlay" id="info-modal" aria-hidden="true">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()" aria-label="Close modal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
            <div class="modal-header">
                <h2 class="modal-title">About This Tracker</h2>
            </div>
            <div class="modal-body">
                <p>This site tracks <strong>new and updated mods</strong> for Baldur's Gate 3 across PC and console (PlayStation &amp; Xbox).</p>

                <div class="modal-section">
                    <h3>How It Works</h3>
                    <p>The tracker automatically checks <a href="https://mod.io/g/baldursgate3" target="_blank" rel="noopener">mod.io</a> every hour for new mods and version updates on every supported platform.</p>
                </div>

                <div class="modal-section">
                    <h3>Features</h3>
                    <ul>
                        <li><strong>New Mods</strong> — Freshly added mods on any platform</li>
                        <li><strong>Updated Mods</strong> — Existing mods that received version bumps</li>
                        <li><strong>Platform Filter</strong> — Filter the feed by PC or Console</li>
                        <li><strong>Daily Navigation</strong> — Browse changes by date</li>
                    </ul>
                </div>

                <div class="modal-section">
                    <h3>Links</h3>
                    <p>
                        <a href="https://github.com/sherazfn/bg3-mod-tracker" target="_blank" rel="noopener">View on GitHub</a>
                    </p>
                    <p class="modal-credit">Forked from <a href="https://github.com/xKeeg/bg3-console-mod-tracker" target="_blank" rel="noopener">xKeeg/bg3-console-mod-tracker</a> &mdash; original work by xKeeg.</p>
                </div>
            </div>
        </div>
    </div>
"""


def info_button() -> str:
    """Generate the info button for the header."""
    return """<button class="info-btn" onclick="openModal()" aria-label="About this tracker">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            </button>"""


def info_modal() -> str:
    """Generate the info modal HTML."""
    return INFO_MODAL_HTML


MODAL_SCRIPT = """
    <script>
        function openModal() {
            const modal = document.getElementById('info-modal');
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
        
        function closeModal() {
            const modal = document.getElementById('info-modal');
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }
        
        // Close modal on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
        
        // Close modal on overlay click
        document.getElementById('info-modal')?.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    </script>
"""
