"""
MedBotX – Professional Medical Chatbot UI
Developed by Bhaskar Shivaji Kumbhar
"""
import os, requests
import streamlit as st
from datetime import datetime

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="MedBotX — AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "messages": [], "session_id": None,
    "access_token": None, "username": None,
    "user_id": None, "dark_mode": True,
    "medical_profile": {},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme tokens ──────────────────────────────────────────────────────────────
D = st.session_state.dark_mode
BG         = "#0b0f1a"      if D else "#f0f4f8"
BG2        = "#111827"      if D else "#ffffff"
BG3        = "#1a2235"      if D else "#e8edf5"
BORDER     = "rgba(99,179,237,0.12)" if D else "rgba(49,130,206,0.2)"
TEXT       = "#e2e8f0"      if D else "#1a202c"
TEXT2      = "#94a3b8"      if D else "#64748b"
ACCENT     = "#3b82f6"
ACCENT2    = "#60a5fa"
BOT_BG     = "#1e293b"      if D else "#eff6ff"
BOT_BORDER = "rgba(96,165,250,0.2)" if D else "rgba(59,130,246,0.2)"
USER_BG    = "linear-gradient(135deg,#1d4ed8,#3b82f6)"
CARD       = "#161d2e"      if D else "#ffffff"
CARD_BORDER= "rgba(255,255,255,0.06)" if D else "rgba(0,0,0,0.08)"
INPUT_BG   = "#1e293b"      if D else "#f8fafc"
SIDE_BG    = "#0d1320"      if D else "#f8fafc"
SUCCESS    = "#10b981"
WARNING    = "#f59e0b"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}}

/* ── App background ── */
.stApp {{ background: {BG} !important; }}
.main .block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {SIDE_BG} !important;
    border-right: 1px solid {BORDER};
    padding: 0 !important;
}}
[data-testid="stSidebar"] > div {{
    padding: 0 !important;
}}
[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}

/* ── Sidebar inner padding ── */
[data-testid="stSidebarContent"] {{
    padding: 20px 16px !important;
}}

/* ── Logo Card ── */
.logo-card {{
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 50%, #3b82f6 100%);
    border-radius: 20px;
    padding: 24px 20px;
    text-align: center;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(59,130,246,0.3);
}}
.logo-card::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 70% 30%, rgba(255,255,255,0.08) 0%, transparent 60%);
}}
.logo-card .icon {{ font-size: 2.8rem; margin-bottom: 8px; display: block; }}
.logo-card h1 {{
    color: #fff !important;
    font-size: 1.8rem !important;
    font-weight: 900 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -1px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}}
.logo-card .tagline {{
    color: rgba(255,255,255,0.8) !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    margin: 0 !important;
    letter-spacing: 0.5px;
}}
.online-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(16,185,129,0.2);
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem !important;
    color: #6ee7b7 !important;
    margin-top: 12px;
    font-weight: 500;
}}
.online-dot {{
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%      {{ opacity:0.5; transform:scale(1.3); }}
}}

/* ── User profile chip ── */
.user-chip {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: {BG3};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
}}
.user-avatar {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg,#1d4ed8,#7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}}
.user-info .name {{ font-weight: 700; font-size: 0.9rem; color: {TEXT}; }}
.user-info .role {{ font-size: 0.72rem; color: {SUCCESS}; font-weight: 500; }}

/* ── Section label ── */
.section-label {{
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.2px !important;
    color: {TEXT2} !important;
    text-transform: uppercase !important;
    margin: 16px 0 8px 0 !important;
}}

/* ── Auth tabs ── */
.stRadio [role="radiogroup"] {{
    display: flex;
    gap: 4px;
    background: {BG3};
    border-radius: 10px;
    padding: 4px;
}}
.stRadio [role="radiogroup"] label {{
    flex: 1;
    text-align: center;
    padding: 7px 12px !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    cursor: pointer;
    transition: all 0.2s;
    color: {TEXT2} !important;
}}
.stRadio [role="radiogroup"] label[data-selected="true"] {{
    background: {ACCENT} !important;
    color: white !important;
}}

/* ── Forms ── */
.stTextInput > label, .stTextArea > label,
.stNumberInput > label, .stSelectbox > label {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: {TEXT2} !important;
    letter-spacing: 0.3px !important;
    margin-bottom: 4px !important;
}}
.stTextInput input, .stTextArea textarea,
.stNumberInput input {{
    background: {INPUT_BG} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}}
