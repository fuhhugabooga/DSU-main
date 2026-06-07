# CLAUDE.md

## Project Overview

**DSU Ecosystem Partners** (Ecosistemul Partenerilor DSU) is an interactive web visualization platform that maps partnership networks between Romania's Department for Emergency Situations (DSU) and various organizations. It also provides comprehensive statistics about DSU operations.

- **Version:** v0.2 (January 2026)
- **License:** Apache 2.0
- **Language:** Romanian (UI text, data, labels)
- **Type:** Static client-side SPA — no backend, no build step

## Tech Stack

- **JavaScript (ES6 modules)** — all application logic
- **HTML5 / CSS3** — single-page shell with CSS custom properties
- **D3.js v7** — force-directed network graph (CDN)
- **Plotly.js v2.35.0** — statistical charts and Romania choropleth (CDN)
- **Google Fonts** — Inter + Nunito typefaces

No npm, no bundler, no build process. All dependencies are loaded via CDN in `index.html`.

## Repository Structure

```
├── index.html                 # SPA entry point (navbar, filter bar, page shells)
├── js/
│   ├── app.js                 # Routing, initialization, navigation events
│   ├── data.js                # CSV loading, parsing, entity classification
│   ├── network.js             # D3 force graph (partners ↔ domains), filters, search
│   ├── network2.js            # D3 bipartite force graph (ONG ↔ ISU județean)
│   ├── statistics.js          # Plotly charts across 4 tabs
│   └── about.js               # About page HTML generation
├── css/
│   └── app.css                # All styles (dark theme, responsive, animations)
├── data.csv                   # Main partner data (64 partners; domains standardized)
├── data_retea2_isu.csv        # Network 2 data (256 ONGs ↔ 34 ISU județene)
├── muchii_operational_bipartit.csv # Optional per-edge context for network 2
├── membrii_fonss.csv          # FONSS organization members (45 members)
├── data/                      # 18 statistics CSV files
│   ├── interventii_ambulanta.csv
│   ├── apeluri_urgenta.csv
│   ├── timp_raspuns.csv
│   ├── situatii_igsu.csv
│   ├── categorii_risc.csv
│   ├── ore_zbor.csv
│   ├── prezentari_upu.csv
│   ├── instruire_persoane.csv
│   ├── protocoale.csv
│   ├── tipuri_actiuni.csv
│   ├── arii_expertiza.csv
│   ├── flux_interventie.csv
│   ├── detaliere_timpi.csv
│   ├── sanctiuni.csv
│   ├── lant_comanda.csv
│   ├── timeline_dsu.csv
│   └── harta_isu.csv
├── logos/                     # Brand assets (DSU, UVT, FabLab/ConnecTM)
├── TASKS.md                   # Outstanding feature tasks
├── .github/
│   ├── CODEOWNERS
│   └── copilot-instructions.md  # Legacy AI instructions (references old Streamlit app)
├── .devcontainer/
│   └── devcontainer.json      # Dev container config (Python 3.11, legacy)
└── .nojekyll                  # Disables Jekyll for GitHub Pages
```

## How to Run

Open `index.html` in a modern browser. No server required for basic viewing, though a local HTTP server is needed for `fetch()` to work with CSV files:

```bash
# Python
python3 -m http.server 8000

# Node.js (npx)
npx serve .
```

Then open `http://localhost:8000`.

## Architecture

### Pages (SPA routing via `app.js`)

1. **Rețea parteneri** (`#page-network`) — Interactive D3.js force-directed graph of DSU partners. Includes search, multi-filter dropdowns (entity type, domain, special flags), a floating legend, stats overlay, and partner detail cards.
2. **Rețea operațională** (`#page-network2`) — Bipartite D3.js force graph of operational collaborations during the pandemic and refugee crisis: 256 NGOs ↔ 34 county emergency inspectorates (ISU). ISU hubs render as diamonds; NGO nodes are colored by actor type (`Tip_actor`) and sized by collaboration count (`Nr_colaborari`). Filterable by crisis context (Pandemie / Aflux refugiați / Ambele). Lazily initialized on first visit (`network2.js`, data via `loadNetwork2Data()`).
3. **Statistici** (`#page-statistics`) — Four tabbed views (Operational, Medical, Prevention, Advanced) with Plotly charts. Lazily initialized on first visit.
4. **Despre proiect** (`#page-about`) — Project information, team, data sources. Generated dynamically by `about.js`.

### Module Dependency Graph

```
app.js (entry)
├── data.js      — loadNetworkData(), loadStatsData(), entity classification
├── network.js   — initNetwork(), D3 force simulation, filter state, interactions
├── statistics.js — initStatistics(), Plotly chart rendering
└── about.js     — initAbout(), static HTML generation
```

