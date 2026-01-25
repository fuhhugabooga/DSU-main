import streamlit as st
import pandas as pd
import os
import math
import random
import base64
import plotly.express as px
import plotly.graph_objects as go
from streamlit_agraph import agraph, Node, Edge, Config

def get_base64_image(image_path):
    """Convert image to base64 string for embedding in HTML."""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# ---------------------------------
# 0. CONFIGURARE PAGINĂ
# ---------------------------------

st.set_page_config(
    layout="wide",
    page_title="Ecosistem DSU",
    initial_sidebar_state="collapsed"
)

# ---------------------------------
# 1. MODERN CSS STYLING
# ---------------------------------

st.markdown(
    """
    <style>
    /* GLOBAL RESET */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a0f0f 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin-top: -30px !important; /* Pulls content up into the empty header space */
    }
    
    /* REMOVE the ".main .block-container" rule that was here previously */
    
    header[data-testid="stHeader"] { 
        display: none !important;
    }
    
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Remove ghost spacing */
    .main .block-container {
        padding-top: 1rem !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* STICKY HEADER */
    .sticky-header-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: linear-gradient(135deg, #0a0e1a 0%, #1a0f0f 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        padding: 10px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .sticky-header-spacer {
        height: 65px;
        margin-bottom: 10px;
    }

    .header-logo {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .header-logo-box {
        width: 45px;
        height: 45px;
        background: rgba(220, 38, 38, 0.2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #dc2626;
        font-weight: bold;
        font-size: 0.9rem;
    }

    .header-title {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .header-nav {
        display: flex;
        gap: 8px;
    }

    .header-nav-btn {
        background: transparent;
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 8px 20px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
    }

    .header-nav-btn:hover {
        background: rgba(220, 38, 38, 0.1);
        border-color: rgba(220, 38, 38, 0.5);
    }

    .header-nav-btn.active {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        border-color: transparent;
        color: #ffffff;
    }

    .header-logos {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .header-logo-placeholder {
        width: 40px;
        height: 40px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }

    /* Radio buttons - position in sticky header */
    .stRadio {
        position: fixed !important;
        top: 12px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 9999999 !important;
    }

    div[role="radiogroup"] {
        flex-direction: row;
        gap: 8px;
        justify-content: center;
        background: transparent;
    }

    div[role="radiogroup"] label {
        background: transparent !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    div[role="radiogroup"] label:hover {
        background: rgba(220, 38, 38, 0.1) !important;
        border-color: rgba(220, 38, 38, 0.5) !important;
    }

    div[role="radiogroup"] label p {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        margin: 0 !important;
    }

    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    div[data-baseweb="radio"] div[aria-checked="true"] + div {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        border-color: transparent !important;
    }

    div[data-baseweb="radio"] div[aria-checked="true"] + div p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Remove all bottom borders and padding from graph container */
    iframe {
        border: none !important;
    }

    /* Fix empty space under graph */
    .element-container:has(iframe) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stVerticalBlock"] > div:has(iframe) {
        margin-bottom: 0 !important;
    }

    /* Graph container zoom animation */
    @keyframes zoomIn {
        from {
            transform: scale(0.85);
            opacity: 0.5;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }

    .stApp iframe {
        animation: zoomIn 0.8s ease-out forwards;
    }

    /* Graph iframe - fill available space */
    iframe {
        height: calc(100vh - 100px) !important;
        min-height: 600px !important;
    }
    
    /* CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(220, 38, 38, 0.2);
        border-color: rgba(220, 38, 38, 0.3);
    }
    
    .partner-card {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(153, 27, 27, 0.1) 100%);
        border: 1px solid rgba(220, 38, 38, 0.3);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(220, 38, 38, 0.15);
    }
    
    .partner-title {
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(220, 38, 38, 0.2);
    }
    
    .partner-desc {
        font-size: 1.05rem;
        color: #cbd5e1;
        line-height: 1.7;
        margin-bottom: 20px;
    }
    
    /* INFO BOXES */
    .info-box {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(153, 27, 27, 0.1) 100%);
        border-left: 4px solid #dc2626;
        padding: 20px;
        margin-bottom: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.1);
    }
    
    .info-title {
        font-weight: 700;
        color: #f87171;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    
    .info-text {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* METRICS */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(220, 38, 38, 0.2);
        border-color: rgba(220, 38, 38, 0.4);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* BADGES */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    
    .badge:hover {
        transform: scale(1.05);
    }
    
    .badge-strategic {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-ukraine {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .badge-fonss {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
        color: #ffffff;
        border: 1px solid rgba(236, 72, 153, 0.3);
    }
    
    .tag-domain {
        display: inline-block;
        background: rgba(220, 38, 38, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(220, 38, 38, 0.3);
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-right: 6px;
        margin-bottom: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .tag-domain:hover {
        background: rgba(220, 38, 38, 0.25);
        border-color: rgba(220, 38, 38, 0.5);
    }
    
    /* SEARCH BOX */
    div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(220, 38, 38, 0.4);
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #cbd5e1 !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(220, 38, 38, 0.1);
    }
    
    /* SECTION HEADERS */
    h3 {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 24px;
        font-size: 1.5rem;
    }
    
    h4 {
        color: #e2e8f0;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    /* DIVIDER */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
        margin: 32px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------
# 2. DATA LOGIC (UNCHANGED)
# ---------------------------------

DOMAIN_GROUPS = {
    "Intervenții, urgențe": ["Intervenție", "Căutare-salvare", "Dezastre chimice", "Răspuns"],
    "Educație, prevenire": ["Prevenire", "Pregătire", "Cercetare", "Prevenirea si combaterea dezinformării"],
    "Logistică, tehnologie": ["IT & C", "Sprijin logistic", "Restabilirea stării de normalitate", "Sprijin tehnic logistic"],
    "Social, medical": ["Servicii sociale", "Prevenire (trafic persoane)"]
}

# Entity type classification and colors
ENTITY_TYPES = {
    "Universitate": {"color": "#8b5cf6", "keywords": ["universitatea", "academia", "facultatea", "politehnica"]},
    "ONG": {"color": "#10b981", "keywords": ["asociația", "fundația", "organizația", "federația"]},
    "Instituție de stat": {"color": "#3b82f6", "keywords": ["serviciul", "autoritatea", "institutul național", "compania națională"]},
    "Companie privată": {"color": "#f59e0b", "keywords": ["s.a.", "srl", "autonom", "omv", "e-distribuție", "transelectrica"]},
    "Media": {"color": "#ec4899", "keywords": ["televiziune", "radiodifuziune", "srtv"]},
    "Organizație profesională": {"color": "#14b8a6", "keywords": ["colegiul", "consiliul", "societatea română", "unsar", "amcham"]},
}

def classify_entity_type(name: str) -> str:
    """Classify a partner into an entity type based on name patterns."""
    name_lower = name.lower()

    # Check each entity type's keywords
    for entity_type, config in ENTITY_TYPES.items():
        for keyword in config["keywords"]:
            if keyword in name_lower:
                return entity_type

    # Default to ONG if no match
    return "ONG"

def get_entity_color(name: str) -> str:
    """Get the color for an entity based on its type."""
    entity_type = classify_entity_type(name)
    return ENTITY_TYPES.get(entity_type, ENTITY_TYPES["ONG"])["color"]

FONSS_PARENT_NAME = "Federația Organizațiilor Neguvernamentale pentru Servicii Sociale (FONSS)"

def clean_domains(domain_str: str) -> list[str]:
    if pd.isna(domain_str): return []
    text = str(domain_str).strip()
    if text in ["", "-"]: return []
    text = text.replace("\n", "/").replace("|", "/").replace("\\", "/")
    return [p.strip() for p in text.split("/") if p.strip()]

def map_domain_category(raw_piece: str) -> str:
    t = raw_piece.lower()
    if "dezastre chimice" in t: return "Dezastre chimice"
    if "smart city" in t or "it & c" in t: return "IT & C"
    if "căutare" in t or "caini" in t or "câini" in t: return "Căutare-salvare"
    if "restabilirea" in t: return "Restabilirea stării de normalitate"
    if "sociale" in t: return "Servicii sociale"
    if "logistic" in t: return "Sprijin logistic"
    if "răspuns" in t or "traum" in t or "psiholog" in t: return "Răspuns"
    if "trafic" in t: return "Prevenire (trafic persoane)"
    if "prevenire" in t: return "Prevenire"
    if "pregătire" in t or "practică" in t or "training" in t: return "Pregătire"
    if "cercetare" in t: return "Cercetare"
    if "intervenție" in t: return "Intervenție"
    return raw_piece.strip()

@st.cache_data
def load_data():
    nodes_dict = {}
    edges_list = []
    all_domains_set = set()
    
    try:
        df = pd.read_csv("data.csv", on_bad_lines='skip')
    except FileNotFoundError:
        return {}, [], pd.DataFrame(), [], None

    df.columns = [c.strip() for c in df.columns]
    if "Ukraine" not in df.columns: df["Ukraine"] = False
    if "Strategic" not in df.columns: df["Strategic"] = False
    if "Description" not in df.columns: df["Description"] = ""

    def normalize_bool(val):
        return str(val).strip().lower() in ["da", "true", "x", "1", "yes"]

    df["Ukraine"] = df["Ukraine"].apply(normalize_bool)
    df["Strategic"] = df["Strategic"].apply(normalize_bool)
    df["Domains_List"] = df["Domain_Raw"].apply(clean_domains)

    fonss_id = None

    for idx, row in df.iterrows():
        p_id = f"p_{idx}"
        partner_label = str(row["Partner"]).strip()
        
        if partner_label == FONSS_PARENT_NAME:
            fonss_id = p_id

        nodes_dict[p_id] = {
            "label": partner_label,
            "type": "Partner",
            "ukraine": row["Ukraine"],
            "strategic": row["Strategic"],
            "description": str(row["Description"]) if not pd.isna(row["Description"]) else "Descriere indisponibilă.",
            "raw_domain": str(row["Domain_Raw"]),
            "parent_id": None
        }

        for raw_dom in row["Domains_List"]:
            dom_cat = map_domain_category(raw_dom)
            all_domains_set.add(dom_cat)
            d_id = f"d_{dom_cat}"
            if d_id not in nodes_dict:
                nodes_dict[d_id] = {
                    "label": dom_cat,
                    "type": "Domain",
                }
            edges_list.append((p_id, d_id))

    if fonss_id and os.path.exists("membrii_fonss.csv"):
        try:
            df_fonss = pd.read_csv("membrii_fonss.csv", on_bad_lines='skip')
            if "Nume" in df_fonss.columns:
                for idx, row in df_fonss.iterrows():
                    m_id = f"m_fonss_{idx}"
                    label = str(row["Nume"]).strip()
                    desc = row["Descriere"] if "Descriere" in row else "Membru FONSS"
                    nodes_dict[m_id] = {
                        "label": label,
                        "type": "Partner",
                        "ukraine": False,
                        "strategic": False,
                        "description": str(desc),
                        "raw_domain": "Servicii sociale",
                        "parent_id": fonss_id,
                        "is_fonss_member": True
                    }
        except Exception:
            pass

    return nodes_dict, edges_list, df, sorted(list(all_domains_set)), fonss_id

nodes_data, edges_data, df, all_domain_labels, fonss_id = load_data()

# ---------------------------------
# 3. NAVIGATION - Sticky Header with Navigation
# ---------------------------------

# Initialize page state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Ecosistem parteneri"

# Load logos as base64
dsu_logo = get_base64_image("logos/dsu.png")
uvt_logo = get_base64_image("logos/uvt.png")
fsgc_logo = get_base64_image("logos/fsgc.png")

# Render sticky header with HTML and logos
st.markdown(f"""
<div class="sticky-header-container">
    <div class="header-logo">
        <a href="https://www.dsu.mai.gov.ro/" target="_blank" style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{dsu_logo}" alt="DSU" style="height: 50px; width: auto; border-radius: 4px; cursor: pointer;">
        </a>
        <span class="header-title">Ecosistemul partenerilor DSU</span>
    </div>
    <div class="header-nav" id="header-nav">
        <!-- Navigation will be handled by Streamlit radio below -->
    </div>
    <div class="header-logos">
        <a href="https://www.uvt.ro/" target="_blank">
            <img src="data:image/png;base64,{uvt_logo}" alt="UVT" style="height: 35px; width: auto; border-radius: 4px; cursor: pointer;">
        </a>
        <a href="https://fsgc.uvt.ro/" target="_blank">
            <img src="data:image/png;base64,{fsgc_logo}" alt="FSGC" style="height: 55px; width: auto; border-radius: 4px; cursor: pointer;">
        </a>
    </div>
</div>
<div class="sticky-header-spacer"></div>
""", unsafe_allow_html=True)

# Hidden radio for page selection (styled to appear in header area)
page = st.radio(
    "Meniu",
    ["Rețea parteneri", "Statistici", "Despre proiect"],
    horizontal=True,
    label_visibility="collapsed",
    key="main_menu"
)

# ---------------------------------
# 4. PAGE: ECOSISTEM
# ---------------------------------

if page == "Rețea parteneri":
    # Inițializare Session State
    if "selected_id" not in st.session_state:
        st.session_state["selected_id"] = None
    if "filter_domains" not in st.session_state:
        st.session_state["filter_domains"] = all_domain_labels
    if "special_filter" not in st.session_state:
        st.session_state["special_filter"] = None
    if "entity_filter" not in st.session_state:
         st.session_state["entity_filter"] = None

    # Layout: Stânga (Controale/Detalii) | Centru (Graf) | Dreapta (Info/Stats)
    col_controls, col_graph, col_stats = st.columns([1.2, 3.0, 1.0], gap="medium")

    # --- PANOU STÂNGA: FILTRE ȘI NAVIGARE ---
    with col_controls:
        # Header dinamic
        if st.session_state["selected_id"]:
            st.markdown("### Detalii partener")
        else:
            st.markdown("### Filtre & Căutare")
        
        # 1. SEARCH BOX (Rămâne mereu vizibil pentru navigare rapidă)
        partner_names = sorted([info["label"] for nid, info in nodes_data.items() 
                               if info["type"] == "Partner" and info.get("parent_id") is None])
        
        def on_search_change():
            selected_name = st.session_state["search_box"]
            found_id = None
            for nid, info in nodes_data.items():
                if info["label"] == selected_name:
                    found_id = nid
                    break
            st.session_state["selected_id"] = found_id

        current_idx = None
        if st.session_state["selected_id"] and st.session_state["selected_id"] in nodes_data:
            node = nodes_data[st.session_state["selected_id"]]
            if node["type"] == "Partner" and node.get("parent_id") is None and node["label"] in partner_names:
                current_idx = partner_names.index(node["label"])

        st.selectbox(
            "Caută partener:", 
            options=partner_names, 
            index=current_idx, 
            key="search_box", 
            on_change=on_search_change, 
            placeholder="Selectează organizație...",
            label_visibility="collapsed"
        )
        
        st.markdown("---")

        selected_id = st.session_state["selected_id"]
        
        # --- LOGICĂ UI: DETALII vs FILTRE ---
        if selected_id and selected_id in nodes_data:
            # === MODUL DETALII (PARTNER CARD) ===
            # Când un partener e selectat, ASCUNDEM filtrele ca să nu aglomerăm
            
            info = nodes_data[selected_id]
            if info["type"] == "Partner":
                badges_html = ""
                if info.get("strategic"): 
                    badges_html += '<span class="badge badge-strategic">Strategic</span>'
                if info.get("ukraine"): 
                    badges_html += '<span class="badge badge-ukraine">Ucraina</span>'
                if info.get("is_fonss_member"): 
                    badges_html += '<span class="badge badge-fonss">Membru FONSS</span>'
                
                if info.get("is_fonss_member"):
                    tags_html = '<span class="tag-domain">Servicii sociale</span>'
                else:
                    my_domains = [nodes_data[t]["label"] for s, t in edges_data if s == selected_id and t in nodes_data]
                    tags_html = "".join([f'<span class="tag-domain">{d}</span>' for d in sorted(set(my_domains))])

                st.markdown(f"""
                <div class="partner-card">
                    <div class="partner-title">{info['label']}</div>
                    <div style="margin-bottom:16px;">{badges_html}</div>
                    <div class="partner-desc">{info['description']}</div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:10px; font-weight:600;">DOMENII DE ACTIVITATE</div>
                    <div>{tags_html}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if selected_id == fonss_id: 
                    st.info("S-au afișat în graf organizațiile membre FONSS.")
            else:
                partners_linked = [nodes_data[s]["label"] for s, t in edges_data if t == selected_id and s in nodes_data]
                st.markdown(f"""
                <div class="partner-card">
                    <div class="partner-title">{info['label']}</div>
                    <div class="partner-desc">Acest domeniu conectează <b>{len(partners_linked)}</b> parteneri DSU.</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Buton mare de întoarcere
            if st.button("← Înapoi la filtre", use_container_width=True):
                st.session_state["selected_id"] = None
                st.rerun()

        else:
            # === MODUL FILTRE (OVERVIEW) ===
            # Aici mutăm TOT ce era în dreapta înainte
            
            # A. FILTRE SPECIALE (STRATEGIC / UCRAINA)
            strategic_count = len([n for n in nodes_data.values() if n.get("strategic")])
            ukraine_count = len([n for n in nodes_data.values() if n.get("ukraine")])
            
            is_strat_active = st.session_state.get("special_filter") == "strategic"
            is_ukr_active = st.session_state.get("special_filter") == "ukraine"

            strat_label = f"{'✓ ' if is_strat_active else ''}Strategic ({strategic_count})"
            ukr_label = f"{'✓ ' if is_ukr_active else ''}Ucraina ({ukraine_count})"
            
            # CSS Specific pentru butoane pills în coloana stângă
            st.markdown("""
            <style>
            /* Resetare stil butoane în acest context */
            div[data-testid="column"] button {
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                # Stil inline pentru butonul Strategic (Portocaliu)
                st.markdown("""
                <style>
                div[data-testid="column"]:nth-of-type(1) div[data-testid="stVerticalBlock"] > div > div > div > button {
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
                    border: none !important;
                    color: white !important;
                    font-weight: 600 !important;
                    border-radius: 20px !important;
                }
                </style>
                """, unsafe_allow_html=True)
                if st.button(strat_label, key="btn_strat_left", use_container_width=True):
                    st.session_state["special_filter"] = None if is_strat_active else "strategic"
                    st.rerun()

            with c_p2:
                # Stil inline pentru butonul Ucraina (Albastru)
                st.markdown("""
                <style>
                div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] > div > div > div > button {
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                    border: none !important;
                    color: white !important;
                    font-weight: 600 !important;
                    border-radius: 20px !important;
                }
                </style>
                """, unsafe_allow_html=True)
                if st.button(ukr_label, key="btn_ukr_left", use_container_width=True):
                    st.session_state["special_filter"] = None if is_ukr_active else "ukraine"
                    st.rerun()

            st.markdown("---")

            # B. FILTRE TIP ENTITATE (LEGENDA INTERACTIVĂ)
            st.markdown("**Tip organizație:**")
            
            # Calculăm numerele pentru legendă
            entity_counts = {}
            for nid, info in nodes_data.items():
                if info["type"] == "Partner" and info.get("parent_id") is None:
                    etype = classify_entity_type(info["label"])
                    entity_counts[etype] = entity_counts.get(etype, 0) + 1

            if st.session_state.get("entity_filter"):
                st.caption(f"Filtru activ: {st.session_state['entity_filter']}")
                if st.button("✕ Șterge filtru tip", key="clear_entity_left", use_container_width=True):
                    st.session_state["entity_filter"] = None
                    st.rerun()

            # CSS pentru lista din stânga (5-column hack pentru aliniere perfectă)
            st.markdown("""
            <style>
            /* Targetăm coloana 4 din rândurile de 5 coloane de mai jos */
            div[data-testid="column"]:nth-of-type(4) button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: #cbd5e1 !important;
                text-align: left !important;
                justify-content: flex-start !important;
                padding: 0px !important;
                font-weight: 400 !important;
            }
            div[data-testid="column"]:nth-of-type(4) button:hover {
                color: #ffffff !important;
                text-decoration: underline !important;
            }
            div[data-testid="column"]:nth-of-type(4) button:focus {
                color: #f87171 !important;
                font-weight: 700 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            for etype, config in ENTITY_TYPES.items():
                count = entity_counts.get(etype, 0)
                color = config['color']
                # Layout compact: Spacer, Dot, Button, Spacer
                c_s1, c_s2, c_dot, c_btn, c_s3 = st.columns([0.01, 0.01, 0.15, 0.8, 0.01])
                
                with c_dot:
                    st.markdown(f'<div style="margin-top: 6px; width: 12px; height: 12px; background-color: {color}; border-radius: 50%;"></div>', unsafe_allow_html=True)
                
                with c_btn:
                    label = f"{etype} ({count})"
                    if st.button(label, key=f"leg_left_{etype}", use_container_width=True):
                        st.session_state["entity_filter"] = None if st.session_state.get("entity_filter") == etype else etype
                        st.rerun()

            st.markdown("---")
            
            # C. FILTRE DOMENII
            st.markdown("**Domenii activitate:**")
            
            c_cl1, c_cl2 = st.columns(2)
            if c_cl1.button("Select all", key="sel_all_dom", use_container_width=True):
                st.session_state["filter_domains"] = all_domain_labels
                st.rerun()
            if c_cl2.button("Clear all", key="clr_all_dom", use_container_width=True):
                st.session_state["filter_domains"] = []
                st.rerun()

            current_selection = set(st.session_state["filter_domains"])
            new_selection = set()
            for group_name, group_domains in DOMAIN_GROUPS.items():
                available_in_group = [d for d in group_domains if d in all_domain_labels]
                if available_in_group:
                    with st.expander(f"{group_name}", expanded=False):
                        sel = st.multiselect(
                            "Selectează:", 
                            options=available_in_group, 
                            default=[d for d in available_in_group if d in current_selection], 
                            key=f"group_{group_name}", 
                            label_visibility="collapsed"
                        )
                        new_selection.update(sel)
            st.session_state["filter_domains"] = list(new_selection)


    # --- PANOU CENTRAL: GRAF ---
    with col_graph:
        # LOGICA GRAFULUI (neschimbată, dar conectată la noile controale)
        final_nodes = []
        final_edges = []
        common_font_style = {"color": "#ffffff", "size": 10, "face": "Inter"}
        hub_font_style = {"color": "#ffffff", "size": 14, "face": "Inter", "bold": True}

        focus_id = st.session_state["selected_id"]
        edges_to_draw = []
        hub_id = None
        leaf_ids = []
        random.seed(42)

        if focus_id:
            # --- VIEW FOCALIZAT (RADIAL) ---
            focus_node = nodes_data.get(focus_id, {})
            is_parent_focus = (focus_id == fonss_id)
            is_child_focus = (focus_node.get("parent_id") is not None)

            if is_parent_focus: 
                hub_id = fonss_id
                for nid, info in nodes_data.items():
                    if info.get("parent_id") == fonss_id:
                        leaf_ids.append(nid)
                        edges_to_draw.append((nid, fonss_id))
            elif is_child_focus: 
                hub_id = focus_node.get("parent_id")
                leaf_ids = [focus_id] 
                edges_to_draw.append((focus_id, hub_id))
            else: 
                hub_id = focus_id
                for s, t in edges_data:
                    if s == hub_id:
                        leaf_ids.append(t)
                        edges_to_draw.append((s, t))
                    elif t == hub_id:
                        leaf_ids.append(s)
                        edges_to_draw.append((s, t))

            # Desenare radială
            info_hub = nodes_data[hub_id]
            final_nodes.append(Node(
                id=hub_id, 
                label=info_hub["label"][:30] + "..." if len(info_hub["label"]) > 30 else info_hub["label"],
                size=40, shape="dot" if info_hub["type"]=="Partner" else "diamond",
                color="#dc2626", font=hub_font_style, x=0, y=0, fixed=True
            ))
            count = len(leaf_ids)
            radius = 300
            for i, nid in enumerate(leaf_ids):
                info = nodes_data[nid]
                angle = 2 * math.pi * i / max(count, 1)
                final_nodes.append(Node(
                    id=nid, 
                    label=info["label"][:25] + "..." if len(info["label"]) > 25 else info["label"],
                    size=22, shape="dot" if info["type"]=="Partner" else "diamond",
                    color="#b91c1c" if info.get("is_fonss_member") else ("#dc2626" if info["type"]=="Domain" else get_entity_color(info["label"])),
                    font=common_font_style, x=radius * math.cos(angle), y=radius * math.sin(angle), fixed=True
                ))
            for s, t in edges_to_draw:
                final_edges.append(Edge(source=s, target=t, color="#dc2626", width=1.5))
            
            config = Config(width="100%", height=900, directed=False, physics=False, hierarchical=False, initialZoom=2.0)

        else:
            # --- VIEW CLUSTERED (FILTRAT) ---
            special_filter = st.session_state.get("special_filter")
            entity_filter = st.session_state.get("entity_filter")

            visible_domain_ids = {nid for nid, info in nodes_data.items()
                                  if info["type"] == "Domain" and info["label"] in st.session_state["filter_domains"]}

            relevant_partners = set()
            active_edges = []

            for s, t in edges_data:
                if t in visible_domain_ids:
                    partner_node = nodes_data[s]
                    if partner_node.get("parent_id") is None:
                        matches_special = True
                        if special_filter == "strategic" and not partner_node.get("strategic"): matches_special = False
                        elif special_filter == "ukraine" and not partner_node.get("ukraine"): matches_special = False
                        
                        matches_entity = True
                        if entity_filter and classify_entity_type(partner_node["label"]) != entity_filter: matches_entity = False

                        if matches_special and matches_entity:
                            relevant_partners.add(s)
                            active_edges.append((s, t))
            
            if special_filter or entity_filter:
                visible_domain_ids &= {t for s, t in active_edges}

            domain_list = list(visible_domain_ids)
            num_domains = len(domain_list)
            spacing = 400 
            cols = math.ceil(math.sqrt(num_domains)) if num_domains > 0 else 1
            rows = math.ceil(num_domains / cols) if num_domains > 0 else 1
            
            for idx, nid in enumerate(domain_list):
                row = idx // cols
                col = idx % cols
                final_nodes.append(Node(
                    id=nid, label=nodes_data[nid]["label"][:20] + "...", size=30, 
                    shape="diamond", color="#dc2626", font=hub_font_style,
                    x=(col - cols/2) * spacing, y=(row - rows/2) * spacing
                ))
            
            for nid in relevant_partners:
                info = nodes_data[nid]
                connected_domains = [t for s, t in active_edges if s == nid]
                if connected_domains:
                    d_idx = domain_list.index(connected_domains[0]) if connected_domains[0] in domain_list else 0
                    base_x = (d_idx % cols - cols/2) * spacing
                    base_y = (d_idx // cols - rows/2) * spacing
                    x, y = base_x + random.uniform(-150, 150), base_y + random.uniform(-150, 150)
                else:
                    x, y = random.uniform(-400, 400), random.uniform(-400, 400)
                
                final_nodes.append(Node(
                    id=nid, label=info["label"][:20] + "...", size=20,
                    shape="dot", color=get_entity_color(info["label"]), font=common_font_style,
                    x=x, y=y
                ))
                 
            for s, t in active_edges:
                final_edges.append(Edge(source=s, target=t, color="rgba(220, 38, 38, 0.2)", width=3))

            config = Config(width="100%", height=900, directed=False, physics=True, initialZoom=1.8, collapsible=False)
        
        return_value = agraph(nodes=final_nodes, edges=final_edges, config=config)
        
        if return_value:
            clicked_id = return_value if isinstance(return_value, str) else (return_value.get("id") or (return_value.get("nodes")[0] if return_value.get("nodes") else None))
            if clicked_id and clicked_id in nodes_data and clicked_id != st.session_state["selected_id"]:
                st.session_state["selected_id"] = clicked_id
                st.rerun()

    # --- PANOU DREAPTA: DOAR STATISTICI & INFO ---
    with col_stats:
        st.markdown("### Statistici rețea")
        total_partners = len([n for n in nodes_data.values() if n["type"] == "Partner" and n.get("parent_id") is None])
        total_domains = len([n for n in nodes_data.values() if n["type"] == "Domain"])
        total_connections = len(edges_data)
        
        st.metric("Total parteneri", total_partners)
        st.metric("Domenii de activitate", total_domains)
        st.metric("Conexiuni", total_connections)

        st.markdown("---")
        
        # AICI am mutat informațiile explicative (statice)
        st.markdown("""
        <div class="info-box">
            <div class="info-title">Cum navighez?</div>
            <div class="info-text">
                Folosește <b>panoul din stânga</b> pentru a filtra partenerii după tip, domeniu sau implicare strategică.<br><br>
                <b>Click pe un nod</b> pentru a vedea detaliile complete ale partenerului.
            </div>
        </div>

        <div class="info-box" style="border-left-color: #94a3b8;">
            <div class="info-title">Despre hartă</div>
            <div class="info-text">
                Vizualizarea grupează partenerii în funcție de domeniul principal de colaborare cu DSU.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------
# 5. PAGE: STATISTICI
# ---------------------------------

elif page == "Statistici":
    st.markdown("### Tablou de bord operațional - anul 2024")
    
    st.markdown("""
    <div class="info-box">
        <div class="info-title">Despre aceste date</div>
        <div class="info-text">
            Această secțiune prezintă o sinteză a activității operaționale DSU pentru anul 2024. 
            Datele includ volumul total de intervenții, tipologia urgențelor gestionate, 
            măsurile de control aplicate și o analiză a riscurilor identificate la nivel național.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_growth = pd.DataFrame({
        "Year": ["2023", "2024"],
        "Total Interventions": [554262, 590891],
        "Growth": [0, 9.44]
    })
    
    df_categories = pd.DataFrame({
        "Type": ["Urgențe medicale", "Incendii & salvare", "Accidente rutiere", "Înec & apă", "Substanțe periculoase"],
        "Count": [265901, 118178, 88634, 47271, 29545]
    })
    
    df_enforcement = pd.DataFrame({
        "Measure": ["Avertismente", "Amenzi (contravenții)", "Suspensii"],
        "Cases": [123555, 21055, 102],
        "Value_RON": [0, 186500000, 0]
    })
    
    df_risks = pd.DataFrame({
        "Risk": ["Cutremure", "Inundații", "Alunecare teren", "Avalanșe", "Tornadă"],
        "Score": [9, 12, 1, 1, 0],
        "Severity": ["Very High", "High", "High", "High", "High"]
    })

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Intervenții totale 2024", "590.891", "+9.44%", help="Comparativ cu 2023 (554.262)")
    k2.metric("Medie zilnică", "1.618", "+101", help="Intervenții pe zi")
    k3.metric("Măsuri coercitive", "144.712", "Amenzi: 14.5%", help="Majoritatea sunt avertismente (85%)")
    k4.metric("Valoare amenzi (RON)", "186.5 M", help="Total amenzi aplicate în 2024")

    st.divider()

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### Distribuția tipurilor de intervenție")
        fig_pie = px.pie(
            df_categories, 
            values="Count", 
            names="Type",
            hole=0.5,
            color_discrete_sequence=["#dc2626", "#991b1b", "#b91c1c", "#7f1d1d", "#450a0a"]
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#e2e8f0", size=13),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("#### Trend anual intervenții")
        fig_bar = px.bar(
            df_growth, 
            x="Year", 
            y="Total Interventions", 
            text="Total Interventions",
            color="Year",
            color_discrete_map={"2023": "#64748b", "2024": "#dc2626"}
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#e2e8f0"),
            showlegend=False,
            yaxis_title="Intervenții",
            xaxis_title=""
        )
        fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    c3, c4 = st.columns(2)
    
    with c3:
        st.markdown("#### Activitate de control")
        fig_enf = px.bar(
            df_enforcement,
            x="Measure",
            y="Cases",
            color="Measure",
            text="Cases",
            color_discrete_map={
                "Avertismente": "#10b981",
                "Amenzi (contravenții)": "#dc2626",
                "Suspensii": "#450a0a"
            }
        )
        fig_enf.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#e2e8f0"),
            showlegend=False,
            yaxis_title="Număr cazuri",
            xaxis_title=""
        )
        fig_enf.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_enf, use_container_width=True)
        
    with c4:
        st.markdown("#### Analiza riscurilor identificate")
        fig_risk = px.scatter(
            df_risks,
            x="Risk",
            y="Score",
            size="Score",
            color="Severity",
            color_discrete_map={"Very High": "#dc2626", "High": "#991b1b"},
            size_max=50
        )
        fig_risk.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#e2e8f0"),
            yaxis_title="Scor risc",
            xaxis_title=""
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# ---------------------------------
# 6. PAGE: DESPRE PROIECT
# ---------------------------------

elif page == "Despre proiect":
    st.markdown("### Despre acest proiect")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="info-title" style="font-size: 1.3rem; margin-bottom: 16px;">Ecosistemului de parteneriate DSU</div>
            <div class="info-text" style="font-size: 1rem; line-height: 1.8;">
                Acest proiect oferă o reprezentare vizuală interactivă a rețelei de parteneriate dintre
                Departamentul pentru Situații de Urgență (DSU) și diverse organizații din România.
                <br><br>
                Scopul principal este de a facilita înțelegerea complexității și diversității colaborărilor
                care susțin capacitatea națională de răspuns la situații de urgență.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="info-title" style="font-size: 1.1rem; margin-bottom: 12px;">Obiective</div>
            <div class="info-text">
                <ul style="margin: 0; padding-left: 20px; line-height: 2;">
                    <li>Cartografierea parteneriatelor formale ale DSU</li>
                    <li>Identificarea domeniilor de activitate și a sinergiilor</li>
                    <li>Evidențierea partenerilor strategici și a celor implicați în criza din Ucraina</li>
                    <li>Oferirea unui instrument de analiză pentru decidenți și cercetători</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="info-title" style="font-size: 1.1rem; margin-bottom: 12px;">Metodologie</div>
            <div class="info-text" style="line-height: 1.8;">
                Datele au fost colectate din surse oficiale și documente publice.
                Fiecare parteneriat a fost clasificat pe domenii de activitate și caracterizat
                în funcție de natura colaborării (strategic, implicare în criza ucraineană etc.).
                <br><br>
                Vizualizarea folosește un graf interactiv care permite explorarea conexiunilor
                dintre parteneri și domeniile lor de activitate.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="partner-card">
            <div class="info-title" style="font-size: 1.1rem; margin-bottom: 16px;">Echipa proiectului</div>
            <div class="info-text" style="line-height: 2;">
                <b>Universitatea de Vest din Timișoara</b><br>
                Facultatea de Științe ale Guvernării și Comunicării
                <br><br>
                <b>Coordonator proiect:</b><br>
                Lect. univ. dr. Silvia Fierăscu
                <br><br>
                <b>Proiect realizat de:</b><br>
                Bogdan Doboșeru<br>
                Laurențiu Florea<br>
                Andrei Galescu<br>
                lexandru Poliac-Seres<br>
                Briana Toader<br>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="info-title" style="font-size: 1.1rem; margin-bottom: 12px;">Contact</div>
            <div class="info-text">
                Pentru întrebări sau sugestii:<br>
                <a href="mailto:contact@example.com" style="color: #dc2626;">contact@example.com</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="info-title" style="font-size: 1.1rem; margin-bottom: 12px;">Versiune</div>
            <div class="info-text">
                v1.0 - Ianuarie 2025<br>
                <span style="font-size: 0.8rem; color: #64748b;">Ultima actualizare a datelor</span>
            </div>
        </div>
        """, unsafe_allow_html=True)