.stSelectbox > div > div {{
    background: {INPUT_BG} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
}}

/* ── Primary button ── */
.stButton > button {{
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 11px 20px !important;
    width: 100% !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.35) !important;
    transition: all 0.2s !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(59,130,246,0.45) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Danger button ── */
.danger-btn > button {{
    background: linear-gradient(135deg,#991b1b,#dc2626) !important;
    box-shadow: 0 4px 16px rgba(220,38,38,0.3) !important;
}}

/* ── Divider ── */
hr {{ border-color: {BORDER} !important; margin: 12px 0 !important; }}

/* ── Disclaimer ── */
.disclaimer {{
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.74rem !important;
    color: #fbbf24 !important;
    line-height: 1.6;
    margin-top: 8px;
}}

/* ── Developer footer ── */
.dev-footer {{
    text-align: center;
    padding: 10px 0 0 0;
    font-size: 0.7rem !important;
    color: {TEXT2} !important;
}}
.dev-footer .name {{ color: {ACCENT2} !important; font-weight: 700; }}

/* ═══════════════════════════════════════════════════
   MAIN CONTENT
═══════════════════════════════════════════════════ */

/* ── Top header ── */
.topbar {{
    background: {BG2};
    border-bottom: 1px solid {BORDER};
    padding: 18px 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.topbar-left h2 {{
    color: {TEXT};
    font-size: 1.25rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}}
.topbar-left p {{
    color: {TEXT2};
    font-size: 0.78rem;
    margin: 3px 0 0 0;
}}

/* ── KPI cards ── */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 12px;
    padding: 20px 36px 0 36px;
}}
.kpi-card {{
    background: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 14px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}}
.kpi-card .kpi-icon {{
    font-size: 1.4rem;
    margin-bottom: 8px;
}}
.kpi-card .kpi-val {{
    font-size: 1.15rem;
    font-weight: 800;
    color: {TEXT};
    letter-spacing: -0.3px;
}}
.kpi-card .kpi-label {{
    font-size: 0.72rem;
    color: {TEXT2};
    font-weight: 500;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.kpi-card .kpi-accent {{
    position: absolute;
    top: 0; right: 0;
    width: 60px; height: 60px;
    border-radius: 0 14px 0 60px;
    opacity: 0.12;
}}

/* ── Chat area ── */
.chat-area {{
    padding: 28px 36px 12px 36px;
    min-height: 400px;
}}

/* ── Welcome screen ── */
.welcome-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60px 20px 40px;
    text-align: center;
}}
.welcome-wrap .hero-icon {{
    font-size: 5rem;
    margin-bottom: 20px;
    filter: drop-shadow(0 0 40px rgba(59,130,246,0.5));
    animation: float 3s ease-in-out infinite;
}}
@keyframes float {{
    0%,100% {{ transform: translateY(0); }}
    50%      {{ transform: translateY(-8px); }}
}}
.welcome-wrap h2 {{
    font-size: 2rem;
    font-weight: 900;
    color: {TEXT};
    margin: 0 0 12px 0;
    letter-spacing: -1px;
}}
.welcome-wrap .sub {{
    color: {TEXT2};
    font-size: 0.95rem;
    max-width: 500px;
    line-height: 1.8;
    margin-bottom: 36px;
}}
.chips-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 600px;
    width: 100%;
}}
.chip {{
    background: {BG3};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 0.83rem;
    color: {ACCENT2};
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
    line-height: 1.5;
}}
.chip:hover {{
    background: rgba(59,130,246,0.1);
    border-color: {ACCENT};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.2);
}}
.chip .chip-icon {{ margin-right: 6px; }}

