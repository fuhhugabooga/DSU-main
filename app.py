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
    initial_sidebar_state="expanded"
)

# ---------------------------------
# 1. MODERN CSS STYLING
# ---------------------------------

st.markdown(
    """
    <style>
    /* =========================================
       GLOBAL RESET & BASE STYLES
       ========================================= */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a0f0f 100%);
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-top: 0 !important;
    }

    /* Add padding for Statistici and Despre pages */
    .page-with-padding .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }

    @media (max-width: 768px) {
        .page-with-padding .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Hide Streamlit default elements */
    header[data-testid="stHeader"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .main .block-container {
        padding-top: 0 !important;
    }

    /* Sidebar styling for network page */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 26, 0.98) 0%, rgba(26, 15, 15, 0.98) 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
        padding-top: 60px !important;
    }

    /* Sidebar button styling */
    section[data-testid="stSidebar"] button {
        font-size: 0.8rem !important;
        padding: 10px 12px !important;
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        align-items: center !important;
    }

    section[data-testid="stSidebar"] button p {
        text-align: center !important;
        width: 100% !important;
    }

    /* Sidebar expander styling */
    section[data-testid="stSidebar"] details {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        font-size: 0.8rem !important;
        padding: 6px 10px !important;
    }

    /* =========================================
       STICKY HEADER - DESKTOP & MOBILE
       ========================================= */
    .sticky-header-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: linear-gradient(135deg, #0a0e1a 0%, #1a0f0f 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        padding: 8px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }

    .sticky-header-spacer {
        height: 60px;
        flex-shrink: 0;
    }

    .header-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-shrink: 0;
    }

    .header-logo img {
        height: 40px;
        width: auto;
        border-radius: 4px;
    }

    .header-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .header-logos {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }

    .header-logos img {
        height: 32px;
        width: auto;
        border-radius: 4px;
    }

    /* Navigation - scrollable on mobile */
    .header-nav-wrapper {
        flex: 1;
        display: flex;
        justify-content: center;
        overflow-x: auto;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        -ms-overflow-style: none;
        padding: 4px 0;
    }

    .header-nav-wrapper::-webkit-scrollbar {
        display: none;
    }

    /* Radio buttons styling */
    .stRadio {
        position: fixed !important;
        top: 10px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 9999999 !important;
        max-width: calc(100vw - 300px);
    }

    div[role="radiogroup"] {
        flex-direction: row;
        gap: 6px;
        justify-content: center;
        background: transparent;
        flex-wrap: nowrap;
        white-space: nowrap;
    }

    div[role="radiogroup"] label {
        background: transparent !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 6px 14px !important;
        transition: all 0.3s ease;
        cursor: pointer;
        white-space: nowrap;
        flex-shrink: 0;
    }

    div[role="radiogroup"] label:hover {
        background: rgba(220, 38, 38, 0.1) !important;
        border-color: rgba(220, 38, 38, 0.5) !important;
    }

    div[role="radiogroup"] label p {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        margin: 0 !important;
        white-space: nowrap;
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

    /* =========================================
       MOBILE RESPONSIVE HEADER
       ========================================= */
    @media (max-width: 768px) {
        .sticky-header-container {
            padding: 6px 10px;
            flex-wrap: wrap;
            gap: 8px;
        }

        .header-title {
            display: none;
        }

        .header-logo img {
            height: 35px;
        }

        .header-logos {
            gap: 6px;
        }

        .header-logos img {
            height: 28px;
        }

        .stRadio {
            position: relative !important;
            top: auto !important;
            left: auto !important;
            transform: none !important;
            width: 100% !important;
            max-width: 100% !important;
            order: 3;
            margin-top: 4px;
        }

        div[role="radiogroup"] {
            justify-content: center;
            gap: 4px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding-bottom: 4px;
        }

        div[role="radiogroup"] label {
            padding: 5px 10px !important;
        }

        div[role="radiogroup"] label p {
            font-size: 0.75rem !important;
        }

        .sticky-header-spacer {
            height: 90px;
        }
    }

    @media (max-width: 480px) {
        .header-logos img:not(:first-child) {
            display: none;
        }

        .sticky-header-spacer {
            height: 85px;
        }
    }

    /* =========================================
       STATS OVERLAY PANEL
       ========================================= */
    .stats-overlay {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 200px;
        background: rgba(10, 14, 26, 0.92);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 14px;
        z-index: 1000;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    .stats-overlay h4 {
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stat-card {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(153, 27, 27, 0.08) 100%);
        border: 1px solid rgba(220, 38, 38, 0.2);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 8px;
        text-align: center;
    }

    .stat-card:last-of-type {
        margin-bottom: 0;
    }

    .stat-label {
        color: #94a3b8;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 4px;
    }

    .stat-value {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #dc2626 0%, #f87171 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .legend-section {
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .legend-title {
        font-size: 0.65rem;
        color: #94a3b8;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
    }

    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .legend-diamond {
        width: 10px;
        height: 10px;
        transform: rotate(45deg);
        flex-shrink: 0;
    }

    .legend-text {
        font-size: 0.72rem;
        color: #cbd5e1;
    }

    /* Mobile Stats Overlay Adjustment */
    @media (max-width: 768px) {
        .stats-overlay {
            position: relative !important;
            top: auto !important;
            bottom: auto !important;
            right: auto !important;
            left: auto !important;
            width: 100% !important;
            max-width: none !important;
            margin: 10px 0 !important;
            border-radius: 12px !important;
        }
    }

    /* =========================================
       GRAPH CONTAINER - FULL SCREEN
       ========================================= */
    iframe {
        border: none !important;
    }

    .element-container:has(iframe) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stVerticalBlock"] > div:has(iframe) {
        margin-bottom: 0 !important;
    }

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

    /* Graph fills available space */
    .graph-container iframe {
        width: 100% !important;
        height: calc(100vh - 60px) !important;
        min-height: 500px !important;
    }

    @media (max-width: 768px) {
        .graph-container iframe {
            height: 60vh !important;
            min-height: 350px !important;
        }

        /* Touch-friendly improvements */
        .stApp iframe {
            touch-action: pan-x pan-y pinch-zoom !important;
        }
    }
    
    /* CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.15);
        border-color: rgba(220, 38, 38, 0.3);
    }

    .partner-card {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(153, 27, 27, 0.1) 100%);
        border: 1px solid rgba(220, 38, 38, 0.3);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.1);
    }

    .partner-title {
        font-size: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(220, 38, 38, 0.2);
        word-wrap: break-word;
    }

    .partner-desc {
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    /* INFO BOXES - Compact */
    .info-box {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.08) 0%, rgba(153, 27, 27, 0.08) 100%);
        border-left: 3px solid #dc2626;
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
    }

    .info-title {
        font-weight: 700;
        color: #f87171;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }

    .info-text {
        color: #cbd5e1;
        font-size: 0.8rem;
        line-height: 1.4;
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
    
    /* BADGES - Compact */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .badge-strategic {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff;
    }

    .badge-ukraine {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff;
    }

    .badge-fonss {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
        color: #ffffff;
    }

    .tag-domain {
        display: inline-block;
        background: rgba(220, 38, 38, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(220, 38, 38, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        margin-right: 4px;
        margin-bottom: 4px;
        font-weight: 500;
    }
    
    /* SEARCH BOX */
    div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    /* BUTTONS - Compact */
    .stButton > button {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.8rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #94a3b8;
    }

    /* EXPANDER - Compact */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        color: #cbd5e1 !important;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 12px !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(220, 38, 38, 0.08);
    }

    details[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        margin-bottom: 6px;
    }

    /* SECTION HEADERS - Compact */
    h3 {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 12px;
        font-size: 1rem;
    }
    
    h4 {
        color: #e2e8f0;
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    /* DIVIDER */
    hr {
        border-color: rgba(255, 255, 255, 0.08);
        margin: 12px 0;
    }

    /* FILTER SECTION STYLES */
    .filter-section-title {
        color: #f87171;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        margin-top: 12px;
    }

    .filter-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #cbd5e1;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 6px;
        width: 100%;
    }

    .filter-btn:hover {
        background: rgba(220, 38, 38, 0.1);
        border-color: rgba(220, 38, 38, 0.3);
    }

    .filter-btn.active {
        background: rgba(220, 38, 38, 0.2);
        border-color: rgba(220, 38, 38, 0.5);
        color: #fca5a5;
    }

    .filter-btn-icon {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* Multiselect compact */
    div[data-baseweb="select"] {
        font-size: 0.8rem !important;
    }

    /* Hide streamlit elements in network page for cleaner look */
    .network-page div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
    }

    /* Touch-friendly for mobile */
    @media (max-width: 768px) {
        .filter-btn {
            padding: 10px 14px;
            font-size: 0.85rem;
        }

        .stButton > button {
            padding: 10px 18px;
            font-size: 0.85rem;
        }
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
# 4. PAGE: ECOSISTEM (REFACTORED - IMMERSIVE LAYOUT)
# ---------------------------------

if page == "Rețea parteneri":
    # Initialize session state
    if "selected_id" not in st.session_state:
        st.session_state["selected_id"] = None
    if "filter_domains" not in st.session_state:
        st.session_state["filter_domains"] = all_domain_labels
    if "special_filter" not in st.session_state:
        st.session_state["special_filter"] = None
    if "entity_filter" not in st.session_state:
        st.session_state["entity_filter"] = None
    if "sidebar_open" not in st.session_state:
        st.session_state["sidebar_open"] = False

    # Calculate statistics upfront
    total_partners = len([n for n in nodes_data.values() if n["type"] == "Partner" and n.get("parent_id") is None])
    total_domains = len([n for n in nodes_data.values() if n["type"] == "Domain"])
    total_connections = len(edges_data)
    strategic_count = len([n for n in nodes_data.values() if n.get("strategic")])
    ukraine_count = len([n for n in nodes_data.values() if n.get("ukraine")])

    entity_counts = {}
    for nid, info in nodes_data.items():
        if info["type"] == "Partner" and info.get("parent_id") is None:
            etype = classify_entity_type(info["label"])
            entity_counts[etype] = entity_counts.get(etype, 0) + 1

    partner_names = sorted([info["label"] for nid, info in nodes_data.items()
                           if info["type"] == "Partner" and info.get("parent_id") is None])

    # Render Stats and Legend Overlay (combined HTML - positioned fixed)
    st.markdown(f"""
    <div class="stats-overlay">
        <h4>Statistici Rețea</h4>
        <div class="stat-card">
            <div class="stat-label">Parteneri</div>
            <div class="stat-value">{total_partners}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Domenii</div>
            <div class="stat-value">{total_domains}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Conexiuni</div>
            <div class="stat-value">{total_connections}</div>
        </div>
        <div class="legend-section">
            <div class="legend-title">Legendă</div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #8b5cf6;"></div>
                <span class="legend-text">Universitate</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #10b981;"></div>
                <span class="legend-text">ONG</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #3b82f6;"></div>
                <span class="legend-text">Instituție de stat</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #f59e0b;"></div>
                <span class="legend-text">Companie privată</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #ec4899;"></div>
                <span class="legend-text">Media</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #14b8a6;"></div>
                <span class="legend-text">Organizație profesională</span>
            </div>
            <div class="legend-item">
                <div class="legend-diamond" style="background: #dc2626;"></div>
                <span class="legend-text">Domeniu de activitate</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Use Streamlit sidebar for filters
    with st.sidebar:
        # ============================================
        # INFO SECTION - App description at top
        # ============================================
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 16px;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                Rețeaua de Parteneri DSU
            </div>
            <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 12px;">
                Vizualizare interactivă a parteneriatelor dintre Departamentul pentru Situații de Urgență
                și organizațiile care contribuie la răspunsul național în caz de urgență.
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; line-height: 1.6;">
                <b>Ce puteți afla?</b><br>
                • Cine sunt partenerii DSU<br>
                • În ce domenii activează<br>
                • Care sunt partenerii strategici<br>
                • Cine ajută în criza din Ucraina
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box" style="margin-bottom: 16px;">
            <div class="info-title">Cum navigați</div>
            <div class="info-text">
                <b>Click</b> pe un nod pentru detalii<br>
                <b>Scroll</b> pentru zoom<br>
                <b>Drag</b> pentru a muta vizualizarea
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ============================================
        # SEARCH SECTION
        # ============================================
        st.markdown('<div class="filter-section-title">Caută partener</div>', unsafe_allow_html=True)

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

        # ============================================
        # ENTITY TYPE FILTER - Uniform buttons
        # ============================================
        st.markdown('<div class="filter-section-title">Sortează după tip</div>', unsafe_allow_html=True)

        if st.session_state.get("entity_filter"):
            if st.button("✕ Resetează filtrul", key="reset_entity", type="secondary", use_container_width=True):
                st.session_state["entity_filter"] = None
                st.rerun()

        for etype, config in ENTITY_TYPES.items():
            count = entity_counts.get(etype, 0)
            is_active = st.session_state.get("entity_filter") == etype
            btn_type = "primary" if is_active else "secondary"

            if st.button(f"{etype} ({count})", key=f"etype_{etype}", type=btn_type, use_container_width=True):
                if is_active:
                    st.session_state["entity_filter"] = None
                else:
                    st.session_state["entity_filter"] = etype
                    st.session_state["selected_id"] = None
                st.rerun()

        st.markdown("---")

        # ============================================
        # DOMAIN FILTER
        # ============================================
        st.markdown('<div class="filter-section-title">Sortează după domeniu</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("Toate", use_container_width=True, key="sel_all"):
            st.session_state["filter_domains"] = all_domain_labels
            st.rerun()
        if c2.button("Nimic", use_container_width=True, key="sel_none"):
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

        st.markdown("---")

        # ============================================
        # SPECIAL FILTERS - Strategic & Ukraine
        # ============================================
        st.markdown('<div class="filter-section-title">Parteneri speciali</div>', unsafe_allow_html=True)

        is_strat_active = st.session_state.get("special_filter") == "strategic"
        is_ukr_active = st.session_state.get("special_filter") == "ukraine"

        strat_type = "primary" if is_strat_active else "secondary"
        if st.button(f"⭐ Parteneri strategici ({strategic_count})", key="btn_strategic", type=strat_type, use_container_width=True):
            if is_strat_active:
                st.session_state["special_filter"] = None
            else:
                st.session_state["special_filter"] = "strategic"
                st.session_state["selected_id"] = None
            st.rerun()

        ukr_type = "primary" if is_ukr_active else "secondary"
        if st.button(f"🇺🇦 Sprijin Ucraina ({ukraine_count})", key="btn_ukraine", type=ukr_type, use_container_width=True):
            if is_ukr_active:
                st.session_state["special_filter"] = None
            else:
                st.session_state["special_filter"] = "ukraine"
                st.session_state["selected_id"] = None
            st.rerun()

        st.markdown("---")

        # ============================================
        # SELECTED PARTNER INFO
        # ============================================
        selected_id = st.session_state["selected_id"]

        if selected_id and selected_id in nodes_data:
            st.markdown('<div class="filter-section-title">Partener selectat</div>', unsafe_allow_html=True)
            info = nodes_data[selected_id]

            if info["type"] == "Partner":
                badges_html = ""
                if info.get("strategic"):
                    badges_html += '<span class="badge badge-strategic">Strategic</span>'
                if info.get("ukraine"):
                    badges_html += '<span class="badge badge-ukraine">Ucraina</span>'
                if info.get("is_fonss_member"):
                    badges_html += '<span class="badge badge-fonss">FONSS</span>'

                if info.get("is_fonss_member"):
                    tags_html = '<span class="tag-domain">Servicii sociale</span>'
                else:
                    my_domains = [nodes_data[t]["label"] for s, t in edges_data if s == selected_id and t in nodes_data]
                    tags_html = "".join([f'<span class="tag-domain">{d}</span>' for d in sorted(set(my_domains))])

                # Get entity type for display
                entity_type = classify_entity_type(info['label'])

                st.markdown(f"""
                <div class="partner-card">
                    <div class="partner-title">{info['label']}</div>
                    <div style="margin-bottom: 8px;">
                        <span style="font-size: 0.7rem; color: #94a3b8; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px;">{entity_type}</span>
                    </div>
                    <div style="margin-bottom: 8px;">{badges_html}</div>
                    <div class="partner-desc">{info['description']}</div>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 12px; margin-bottom: 6px; font-weight: 600;">DOMENII DE ACTIVITATE</div>
                    <div>{tags_html}</div>
                </div>
                """, unsafe_allow_html=True)

                if selected_id == fonss_id:
                    st.info("Se afișează organizațiile membre FONSS.")
            else:
                partners_linked = [nodes_data[s]["label"] for s, t in edges_data if t == selected_id and s in nodes_data]
                st.markdown(f"""
                <div class="partner-card">
                    <div class="partner-title">{info['label']}</div>
                    <div class="partner-desc">Acest domeniu conectează <b>{len(partners_linked)}</b> parteneri.</div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("← Înapoi la rețea", use_container_width=True, key="back_btn"):
                st.session_state["selected_id"] = None
                st.rerun()

        # ============================================
        # EXPORT SECTION
        # ============================================
        st.markdown("---")
        st.markdown('<div class="filter-section-title">Exportă date</div>', unsafe_allow_html=True)

        # Get filtered partners based on current filters
        special_filter = st.session_state.get("special_filter")
        entity_filter = st.session_state.get("entity_filter")
        domain_filter = st.session_state.get("filter_domains", all_domain_labels)

        filtered_partners = []
        for nid, info in nodes_data.items():
            if info["type"] == "Partner" and info.get("parent_id") is None:
                # Check special filter
                if special_filter == "strategic" and not info.get("strategic"):
                    continue
                if special_filter == "ukraine" and not info.get("ukraine"):
                    continue

                # Check entity filter
                if entity_filter:
                    if classify_entity_type(info["label"]) != entity_filter:
                        continue

                # Check domain filter
                partner_domains = [nodes_data[t]["label"] for s, t in edges_data if s == nid and t in nodes_data and nodes_data[t]["type"] == "Domain"]
                if domain_filter and not any(d in domain_filter for d in partner_domains):
                    continue

                filtered_partners.append({
                    "Nume": info["label"],
                    "Tip": classify_entity_type(info["label"]),
                    "Strategic": "Da" if info.get("strategic") else "Nu",
                    "Sprijin Ucraina": "Da" if info.get("ukraine") else "Nu",
                    "Domenii": ", ".join(partner_domains),
                    "Descriere": info.get("description", "")
                })

        # Create DataFrame for export
        if filtered_partners:
            export_df = pd.DataFrame(filtered_partners)

            # CSV Export
            csv_data = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Descarcă CSV ({len(filtered_partners)} parteneri)",
                data=csv_data,
                file_name="parteneri_dsu.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.caption("Descarcă lista partenerilor afișați în format CSV.")
        else:
            st.caption("Niciun partener de exportat cu filtrele curente.")

    # Main content - Full width graph (outside sidebar)
    final_nodes = []
    final_edges = []

    # Font styles
    common_font_style = {"color": "#ffffff", "size": 10, "face": "Inter"}
    hub_font_style = {"color": "#ffffff", "size": 14, "face": "Inter", "bold": True}

    focus_id = st.session_state["selected_id"]
    edges_to_draw = []
    hub_id = None
    leaf_ids = []
    random.seed(42)

    if focus_id:
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

    if hub_id:
        # RADIAL FOCUSED VIEW
        info_hub = nodes_data[hub_id]
        final_nodes.append(Node(
            id=hub_id,
            label=info_hub["label"][:30] + "..." if len(info_hub["label"]) > 30 else info_hub["label"],
            size=40,
            shape="dot" if info_hub["type"] == "Partner" else "diamond",
            color="#dc2626",
            font=hub_font_style,
            x=0, y=0, fixed=True
        ))

        count = len(leaf_ids)
        radius = 300

        for i, nid in enumerate(leaf_ids):
            info = nodes_data[nid]
            angle = 2 * math.pi * i / max(count, 1)
            pos_x = radius * math.cos(angle)
            pos_y = radius * math.sin(angle)

            if info["type"] == "Domain":
                color = "#dc2626"
            elif info.get("is_fonss_member"):
                color = "#b91c1c"
            else:
                color = get_entity_color(info["label"])

            label = info["label"][:25] + "..." if len(info["label"]) > 25 else info["label"]

            final_nodes.append(Node(
                id=nid, label=label, size=22,
                shape="dot" if info["type"] == "Partner" else "diamond",
                color=color, font=common_font_style,
                x=pos_x, y=pos_y, fixed=True
            ))

        for s, t in edges_to_draw:
            final_edges.append(Edge(
                source=s, target=t,
                color="#dc2626",
                width=1.5
            ))

        config = Config(
            width="100%",
            height=900,
            directed=False,
            physics=False,
            hierarchical=False
        )

    else:
        # CLUSTERED VIEW BY DOMAIN
        special_filter = st.session_state.get("special_filter")
        entity_filter = st.session_state.get("entity_filter")

        visible_domain_ids = {nid for nid, info in nodes_data.items()
                              if info["type"] == "Domain"
                              and info["label"] in st.session_state["filter_domains"]}

        relevant_partners = set()
        active_edges = []

        for s, t in edges_data:
            if t in visible_domain_ids:
                partner_node = nodes_data[s]

                if partner_node.get("parent_id") is None:
                    matches_special = True
                    matches_entity = True

                    if special_filter == "strategic" and not partner_node.get("strategic"):
                        matches_special = False
                    elif special_filter == "ukraine" and not partner_node.get("ukraine"):
                        matches_special = False

                    if entity_filter:
                        current_type = classify_entity_type(partner_node["label"])
                        if current_type != entity_filter:
                            matches_entity = False

                    if matches_special and matches_entity:
                        relevant_partners.add(s)
                        active_edges.append((s, t))

        if special_filter or entity_filter:
            connected_domain_ids = {t for s, t in active_edges}
            visible_domain_ids = visible_domain_ids & connected_domain_ids

        domain_list = list(visible_domain_ids)
        num_domains = len(domain_list)
        cols = 1
        spacing = 400

        if num_domains > 0:
            cols = math.ceil(math.sqrt(num_domains))
            rows = math.ceil(num_domains / cols)

            for idx, nid in enumerate(domain_list):
                row = idx // cols
                col = idx % cols
                x = (col - cols / 2) * spacing
                y = (row - rows / 2) * spacing

                label = nodes_data[nid]["label"][:20] + "..." if len(nodes_data[nid]["label"]) > 20 else nodes_data[nid]["label"]

                final_nodes.append(Node(
                    id=nid, label=label, size=30,
                    shape="diamond", color="#dc2626", font=hub_font_style,
                    x=x, y=y
                ))

        for nid in relevant_partners:
            info = nodes_data[nid]
            color = get_entity_color(info["label"])

            connected_domains = [t for s, t in active_edges if s == nid]
            if connected_domains and domain_list:
                domain_idx = domain_list.index(connected_domains[0]) if connected_domains[0] in domain_list else 0
                row = domain_idx // cols
                col = domain_idx % cols
                base_x = (col - cols / 2) * spacing
                base_y = (row - rows / 2) * spacing
                x = base_x + random.uniform(-150, 150)
                y = base_y + random.uniform(-150, 150)
            else:
                x = random.uniform(-400, 400)
                y = random.uniform(-400, 400)

            label = info["label"][:20] + "..." if len(info["label"]) > 20 else info["label"]

            final_nodes.append(Node(
                id=nid, label=label, size=20,
                shape="dot", color=color, font=common_font_style,
                x=x, y=y
            ))

        for s, t in active_edges:
            final_edges.append(Edge(
                source=s, target=t,
                color="rgba(220, 38, 38, 0.2)",
                width=3
            ))

        config = Config(
            width="100%",
            height=900,
            directed=False,
            physics=True,
            hierarchical=False
        )

    # Render the graph
    return_value = agraph(nodes=final_nodes, edges=final_edges, config=config)

    # Handle clicking on nodes
    if return_value:
        clicked_id = None
        if isinstance(return_value, str):
            clicked_id = return_value
        elif isinstance(return_value, dict):
            if "id" in return_value:
                clicked_id = return_value["id"]
            elif "nodes" in return_value and len(return_value["nodes"]) > 0:
                clicked_id = return_value["nodes"][0]

        if clicked_id and clicked_id in nodes_data and clicked_id != st.session_state["selected_id"]:
            st.session_state["selected_id"] = clicked_id
            st.rerun()

# ---------------------------------
# 5. PAGINA: STATISTICI (V2.0 - REDESIGN)
# ---------------------------------

elif page == "Statistici":
    # Add padding class for this page
    st.markdown('<style>.stApp .main .block-container { padding-left: 2rem !important; padding-right: 2rem !important; max-width: 1400px !important; margin: 0 auto !important; }</style>', unsafe_allow_html=True)

    st.markdown("### DSU în cifre")
    st.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 5px solid #dc2626; margin-bottom: 25px;">
        Date în curs de prelucrare. Ultimele date disponibile sunt din 2024
    </div>
    """, unsafe_allow_html=True)
    
    # --- 1. FUNCTIE INCARCARE DATE ---
    @st.cache_data
    def load_all_stats():
        data = {}
        files = {
            "interv": "data/interventii_ambulanta.csv",
            "apeluri": "data/apeluri_urgenta.csv",
            "timp": "data/timp_raspuns.csv",
            "igsu": "data/situatii_igsu.csv",
            "risc": "data/categorii_risc.csv",
            "zbor": "data/ore_zbor.csv",
            "upu": "data/prezentari_upu.csv",
            "instruire": "data/instruire_persoane.csv",
            "protocoale": "data/protocoale.csv",
            "actiuni": "data/tipuri_actiuni.csv",
            "expertiza": "data/arii_expertiza.csv"
        }
        
        for key, path in files.items():
            try:
                df = pd.read_csv(path)
                df.columns = [c.strip() for c in df.columns] 
                data[key] = df
            except Exception:
                data[key] = None
        return data

    D = load_all_stats()
    
    # --- 2. CONFIGURARE HARTA ROMANIA ---
    @st.cache_data
    def get_romania_geojson():
        # URL stabil fără diacritice în proprietățile numelor
        return "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/romania.geojson"

    # Mapare COMPLETĂ și FĂRĂ DIACRITICE pentru a se potrivi cu GeoJSON-ul
    isu_to_judet = {
        "AB": "Alba", "AR": "Arad", "AG": "Arges", "BC": "Bacau", "BH": "Bihor", 
        "BN": "Bistrita-Nasaud", "BT": "Botosani", "BV": "Brasov", "BR": "Braila", "BZ": "Buzau",
        "CS": "Caras-Severin", "CL": "Calarasi", "CJ": "Cluj", "CT": "Constanta", "CV": "Covasna",
        "DB": "Dambovita", "DJ": "Dolj", "GL": "Galati", "GR": "Giurgiu", "GJ": "Gorj",
        "HR": "Harghita", "HD": "Hunedoara", "IL": "Ialomita", "IS": "Iasi", "IF": "Ilfov",
        "MM": "Maramures", "MH": "Mehedinti", "MS": "Mures", "NT": "Neamt", "OT": "Olt",
        "PH": "Prahova", "SM": "Satu Mare", "SJ": "Salaj", "SB": "Sibiu", "SV": "Suceava",
        "TR": "Teleorman", "TM": "Timis", "TL": "Tulcea", "VS": "Vaslui", "VL": "Valcea",
        "VN": "Vrancea", "B": "Bucuresti", "BIF": "Bucuresti"
    }

    toate_judetele = sorted(list(set(isu_to_judet.values())))

    if D["interv"] is None:
        st.error("Eroare: Nu s-au găsit fișierele de date. Verifică folderul /data.")
    else:
        # --- MENIU TAB-URI ---
        tab1, tab2, tab3 = st.tabs(["Operațional și urgențe", "Medical și aviație", "Prevenire și parteneri"])

        # ==========================================
        # TAB 1: OPERAȚIONAL
        # ==========================================
        with tab1:
            st.markdown("#### Indicatori de performanță operațională")
            st.markdown("""
            <span style='font-size:0.9rem; color:#cbd5e1'>
            Această secțiune monitorizează volumul total de activitate. 
            Comparăm numărul de apeluri primite la 112 cu numărul de intervenții reale efectuate de echipaje (Ambulanță, SMURD, Pompieri).
            </span><br><br>
            """, unsafe_allow_html=True)

            latest_year = D["interv"]['An'].max()
            curr_interv = D["interv"].loc[D["interv"]['An'] == latest_year, 'Interventii'].values[0]
            
            last_call_year = D["apeluri"]['An'].max()
            curr_apel = D["apeluri"].loc[D["apeluri"]['An'] == last_call_year, 'Apeluri'].values[0]
            
            curr_time = D["timp"].loc[D["timp"]['An'] == D["timp"]['An'].max(), 'Minute'].values[0]

            k1, k2, k3, k4 = st.columns(4)
            k1.metric(f"Total Intervenții ({latest_year})", f"{curr_interv:,.0f}", help="Numărul total de misiuni executate de serviciile de urgență.")
            k2.metric(f"Apeluri 112 ({last_call_year})", f"{curr_apel:,.0f}", help="Apeluri de urgență recepționate în sistemul SNUAU.")
            k3.metric("Timp mediu de răspuns", f"{curr_time} min", help="Timpul mediu scurs de la apel până la sosirea echipajului.")
            k4.metric("Medie zilnică intervenții", f"{int(curr_interv/365):,.0f}", help="Media misiunilor de salvare efectuate în fiecare zi la nivel național.")
            
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Cerere vs. răspuns")
                st.markdown("<div style='margin-bottom:10px; font-size:0.85rem; color:#94a3b8;'>Evoluția comparativă a apelurilor de urgență (cererea cetățenilor) față de intervențiile efective (capacitatea de răspuns) pe ultimii 10 ani.</div>", unsafe_allow_html=True)
                
                fig_main = go.Figure()
                fig_main.add_trace(go.Scatter(x=D["interv"]['An'], y=D["interv"]['Interventii'], name='Intervenții Reale', line=dict(color='#dc2626', width=3), mode='lines+markers'))
                fig_main.add_trace(go.Scatter(x=D["apeluri"]['An'], y=D["apeluri"]['Apeluri'], name='Apeluri 112', line=dict(color='#3b82f6', width=3), mode='lines+markers'))
                fig_main.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig_main, use_container_width=True)
                
            with c2:
                st.subheader("Distribuția misiunilor IGSU")
                st.markdown("<div style='margin-bottom:10px; font-size:0.85rem; color:#94a3b8;'>Ce tipuri de urgențe gestionează pompierii și paramedicii? SMURD reprezintă majoritatea covârșitoare a intervențiilor.</div>", unsafe_allow_html=True)
                
                if D["igsu"] is not None:
                    fig_pie = px.pie(D["igsu"], values="Număr", names="Subcategorie", hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
                    fig_pie.update_traces(textposition='outside', textinfo='percent+label')
                    fig_pie.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(color="white"))
                    st.plotly_chart(fig_pie, use_container_width=True)

        # ==========================================
        # TAB 2: MEDICAL & AVIAȚIE
        # ==========================================
        with tab2:
            st.markdown("#### Infrastructura critică: UPU și Aviația SMURD")
            st.markdown("""
            <span style='font-size:0.9rem; color:#cbd5e1'>
            Analizăm presiunea asupra spitalelor (prin numărul de pacienți ajunși în Unitățile de Primiri Urgențe) 
            și activitatea flotei aeriene de salvare (elicoptere și avioane SMURD) pentru cazurile critice sau transport la distanță.
            </span><br><br>
            """, unsafe_allow_html=True)
            
            m1, m2 = st.columns(2)
            
            with m1:
                st.subheader("Fluxul de pacienți în UPU")
                st.markdown("<div style='font-size:0.85rem; color:#94a3b8;'>Volumul total anual de persoane care au necesitat asistență medicală de urgență în spitale.</div>", unsafe_allow_html=True)
                
                if D["upu"] is not None:
                    fig_upu = px.area(D["upu"], x="An", y="Prezentări în UPU")
                    fig_upu.update_traces(line_color="#10b981", fillcolor="rgba(16, 185, 129, 0.2)")
                    fig_upu.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_upu, use_container_width=True)
            
            with m2:
                st.subheader("Activitatea aeriană de salvare")
                st.markdown("<div style='font-size:0.85rem; color:#94a3b8;'>Orele de zbor acumulate anual de Inspectoratul General de Aviație (IGAV) în misiuni medicale și de căutare-salvare.</div>", unsafe_allow_html=True)
                
                if D["zbor"] is not None:
                    fig_zbor = px.bar(D["zbor"], x="An", y="Ore de zbor", text="Ore de zbor")
                    fig_zbor.update_traces(marker_color="#f59e0b", textposition='outside')
                    fig_zbor.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), yaxis=dict(showgrid=False))
                    st.plotly_chart(fig_zbor, use_container_width=True)

        # ==========================================
        # TAB 3: PREVENIRE & PARTENERI
        # ==========================================
        with tab3:
            st.markdown("#### Reziliența Comunității și Parteneriate")
            st.markdown("""
            <span style='font-size:0.9rem; color:#cbd5e1'>
            Situațiile de urgență nu se gestionează doar prin intervenție, ci și prin educație. 
            Aici vizualizăm impactul campaniilor de instruire a populației și structura rețelei de parteneri civili (ONG-uri, mediu privat).
            </span><br><br>
            """, unsafe_allow_html=True)

            p1, p2 = st.columns([1.4, 1])
            
            with p1:
                st.subheader("Campania Națională 'Fii Pregătit'")
                st.markdown("""
                <div style='background-color:rgba(220, 38, 38, 0.1); padding:10px; border-radius:5px; margin-bottom:10px; font-size:0.85rem;'>
                'Fii Pregătit' este platforma oficială de informare a DSU. 
                Caravana SMURD și voluntarii merg în județe pentru a învăța populația tehnici de prim ajutor și reacție la dezastre.
                <br><strong>Harta:</strong> Arată numărul de persoane instruite fizic în fiecare județ raportat în 2024.
                </div>
                """, unsafe_allow_html=True)
                
                if D["instruire"] is not None:
                    # Procesare date
                    df_map = D["instruire"].copy()
                    
                    def extract_code(val):
                        parts = str(val).split()
                        if len(parts) > 1: return parts[-1].upper()
                        return ""
                    
                    df_map['Code'] = df_map['Unitate'].apply(extract_code)
                    df_map['Judet_Map'] = df_map['Code'].map(isu_to_judet)
                    
                    # Merge cu toate judetele pentru contur complet
                    df_full = pd.DataFrame({'Judet_Map': toate_judetele})
                    df_agged = df_map.groupby('Judet_Map')['Total Persoane instruite'].sum().reset_index()
                    final_map_data = pd.merge(df_full, df_agged, on='Judet_Map', how='left').fillna(0)
                    
                    geojson_url = get_romania_geojson()
                    
                    fig_choropleth = px.choropleth(
                        final_map_data,
                        geojson=geojson_url,
                        locations='Judet_Map',
                        featureidkey="properties.name",
                        color='Total Persoane instruite',
                        color_continuous_scale="Reds",
                        range_color=(0, final_map_data[final_map_data['Total Persoane instruite'] > 0]['Total Persoane instruite'].max()),
                        scope="europe", 
                        center={"lat": 46.0, "lon": 25.0},
                        labels={'Total Persoane instruite': 'Persoane instruite'}
                    )
                    
                    fig_choropleth.update_geos(fitbounds="locations", visible=False)
                    fig_choropleth.update_layout(
                        height=550,
                        paper_bgcolor="rgba(0,0,0,0)",
                        geo=dict(bgcolor="rgba(0,0,0,0)"),
                        font=dict(color="white"),
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )
                    st.plotly_chart(fig_choropleth, use_container_width=True)
            
            with p2:
                # --- REDESIGN: Arii de expertiza (Bar Chart in loc de Pie) ---
                st.subheader("Domeniile partenerilor DSU")
                st.markdown("<div style='font-size:0.85rem; color:#94a3b8; margin-bottom:10px;'>În ce domenii activează organizațiile partenere?</div>", unsafe_allow_html=True)
                
                if D["expertiza"] is not None:
                    # Sortam pentru aspect placut
                    df_exp = D["expertiza"].sort_values("Număr organizații", ascending=True)
                    fig_exp = px.bar(
                        df_exp, 
                        x="Număr organizații", 
                        y="Value", 
                        orientation='h', 
                        text="Număr organizații",
                        color="Număr organizații",
                        color_continuous_scale="Reds"
                    )
                    fig_exp.update_traces(textposition='outside')
                    fig_exp.update_layout(
                        height=300, 
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white"), 
                        xaxis_title="",
                        yaxis_title="",
                        showlegend=False,
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig_exp, use_container_width=True)
                
                st.divider()

                # --- REDESIGN: Protocoale (Area Chart in loc de Tabel) ---
                st.subheader("Dinamica parteneriatelor")
                st.markdown("<div style='font-size:0.85rem; color:#94a3b8; margin-bottom:10px;'>Evoluția semnării de noi protocoale de colaborare cu societatea civilă.</div>", unsafe_allow_html=True)
                
                if D["protocoale"] is not None:
                    fig_proto = px.area(
                        D["protocoale"], 
                        x="An", 
                        y="Situatii",
                        markers=True
                    )
                    fig_proto.update_traces(line_color="#3b82f6", fillcolor="rgba(59, 130, 246, 0.2)")
                    fig_proto.update_layout(
                        height=250, 
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white"),
                        xaxis=dict(showgrid=False),
                        yaxis_title="Protocoale Noi",
                        margin={"l":0, "r":0, "b":0, "t":10}
                    )
                    st.plotly_chart(fig_proto, use_container_width=True)


# ---------------------------------
# 6. PAGE: DESPRE PROIECT
# ---------------------------------

elif page == "Despre proiect":
    # Add padding class for this page
    st.markdown('<style>.stApp .main .block-container { padding-left: 2rem !important; padding-right: 2rem !important; max-width: 1400px !important; margin: 0 auto !important; }</style>', unsafe_allow_html=True)

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
                <a href="mailto:alexandru.poliac03@e-uvt.ro" style="color: #dc2626;">contact@example.com</a>
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