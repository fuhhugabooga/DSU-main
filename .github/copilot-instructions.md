# Copilot instructions for DSU

## Project overview
- Single-file Streamlit app: [app.py](app.py) renders **Rețea parteneri**, **Statistici**, **Despre proiect** via a header `st.radio`.
- The UI is CSS-driven with large inline `<style>` blocks for sticky header, responsive layout, and mobile behavior. Preserve these blocks unless asked to redesign.
- Romanian language is used throughout the UI and data.

## Build & run
- **Install dependencies**: `pip install -r requirements.txt`
- **Run the app**: `streamlit run app.py` (must run from repository root for relative data paths to resolve correctly)
- **Dev environment**: Uses Python 3.11+ (see `.devcontainer/devcontainer.json`)
- **No tests**: This project does not have automated tests. Manual testing via the Streamlit UI is required.
- **No linting**: There is no formal linting configuration. Follow existing code style when making changes.

## File structure
- **app.py**: Main application file containing all Streamlit logic, CSS, and visualization code
- **data.csv**: Network partner data (root level, not in `data/` folder)
- **data/**: Contains statistics CSVs for the "Statistici" page
- **logos/**: Logo images embedded as base64 via `get_base64_image()`
- **membrii_fonss.csv**: Optional enrichment data for network members
- **requirements.txt**: Python dependencies (streamlit, pandas, streamlit-agraph, plotly)

## Data & assets
- Network data loads from root [data.csv](data.csv) in `load_data()` (not the [data/](data/) folder). Expected columns: `Partner`, `Domain_Raw`, `Ukraine`, `Strategic`, `Description`.
- Optional enrichment from [membrii_fonss.csv](membrii_fonss.csv): members attach under `FONSS_PARENT_NAME` with `parent_id`.
- Statistics read multiple CSVs under [data/](data/) via `load_all_stats()` (e.g., `interventii_ambulanta.csv`, `apeluri_urgenta.csv`, `timp_raspuns.csv`, `situatii_igsu.csv`, `arii_expertiza.csv`).
- Logos are embedded as base64 from [logos/](logos/) using `get_base64_image()`.

## Key flows & patterns
- Graph nodes/edges are computed once in `load_data()` with `@st.cache_data`. Domains are normalized by `clean_domains()` and `map_domain_category()`.
- Partner type coloring is driven by `ENTITY_TYPES` keywords via `classify_entity_type()` and `get_entity_color()`.
- Filters and selection live in `st.session_state` (`selected_id`, `filter_domains`, `special_filter`, `entity_filter`). Actions typically set state then call `st.rerun()`.
- Two graph modes: focused radial view when a node is selected; clustered view by domain otherwise. See the agraph setup in [app.py](app.py).
- Stats page uses Plotly (`px`/`go`) and a remote Romania GeoJSON in `get_romania_geojson()`.

## Coding standards
- Use Python 3.11+ compatible syntax
- Follow existing function naming conventions (snake_case)
- Maintain the single-file architecture unless explicitly requested to refactor
- Use Streamlit's session state for managing UI state
- Cache expensive operations with `@st.cache_data` decorator
- Preserve existing CSS structure and selectors - many UI behaviors depend on them
- Use Romanian language for user-facing text to match existing UI

## Repo-specific conventions
- Keep the app as a single Streamlit script unless explicitly asked to refactor.
- Preserve existing CSS selectors; many layout behaviors depend on them (sticky header, mobile overlays, agraph sizing).
- Keep `data.csv` and [data/](data/) paths relative (no absolute paths).
- All data files use UTF-8 encoding to support Romanian characters.

## Security and boundaries
- **Never modify or expose**: `.streamlit/secrets.toml` (gitignored), `.env` files, or any credentials
- **Do not commit**: Build artifacts, Python cache files (`__pycache__/`, `*.pyc`), virtual environments, `.DS_Store`
- **Data privacy**: The data files contain public information about DSU partners; treat with appropriate care
- **External dependencies**: Only add new dependencies if absolutely necessary; prefer using existing libraries

## Validation
- Always run the app with `streamlit run app.py` to manually verify changes
- Test on both desktop and mobile layouts (Streamlit's responsive CSS is present)
- Check that all three pages work: "Rețea parteneri", "Statistici", "Despre proiect"
- Verify that filters, graph interactions, and statistics visualizations work as expected
