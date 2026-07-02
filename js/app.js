/* =========================================
   MAIN APPLICATION - Routing, Init, Events
   ========================================= */

import { loadNetworkData, loadStatsData } from './data.js';
import { initNetwork, selectNodeByName } from './network.js';
import { initStatistics } from './statistics.js';
import { initAbout } from './about.js';
import { initNetwork2, resizeNetwork2, selectNet2ByName } from './network2.js';

const PAGES = ['network', 'network2', 'statistics', 'about'];

// Pages that show a filter bar pinned under the navbar
const FILTER_BAR_PAGES = { network: 'filter-bar', network2: 'filter-bar2' };

// Current page state
let currentPage = 'network';
let statsInitialized = false;
let net2Initialized = false;

// ---- INITIALIZATION ----

async function init() {
    try {
        // Load data in parallel
        const [networkData, statsData] = await Promise.all([
            loadNetworkData(),
            loadStatsData()
        ]);

        // Initialize network page (default)
        initNetwork(networkData);

        // Store stats data for lazy init
        window._statsData = statsData;

        // Initialize about page (lightweight)
        initAbout();

        setupNavigation();
        setupMobileNav();
        setupFilterBarVisibility();
        setupOnboarding();
        setupTheme();

        // Hide loading screen
        document.getElementById('loading-screen').classList.add('hidden');

        // Handle initial URL hash (deep-linking)
        const { page: initialPage, partner: initialPartner } = parseHash();
        if (initialPage && initialPage !== 'network') {
            navigateTo(initialPage);
        }
        if (initialPartner) {
            const sel = initialPage === 'network2' ? selectNet2ByName : selectNodeByName;
            setTimeout(() => sel(initialPartner), 1200);
        }

        // Listen for hash changes
        window.addEventListener('hashchange', () => {
            const { page, partner } = parseHash();
            if (page && page !== currentPage) {
                navigateTo(page);
            }
            if (page === 'network' && partner) {
                selectNodeByName(partner);
            }
            if (page === 'network2' && partner) {
                setTimeout(() => selectNet2ByName(partner), currentPage === 'network2' ? 50 : 600);
            }
        });

    } catch (err) {
        console.error('Failed to initialize app:', err);
        document.getElementById('loading-screen').innerHTML = `
            <div class="loader-content">
                <div style="color: #f87171; font-size: 1.1rem; margin-bottom: 12px;">Eroare la încărcarea datelor</div>
                <div style="color: #94a3b8; font-size: 0.85rem;">${err.message}</div>
                <button onclick="location.reload()" style="margin-top:16px;padding:10px 24px;background:#dc2626;border:none;border-radius:8px;color:#fff;cursor:pointer;font-family:inherit">Reîncearcă</button>
            </div>
        `;
    }
}

// ---- NAVIGATION ----

function setupNavigation() {
    document.querySelectorAll('#main-nav .nav-link').forEach(link => {
        link.addEventListener('click', () => navigateTo(link.dataset.page));
    });

    document.querySelectorAll('#mobile-nav-dropdown .mobile-nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navigateTo(link.dataset.page);
            closeMobileNav();
        });
    });
}

function navigateTo(page) {
    if (page === currentPage) return;

    const currentEl = document.getElementById(`page-${currentPage}`);
    const nextEl = document.getElementById(`page-${page}`);

    if (currentEl && nextEl) {
        currentEl.classList.add('page-exit');
        setTimeout(() => {
            currentEl.classList.remove('page-exit', 'active');
            finishNavigation(page, nextEl);
        }, 200);
    } else {
        finishNavigation(page, nextEl);
    }
}