### Data Flow

1. `app.js` calls `loadNetworkData()` and `loadStatsData()` in parallel on `DOMContentLoaded`
2. `data.js` fetches and parses CSVs, classifies entities by keyword matching, builds a graph of nodes and edges
3. Network data is passed to `initNetwork()` which creates the D3 force simulation
4. Stats data is stored on `window._statsData` and lazily passed to `initStatistics()` on first tab visit

### Key Data Concepts

- **Partners** are loaded from `data.csv` with columns: `Partner`, `Domain_Raw`, `Ukraine`, `Strategic`, `Description`
- **FONSS members** from `membrii_fonss.csv` are attached as children of the FONSS parent node
- **Entity types** (6 categories) are classified by keyword matching on organization name — see `ENTITY_TYPES` in `data.js`
- **Domain groups** (4 categories) aggregate raw domain strings into higher-level categories — see `DOMAIN_GROUPS` in `data.js`
- **Statistics** are 16 independent CSV files under `data/`, each with their own schema

## Code Conventions

### JavaScript
- ES6 module syntax (`import`/`export`) — no CommonJS
- `async`/`await` for data fetching
- Template literals for HTML generation
- No framework — vanilla DOM manipulation
- Function naming: `camelCase` for functions and variables
- Constants: `UPPER_SNAKE_CASE` for exported config objects (`DOMAIN_GROUPS`, `ENTITY_TYPES`, `FONSS_PARENT_NAME`, `ISU_TO_JUDET`)

### CSS
- Single file `css/app.css` (~1,885 lines)
- CSS custom properties for theming (colors, spacing, motion, typography)
- Dark theme: gradient background `#0a0e1a` to `#1a0f0f`, light text
- Accent color: `#dc2626` (red)
- Mobile-first responsive design with media queries
- BEM-like naming (`.fb-dropdown-btn`, `.stat-card`, `.nav-link`)

### HTML
- Semantic elements with `aria-label` attributes for accessibility
- IDs for JavaScript hooks (e.g., `#search-input`, `#entity-panel`, `#graph-container`)
- Romanian language (`lang="ro"`)

### Data Files
- CSV format with comma separators and quoted fields
- BOM handling in parser (removes `\uFEFF`)
- All data paths are relative to the repo root
- Boolean fields use flexible truthy values: `da`, `true`, `x`, `1`, `yes`

## Development Guidelines

### When Modifying Code

- **No build step** — changes are immediately reflected on page reload
- Keep all data paths relative (no absolute paths)
- Preserve CSS custom properties and existing selectors — layout behaviors depend on them (sticky header, mobile overlays, graph sizing)
- The filter bar is only visible on the network page — `updateFilterBarVisibility()` in `app.js` manages this
- When adding new statistics, add a CSV file under `data/`, register it in `loadStatsData()` in `data.js`, and render it in the appropriate tab function in `statistics.js`

### When Modifying Data

- `data.csv` is the primary partner dataset — maintain the column structure (`Partner`, `Domain_Raw`, `Ukraine`, `Strategic`, `Description`)
- `membrii_fonss.csv` uses columns `Nume` and `Descriere`
- Domain classification relies on keyword matching in `mapDomainCategory()` — adding new domains may require updating this function
- Entity type classification relies on keyword matching in `classifyEntityType()` — adding new entity types requires updating `ENTITY_TYPES` in `data.js`

### Important Patterns

- **Lazy initialization:** Statistics page is only initialized when the user navigates to it
- **Filter state:** Managed internally in `network.js` — dropdowns, search, and graph rendering are tightly coupled
- **Graph modes:** Force-directed layout clusters by domain; selecting a node focuses on it with connected nodes
- **Mobile responsiveness:** Separate mobile nav dropdown and mobile filter panel — changes to desktop UI should be mirrored for mobile

## No Test Suite / No CI

This project has no automated tests, no linting configuration, and no CI/CD pipelines. Changes are tested manually in the browser. There is no `package.json`.

## Outstanding Tasks

See `TASKS.md` for the current feature backlog, including:
- Filter count display
- Empty graph message
- Navigation help card
- Statistics grid alignment
- About page updates
- Sources and data section

## Legacy Notes

- The project was originally a single-file Streamlit Python app (`app.py`) that has since been deleted
- `.github/copilot-instructions.md` still references the old Streamlit architecture — it is outdated
- `.devcontainer/devcontainer.json` and `requirements.txt` reference Python/Streamlit — these are legacy artifacts
- The `.gitignore` is Python-centric (`.pyc`, `__pycache__`, `venv`) and lacks JavaScript-specific patterns