/* ── Message bubbles ── */
.msg-wrap {{
    display: flex;
    margin-bottom: 24px;
    gap: 14px;
    align-items: flex-start;
    animation: msgIn 0.35s cubic-bezier(0.34,1.56,0.64,1);
}}
@keyframes msgIn {{
    from {{ opacity:0; transform:translateY(12px) scale(0.97); }}
    to   {{ opacity:1; transform:translateY(0) scale(1); }}
}}
.msg-wrap.user {{ flex-direction: row-reverse; }}

.av {{
    width: 40px;
    height: 40px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}
.av.bot {{
    background: linear-gradient(135deg,#1e3a5f,#1d4ed8);
    border: 1px solid rgba(59,130,246,0.3);
}}
.av.usr {{
    background: linear-gradient(135deg,#065f46,#059669);
    border: 1px solid rgba(5,150,105,0.3);
}}

.bubble {{
    max-width: 65%;
    padding: 16px 20px;
    border-radius: 18px;
    font-size: 0.9rem;
    line-height: 1.75;
    position: relative;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}}
.bubble.bot {{
    background: {BOT_BG};
    border: 1px solid {BOT_BORDER};
    border-top-left-radius: 4px;
    color: {TEXT};
}}
.bubble.usr {{
    background: {USER_BG};
    border: none;
    border-top-right-radius: 4px;
    color: white;
}}
.bubble .btime {{
    font-size: 0.68rem;
    opacity: 0.5;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
}}

/* ── Typing indicator ── */
.typing {{
    display: flex;
    gap: 5px;
    padding: 14px 20px;
    background: {BOT_BG};
    border: 1px solid {BOT_BORDER};
    border-radius: 18px;
    border-top-left-radius: 4px;
    width: fit-content;
}}
.dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: {ACCENT2};
    animation: bounce 1.2s infinite;
}}
.dot:nth-child(2) {{ animation-delay: 0.2s; }}
.dot:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes bounce {{
    0%,80%,100% {{ transform:scale(0.7); opacity:0.5; }}
    40%          {{ transform:scale(1);   opacity:1; }}
}}

/* ── Input bar ── */
.input-section {{
    padding: 0 36px 20px 36px;
    margin-top: 8px;
}}
.input-section .stTextInput input {{
    background: {INPUT_BG} !important;
    border: 2px solid {BORDER} !important;
    border-radius: 14px !important;
    color: {TEXT} !important;
    font-size: 0.95rem !important;
    padding: 16px 20px !important;
    transition: all 0.2s !important;
}}
.input-section .stTextInput input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.12) !important;
}}
.send-btn > button {{
    height: 52px !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
    padding: 0 !important;
}}