function finishNavigation(page, nextEl) {
    currentPage = page;

    history.replaceState(null, '', `#${page}`);

    document.querySelectorAll('#main-nav .nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });
    document.querySelectorAll('#mobile-nav-dropdown .mobile-nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });

    if (nextEl) nextEl.classList.add('active');

    updateFilterBarVisibility(page);

    // Lazy init statistics
    if (page === 'statistics' && !statsInitialized && window._statsData) {
        initStatistics(window._statsData);
        statsInitialized = true;
    }
    if (page === 'statistics') {
        setTimeout(() => window.dispatchEvent(new Event('resize')), 150);
    }

    // Lazy init network 2 (ONG <-> ISU); resize on every visit
    if (page === 'network2') {
        setTimeout(() => {
            if (!net2Initialized) {
                initNetwork2();
                net2Initialized = true;
            } else {
                resizeNetwork2();
            }
        }, net2Initialized ? 50 : 400);
    }
}

// ---- FILTER BAR VISIBILITY ----

function setupFilterBarVisibility() {
    updateFilterBarVisibility(currentPage);
}

function updateFilterBarVisibility(page) {
    const activeBar = FILTER_BAR_PAGES[page] || null;

    // Show only the active page's filter bar, hide the others
    Object.values(FILTER_BAR_PAGES).forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === activeBar) ? '' : 'none';
    });

    // body.no-filter-bar drives the app-container top offset (CSS only)
    document.body.classList.toggle('no-filter-bar', !activeBar);

    if (!activeBar) {
        document.getElementById('mobile-filter-panel')?.classList.add('hidden');
    }
}

// ---- ONBOARDING / WELCOME MODAL ----

function setupOnboarding() {
    const overlay = document.getElementById('onboarding-overlay');
    if (!overlay) return;

    const open = () => overlay.classList.remove('hidden');
    const close = () => {
        overlay.classList.add('hidden');
        localStorage.setItem('dsu-onboarding-seen', '1');
    };

    document.getElementById('onboarding-close')?.addEventListener('click', close);
    document.getElementById('onboarding-start')?.addEventListener('click', close);
    document.getElementById('info-btn')?.addEventListener('click', open);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !overlay.classList.contains('hidden')) close();
    });

    overlay.querySelectorAll('.onboarding-card[data-page]').forEach(card => {
        card.addEventListener('click', () => {
            close();
            navigateTo(card.dataset.page);
        });
    });

    // Show automatically on first visit
    if (!localStorage.getItem('dsu-onboarding-seen')) open();
}

// ---- THEME TOGGLE ----

function setupTheme() {
    const saved = localStorage.getItem('dsu-theme') || 'dark';
    applyTheme(saved);

    document.getElementById('theme-toggle')?.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        localStorage.setItem('dsu-theme', next);
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    const btn = document.getElementById('theme-toggle');
    if (btn) {
        btn.innerHTML = theme === 'dark'
            ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
            : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
        btn.title = theme === 'dark' ? 'Comută la tema deschisă' : 'Comută la tema întunecată';
    }

    // Plotly charts bake colors in at render time — let statistics re-render
    window.dispatchEvent(new CustomEvent('dsu-theme-change'));
}

// ---- MOBILE NAV ----

function setupMobileNav() {
    const toggle = document.getElementById('mobile-nav-toggle');
    const dropdown = document.getElementById('mobile-nav-dropdown');

    if (!toggle || !dropdown) return;

    toggle.addEventListener('click', () => {
        const isOpen = !dropdown.classList.contains('hidden');
        if (isOpen) {
            closeMobileNav();
        } else {
            dropdown.classList.remove('hidden');
            toggle.classList.add('active');
        }
    });

    document.addEventListener('click', (e) => {
        if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
            closeMobileNav();
        }
    });
}

function closeMobileNav() {
    const dropdown = document.getElementById('mobile-nav-dropdown');
    const toggle = document.getElementById('mobile-nav-toggle');
    if (dropdown) dropdown.classList.add('hidden');
    if (toggle) toggle.classList.remove('active');
}

// ---- URL HASH ROUTING ----

function parseHash() {
    const hash = location.hash.replace('#', '');
    if (!hash) return { page: 'network', partner: null };

    const parts = hash.split('/');
    // Unknown page names (mistyped or stale links) fall back to the default
    // page instead of leaving the app on a blank screen.
    const page = PAGES.includes(parts[0]) ? parts[0] : 'network';
    const partner = parts.length > 1 ? decodeURIComponent(parts.slice(1).join('/')) : null;

    return { page, partner };
}

// ---- START ----

document.addEventListener('DOMContentLoaded', init);
