import streamlit as st

st.set_page_config(page_title="Coffee Aggregated Exports", layout="wide", initial_sidebar_state="expanded")

import exports_view as ev  # noqa: E402  (after set_page_config)
from origins import NAMES  # noqa: E402

# Strict light theme (same as Cecafe Daily): CSS hard-codes colours, no prefers-color-scheme,
# and .streamlit/config.toml pins base="light".
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: #fafafa !important; }
[data-testid="stHeader"] { background: #fafafa !important; }
[data-testid="stSidebar"] { background: #f0f2f8 !important; border-right: 1px solid #dfe3ee; }
h1, h2, h3, h4, h5, h6 { color: #0a2463 !important; }
body, .main { color: #1a1a2e; }
[data-testid="stSidebar"] { color: #1a1a2e; }
.block-container { padding-top: 2.2rem; }

/* Radio as pill / segmented control */
div[role="radiogroup"] { background: #eef0f6; padding: 4px; border-radius: 999px; gap: 2px; display: inline-flex; flex-wrap: wrap; }
div[role="radiogroup"] label { background: transparent !important; border-radius: 999px !important; padding: 4px 12px !important; margin: 0 !important; }
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display: none; }
div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 12px !important; color: #5a6688; }
div[role="radiogroup"] label:has(input:checked) { background: #0a2463 !important; }
div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600; }

/* Multi-select pills (Origin) */
[data-testid="stButtonGroup"] { background: #eef0f6; padding: 4px; border-radius: 999px; gap: 2px; width: fit-content; max-width: 100%; flex-wrap: wrap; }
[data-testid="stBaseButton-pills"] { background: transparent !important; border: none !important; color: #5a6688 !important;
    padding: 3px 12px !important; min-height: 0 !important; border-radius: 999px !important; }
[data-testid="stBaseButton-pillsActive"] { background: #0a2463 !important; border: none !important; color: #ffffff !important;
    padding: 3px 12px !important; min-height: 0 !important; border-radius: 999px !important; }
[data-testid="stBaseButton-pills"] p, [data-testid="stBaseButton-pillsActive"] p { font-size: 12px !important; }
[data-testid="stBaseButton-pillsActive"] p { font-weight: 600; color: #ffffff !important; }

/* Selects: white bg, dark text */
[data-baseweb="popover"] [data-baseweb="menu"] { background: #ffffff !important; }
[data-baseweb="popover"] [data-baseweb="menu"] li,
[data-baseweb="popover"] [data-baseweb="menu"] li * { color: #1a1a2e !important; }
[data-baseweb="select"] { background: #ffffff !important; }
[data-baseweb="select"] > div { background: #ffffff !important; color: #1a1a2e !important; }

.card-desc { color: #5a6688; font-size: 0.82rem; margin-top: -6px; margin-bottom: 10px; }
.chart-head { color: #0a2463; font-weight: 600; font-size: 0.95rem; margin-bottom: 0; }
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    background: #ffffff; border: 1px solid #e3e7f0 !important; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(10,36,99,0.06); }

/* Section selector in the sidebar: large stacked pills; Entry (first) is dark orange when selected */
[data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { display: flex; flex-direction: column; align-items: stretch; width: 100%; border-radius: 22px; padding: 5px; gap: 3px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding: 8px 18px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label:first-of-type:has(input:checked) { background: #c2410c !important; }
.sb-label { font-size: 11px; color: #7a86a8; text-transform: uppercase; letter-spacing: .06em; margin: 6px 0 4px; }
.sb-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: #0a2463; margin-bottom: 2px; }
.page-title { color: #0a2463; font-weight: 700; font-size: 1.25rem; margin: 0 0 6px 0; }
.card-title { color: #0a2463; font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.pill { display: inline-block; background: #e6e9f2; color: #0a2463; font-size: 11px; font-weight: 600;
        padding: 1px 8px; border-radius: 999px; margin-left: 6px; vertical-align: middle; }

/* Compact Excel-style tables (save history) */
.dtab { width: auto; border-collapse: collapse; font-size: 11.5px; line-height: 1.15; background: #ffffff; }
.dtab th { text-align: center; padding: 2px 8px; font-weight: 600; white-space: nowrap; }
.dtab .sub th { background: #0a2463; color: #ffffff; }
.dtab td { text-align: right; padding: 1px 8px; border-bottom: 1px solid #eef0f6; white-space: nowrap; color: #1a1a2e; }
.dtab td.dt { text-align: center; background: #f0f2f8; }
.dtab td.b { font-weight: 700; background: #f6f7fb; }
.dtab td.ts { font-size: 10.5px; font-style: italic; color: #7a86a8; text-align: left; }
</style>
""",
    unsafe_allow_html=True,
)

# Widgets that are not drawn in a run lose their value (e.g. the Exports filters while Entry is open).
# Keep a copy of the ones we care about and put it back before the widgets are created.
KEEP = (["section", "mc_ch_comm", "mc_ch_unit", "mc_ch_span", "mc_cy_basis", "mc_pj_method", "mc_view", "mc_cumview",
         "mc_roll", "en_origin", "en_years"] + [f"mc_origin_{c}" for c in ev.COMMS])
for _k in KEEP:
    if _k not in st.session_state and f"_keep_{_k}" in st.session_state:
        st.session_state[_k] = st.session_state[f"_keep_{_k}"]

with st.sidebar:
    st.markdown("<div class='sb-title'>Coffee Exports</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-label'>Section</div>", unsafe_allow_html=True)
    section = st.radio("Section", ["Entry", "Exports"], index=1, label_visibility="collapsed", key="section")

if section == "Entry":
    ev.render_entry()
else:
    ev.render()

for _k in KEEP:                                                # remember the values for the next run
    if _k in st.session_state:
        st.session_state[f"_keep_{_k}"] = st.session_state[_k]
