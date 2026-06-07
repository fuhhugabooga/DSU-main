/* =========================================
   MAIN APPLICATION - Routing, Init, Events
   ========================================= */

import { loadNetworkData, loadStatsData } from './data.js?v=2';
import { initNetwork, selectNodeByName } from './network.js?v=2';
import { initStatistics } from './statistics.js?v=2';
import { initAbout } from './about.js?v=2';
import { initNetwork2, resizeNetwork2 } from './network2.js?v=2';

// Pages that show a filter bar pinned under the navbar
const FILTER_BAR_PAGES = { network: 'filter-bar', network2: 'filter-bar2' };

// Current page state
let currentPage = 'network';
let networkInitialized = false;
let statsInitialized = false;
let aboutInitialized = false;
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
        networkInitialized = true;

        // Store stats data for lazy init
        window._statsData = statsData;

        // Initialize about page (lightweight)
        initAbout();
        aboutInitialized = true;

        setupNavigation();
        setupMobileNav();
        setupFilterBarVisibility();

        // Hide loading screen
        document.getElementById('loading-screen').classList.add('hidden');

        // Handle initial URL hash (deep-linking)
        const { page: initialPage, partner: initialPartner } = parseHash();
        if (initialPage && initialPage !== 'network') {
            navigateTo(initialPage);
        }
        if (initialPartner) {
            setTimeout(() => selectNodeByName(initialPartner), 1200);
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
        });

    } catch (err) {
        console.error('Failed to initialize app:', err);
        document.getElementById('loading-screen').innerHTML = `
            <div class="loader-content">
                <div style="color: #f87171; font-size: 1.1rem; margin-bottom: 12px;">Eroare la incarcarea datelor</div>
                <div style="color: #94a3b8; font-size: 0.85rem;">${err.message}</div>
                <button onclick="location.reload()" style="margin-top:16px;padding:10px 24px;background:#dc2626;border:none;border-radius:8px;color:#fff;cursor:pointer;font-family:inherit">Reincearca</button>
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

    // Network-1 overlays (its stats/legend live outside its page element)
    const statsOverlay = document.getElementById('stats-overlay');
    if (statsOverlay) statsOverlay.style.display = page === 'network' ? '' : 'none';
    const legend = document.getElementById('floating-legend');
    if (legend) legend.style.display = page === 'network' ? '' : 'none';

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
    const page = parts[0] || 'network';
    const partner = parts.length > 1 ? decodeURIComponent(parts.slice(1).join('/')) : null;

    return { page, partner };
}

// ---- START ----

document.addEventListener('DOMContentLoaded', init);