/* ── Metrics override ── */
[data-testid="stMetricValue"] {{
    color: {TEXT} !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {TEXT2} !important;
    font-size: 0.72rem !important;
}}
[data-testid="stMetric"] {{
    background: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 12px 16px !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: {BG3} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}
[data-testid="stExpander"] summary {{
    color: {TEXT} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}}

/* ── Toggle / checkbox ── */
.stCheckbox label {{ color: {TEXT2} !important; font-size: 0.82rem !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: rgba(59,130,246,0.25);
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{ background: rgba(59,130,246,0.45); }}

/* ── Alerts ── */
.stSuccess > div {{ border-radius: 10px !important; background: rgba(16,185,129,0.1) !important; border-color: rgba(16,185,129,0.3) !important; }}
.stError   > div {{ border-radius: 10px !important; background: rgba(239,68,68,0.1) !important; border-color: rgba(239,68,68,0.3) !important; }}
.stWarning > div {{ border-radius: 10px !important; background: rgba(245,158,11,0.1) !important; border-color: rgba(245,158,11,0.3) !important; }}
.stInfo    > div {{ border-radius: 10px !important; background: rgba(59,130,246,0.1) !important; border-color: rgba(59,130,246,0.3) !important; }}
</style>
""", unsafe_allow_html=True)


# ── API helpers ───────────────────────────────────────────────────────────────
def auth_headers():
    t = st.session_state.access_token
    return {"Authorization": f"Bearer {t}"} if t else {}

def api_post(ep, payload, timeout=30):
    try:
        r = requests.post(f"{API_BASE}{ep}", json=payload, headers=auth_headers(), timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the MedBotX API. Please start the backend server.")
        return None
    except requests.HTTPError as e:
        try:   detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        st.error(f"{detail}")
        return None

def api_get(ep, params=None):
    try:
        r = requests.get(f"{API_BASE}{ep}", headers=auth_headers(), params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except: return None

def api_put(ep, payload, timeout=30):
    try:
        r = requests.put(f"{API_BASE}{ep}", json=payload, headers=auth_headers(), timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API.")
        return None
    except requests.HTTPError as e:
        try:   detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        st.error(f"{detail}")
        return None

def ensure_session():
    if not st.session_state.session_id:
        d = api_post("/api/v1/chat/session/new", {})
        if d: st.session_state.session_id = d["session_id"]

def load_profile():
    d = api_get("/api/v1/memory/load")
    if d: st.session_state.medical_profile = d.get("medical_context", {})


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="logo-card">
        <span class="icon">🏥</span>
        <h1>MedBotX</h1>
        <p class="tagline">Advanced AI Medical Assistant</p>
        <div class="online-badge">
            <span class="online-dot"></span> Online & Ready
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dark / Light toggle
    col_t1, col_t2 = st.columns([3,2])
    with col_t1:
        st.markdown(f'<p class="section-label">Appearance</p>', unsafe_allow_html=True)
    with col_t2:
        new_mode = st.toggle("Dark", value=st.session_state.dark_mode, label_visibility="collapsed")
        if new_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = new_mode
            st.rerun()
    st.markdown(f'<p style="font-size:0.75rem;color:{TEXT2};margin-top:-8px;">{"🌙 Dark mode" if D else "☀️ Light mode"}</p>', unsafe_allow_html=True)

    st.divider()

    # ── AUTH ──────────────────────────────────────────────────────────────────
    if not st.session_state.username:
        st.markdown(f'<p class="section-label">Account</p>', unsafe_allow_html=True)
        tab = st.radio("", ["Guest", "Sign In", "Register"], horizontal=True, label_visibility="collapsed")

        if tab == "Sign In":
            with st.form("lf", clear_on_submit=False):
                un = st.text_input("Username", placeholder="your_username")
                pw = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Sign In →"):
                    if un and pw:
                        d = api_post("/api/v1/auth/login", {"username": un, "password": pw})
                        if d:
                            st.session_state.access_token = d["access_token"]
                            st.session_state.username = un
                            me = api_get("/api/v1/auth/me")
                            if me: st.session_state.user_id = me["id"]
                            load_profile()
                            st.success(f"Welcome back, {un}!")
                            st.rerun()
                    else:
                        st.warning("Please fill in all fields.")

        elif tab == "Register":
            with st.form("rf", clear_on_submit=False):
                un = st.text_input("Username", placeholder="choose_username")
                em = st.text_input("Email", placeholder="you@email.com")
                pw = st.text_input("Password", type="password", placeholder="Min 8 characters")
                if st.form_submit_button("Create Account →"):
                    if un and em and pw:
                        d = api_post("/api/v1/auth/register", {"username": un, "email": em, "password": pw})
                        if d:
                            st.success("✅ Account created! Now sign in.")
                    else:
                        st.warning("Please fill in all fields.")

        else:
            st.info("💬 Chatting as guest. Sign in to save history and medical profile permanently.")

    else:
        # Logged-in user chip
        initials = st.session_state.username[0].upper()
        st.markdown(f"""
        <div class="user-chip">
            <div class="user-avatar">{initials}</div>
            <div class="user-info">
                <div class="name">{st.session_state.username}</div>
                <div class="role">✓ Authenticated · Memory Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign Out", key="signout"):
            for k in ["access_token","username","user_id","messages","session_id","medical_profile"]:
                st.session_state[k] = [] if k == "messages" else ({} if k == "medical_profile" else None)
            st.rerun()

        st.divider()

        # ── Health Profile ────────────────────────────────────────────────────
        st.markdown(f'<p class="section-label">🩺 Health Profile</p>', unsafe_allow_html=True)

        prof = st.session_state.medical_profile
        with st.expander("View / Edit my health info", expanded=False):
            with st.form("hf", clear_on_submit=False):
                age   = st.number_input("Age",
                    min_value=0, max_value=120,
                    value=int(prof.get("age", 0) or 0))
                blood = st.selectbox("Blood Type",
                    ["", "A+","A-","B+","B-","AB+","AB-","O+","O-"],
                    index=(["","A+","A-","B+","B-","AB+","AB-","O+","O-"].index(prof.get("blood_type","")) if prof.get("blood_type") in ["","A+","A-","B+","B-","AB+","AB-","O+","O-"] else 0))
                allerg = st.text_area("Allergies (comma-separated)",
                    value=", ".join(prof.get("allergies", [])),
                    placeholder="e.g. Penicillin, Peanuts", height=68)
                conds  = st.text_area("Medical Conditions",
                    value=", ".join(prof.get("conditions", [])),
                    placeholder="e.g. Diabetes Type 2, Hypertension", height=68)
                meds   = st.text_area("Current Medications",
                    value=", ".join(prof.get("medications", [])),
                    placeholder="e.g. Metformin 500mg, Lisinopril", height=68)
                notes  = st.text_area("Notes for Doctor",
                    value=prof.get("notes",""),
                    placeholder="Any other health notes...", height=60)

                if st.form_submit_button("💾 Save Health Profile"):
                    payload = {
                        "age":        int(age) if age and age > 0 else None,
                        "blood_type": blood or None,
                        "allergies":  [a.strip() for a in allerg.split(",") if a.strip()],
                        "conditions": [c.strip() for c in conds.split(",")  if c.strip()],
                        "medications":[m.strip() for m in meds.split(",")   if m.strip()],
                        "notes":      notes.strip() or None,
                    }
                    r = api_put("/api/v1/memory/medical-context", payload)
                    if r:
                        st.session_state.medical_profile = r.get("medical_context", payload)
                        st.success("✅ Health profile saved!")

        # Show profile summary if filled
        if prof:
            items = []
            if prof.get("age"):        items.append(f"Age {prof['age']}")
            if prof.get("blood_type"): items.append(f"Blood {prof['blood_type']}")
            if prof.get("conditions"): items.append(f"{len(prof['conditions'])} condition(s)")
            if prof.get("medications"):items.append(f"{len(prof['medications'])} medication(s)")
            if items:
                summary = " · ".join(items)
                st.markdown(f'<p style="font-size:0.75rem;color:{TEXT2};padding:4px 0;">{summary}</p>', unsafe_allow_html=True)

    st.divider()

    # Disclaimer
    st.markdown(f"""
    <div class="disclaimer">
        ⚠️ <strong>Medical Disclaimer</strong><br>
        MedBotX provides general health information only — not a substitute for professional medical advice,
        diagnosis, or treatment. Always consult a qualified healthcare provider.
    </div>
    <div class="dev-footer" style="margin-top:14px;">
        Developed by <span class="name">Bhaskar Shivaji Kumbhar</span><br>
        <span style="font-size:0.65rem;opacity:0.5;">MedBotX v1.0.0 · 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

# ── Top bar ──────────────────────────────────────────────────────────────────
user_label  = st.session_state.username or "Guest"
mem_label   = "Permanent" if st.session_state.access_token else "Session"
msg_count   = len([m for m in st.session_state.messages if m["role"] == "human"])

st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <h2>🏥 MedBotX &nbsp;—&nbsp; AI Medical Assistant</h2>
        <p>Ask about symptoms, medications, conditions, diet, or general health</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-icon">👤</div>
        <div class="kpi-val">{user_label}</div>
        <div class="kpi-label">Logged in as</div>
        <div class="kpi-accent" style="background:{ACCENT};"></div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">🧠</div>
        <div class="kpi-val">{mem_label}</div>
        <div class="kpi-label">Memory Type</div>
        <div class="kpi-accent" style="background:#7c3aed;"></div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">💬</div>
        <div class="kpi-val">{msg_count}</div>
        <div class="kpi-label">Questions Asked</div>
        <div class="kpi-accent" style="background:#0891b2;"></div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">🟢</div>
        <div class="kpi-val">Online</div>
        <div class="kpi-label">System Status</div>
        <div class="kpi-accent" style="background:{SUCCESS};"></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.divider()

# ── Chat messages ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome-wrap">
        <div class="hero-icon">🩺</div>
        <h2>How can I help you today?</h2>
        <p class="sub">
            I'm MedBotX, your AI-powered medical information assistant.<br>
            Ask me about symptoms, medications, health conditions, nutrition, or wellness tips.<br>
            I always recommend consulting a doctor for personal medical decisions.
        </p>
        <div class="chips-grid">
            <div class="chip"><span class="chip-icon">🤒</span> What are symptoms of Type 2 Diabetes?</div>
            <div class="chip"><span class="chip-icon">💊</span> Side effects of Ibuprofen?</div>
            <div class="chip"><span class="chip-icon">❤️</span> How to lower blood pressure naturally?</div>
            <div class="chip"><span class="chip-icon">😴</span> Why am I always feeling tired?</div>
            <div class="chip"><span class="chip-icon">🧬</span> What is cholesterol and why does it matter?</div>
            <div class="chip"><span class="chip-icon">🍎</span> Best diet for someone with hypertension?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"].replace("\n", "<br>")
        ts      = msg.get("timestamp", "")
        if role == "ai":
            st.markdown(f"""
            <div class="msg-wrap">
                <div class="av bot">🤖</div>
                <div class="bubble bot">{content}<div class="btime">{ts}</div></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-wrap user">
                <div class="av usr">👤</div>
                <div class="bubble usr">{content}<div class="btime">{ts}</div></div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Input bar ─────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="input-section">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([10, 1])
    with cols[0]:
        user_input = st.text_input(
            "msg", placeholder="Ask your medical question here...",
            label_visibility="collapsed")
    with cols[1]:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send = st.form_submit_button("➤")
        st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if send and user_input.strip():
    ensure_session()
    st.session_state.messages.append({
        "role": "human", "content": user_input.strip(),
        "timestamp": datetime.now().strftime("%I:%M %p"),
    })
    with st.spinner("MedBotX is thinking..."):
        data = api_post("/api/v1/chat/", {
            "message": user_input.strip(),
            "session_id": st.session_state.session_id,
        })
    if data:
        st.session_state.session_id = data["session_id"]
        st.session_state.messages.append({
            "role": "ai", "content": data["response"],
            "timestamp": datetime.now().strftime("%I:%M %p"),
        })
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:12px 0 4px;font-size:0.72rem;color:{TEXT2};
border-top:1px solid {BORDER};margin-top:12px;">
    MedBotX &nbsp;·&nbsp; Developed by
    <span style="color:{ACCENT2};font-weight:700;">Bhaskar Shivaji Kumbhar</span>
    &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp;
    Always consult a healthcare professional
</div>
""", unsafe_allow_html=True)
