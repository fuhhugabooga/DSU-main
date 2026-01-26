# Copilot instructions for DSU

## Project overview
- Single-file Streamlit app: [app.py](app.py) renders **Rețea parteneri**, **Statistici**, **Despre proiect** via a header `st.radio`.
- The UI is CSS-driven with large inline `<style>` blocks for sticky header, responsive layout, and mobile behavior. Preserve these blocks unless asked to redesign.

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

## Developer workflow
- Install deps from [requirements.txt](requirements.txt): `streamlit`, `pandas`, `streamlit-agraph`, `plotly`.
- Run from repo root so relative data paths resolve: `streamlit run app.py`.

## Repo-specific conventions
- Keep the app as a single Streamlit script unless explicitly asked to refactor.
- Preserve existing CSS selectors; many layout behaviors depend on them (sticky header, mobile overlays, agraph sizing).
- Keep `data.csv` and [data/](data/) paths relative (no absolute paths).
