"""
MedBotX – Professional Medical Chatbot UI
Developed by Bhaskar Shivaji Kumbhar
"""
import os
import requests
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

D = st.session_state.dark_mode

# ── Theme ─────────────────────────────────────────────────────────────────────
if D:
    BG        = "#0b0f1a"
    SIDEBAR   = "#0d1320"
    CARD      = "#111827"
    CARD2     = "#1a2235"
    BORDER    = "#1e3a5f"
    TEXT      = "#e2e8f0"
    TEXT_MUTE = "#94a3b8"
    INPUT_BG  = "#1e293b"
    BOT_BG    = "#1a2235"
    BOT_BORDER= "#1e3a5f"
    USER_BG   = "linear-gradient(135deg, #1d4ed8, #3b82f6)"
    USER_TEXT = "#ffffff"
    BOT_TEXT  = "#e2e8f0"
    BTN_BG    = "linear-gradient(135deg, #1d4ed8, #3b82f6)"
    BTN_TEXT  = "#ffffff"
    BTN_SHADOW= "rgba(59,130,246,0.4)"
    CHIP_BG   = "#1a2235"
    CHIP_BD   = "#1e3a5f"
    CHIP_TEXT = "#93c5fd"
    DIVIDER   = "#1e293b"
    KPI_CARD  = "#111827"
    KPI_BD    = "#1e3a5f"
    TOPBAR    = "#111827"
    TOPBAR_BD = "#1e3a5f"
    DISC_BG   = "rgba(245,158,11,0.1)"
    DISC_BD   = "rgba(245,158,11,0.3)"
    DISC_TEXT = "#fbbf24"
    INP_FOCUS = "#3b82f6"
    SUCCESS   = "#10b981"
    WARN_TEXT = "#fbbf24"
else:
    BG        = "#f1f5f9"
    SIDEBAR   = "#ffffff"
    CARD      = "#ffffff"
    CARD2     = "#f8fafc"
    BORDER    = "#cbd5e1"
    TEXT      = "#0f172a"
    TEXT_MUTE = "#64748b"
    INPUT_BG  = "#f8fafc"
    BOT_BG    = "#eff6ff"
    BOT_BORDER= "#bfdbfe"
    USER_BG   = "linear-gradient(135deg, #1d4ed8, #3b82f6)"
    USER_TEXT = "#ffffff"
    BOT_TEXT  = "#1e3a5f"
    BTN_BG    = "linear-gradient(135deg, #1d4ed8, #2563eb)"
    BTN_TEXT  = "#ffffff"
    BTN_SHADOW= "rgba(37,99,235,0.35)"
    CHIP_BG   = "#eff6ff"
    CHIP_BD   = "#bfdbfe"
    CHIP_TEXT = "#1d4ed8"
    DIVIDER   = "#e2e8f0"
    KPI_CARD  = "#ffffff"
    KPI_BD    = "#cbd5e1"
    TOPBAR    = "#ffffff"
    TOPBAR_BD = "#cbd5e1"
    DISC_BG   = "rgba(180,83,9,0.06)"
    DISC_BD   = "rgba(180,83,9,0.2)"
    DISC_TEXT = "#92400e"
    INP_FOCUS = "#2563eb"
    SUCCESS   = "#059669"
    WARN_TEXT = "#92400e"

ACCENT = "#3b82f6"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ═══════ RESET & BASE ═══════ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}
html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: {BG} !important;
}}
.stApp {{ background: {BG} !important; }}
#MainMenu, footer, [data-testid="stToolbar"], .st-emotion-cache-zq5wmm {{ display:none!important; }}
.main .block-container {{ padding: 1.2rem 1.8rem 0.5rem !important; max-width: 100% !important; }}

/* ═══════ SIDEBAR ═══════ */
[data-testid="stSidebar"] {{
    background: {SIDEBAR} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebarContent"] {{ padding: 1rem 0.9rem !important; }}

/* ═══════ LOGO ═══════ */
.logo-wrap {{
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 55%, #3b82f6 100%);
    border-radius: 16px; padding: 20px 16px 18px;
    text-align: center; margin-bottom: 16px;
    box-shadow: 0 6px 28px rgba(59,130,246,0.3);
}}
.logo-wrap .logo-icon {{ font-size: 2.2rem; display: block; margin-bottom: 6px; }}
.logo-wrap .logo-name {{
    color: #fff !important; font-size: 1.55rem !important;
    font-weight: 900 !important; letter-spacing: -0.8px;
    display: block; margin-bottom: 2px;
}}
.logo-wrap .logo-sub {{
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.73rem !important; display: block;
}}
.logo-wrap .live-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,0.22); border: 1px solid rgba(16,185,129,0.4);
    border-radius: 20px; padding: 3px 10px; margin-top: 10px;
    font-size: 0.68rem !important; color: #6ee7b7 !important; font-weight: 600;
}}
.live-dot {{
    width: 6px; height: 6px; background: #10b981;
    border-radius: 50%; display: inline-block;
    animation: pulse 1.8s ease-in-out infinite;
}}
@keyframes pulse {{ 0%,100%{{ opacity:1; transform:scale(1); }} 50%{{ opacity:0.4; transform:scale(1.4); }} }}

/* ═══════ SIDEBAR TEXT ═══════ */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
    color: {TEXT} !important;
}}
[data-testid="stSidebar"] .stRadio label {{ color: {TEXT} !important; }}

/* ═══════ SECTION LABEL ═══════ */
.slabel {{
    font-size: 0.64rem !important; font-weight: 700 !important;
    letter-spacing: 1.3px !important; color: {TEXT_MUTE} !important;
    text-transform: uppercase !important; margin: 12px 0 7px !important;
    display: block;
}}

/* ═══════ USER CHIP ═══════ */
.uchip {{
    display: flex; align-items: center; gap: 10px;
    background: {CARD2}; border: 1px solid {BORDER};
    border-radius: 12px; padding: 11px 13px; margin-bottom: 10px;
}}
.uav {{
    width: 36px; height: 36px; border-radius: 9px;
    background: linear-gradient(135deg, #1d4ed8, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.95rem; color: #fff; flex-shrink: 0;
}}
.uname {{ font-weight: 700; font-size: 0.87rem; color: {TEXT} !important; }}
.urole {{ font-size: 0.69rem; color: {SUCCESS} !important; font-weight: 600; margin-top: 1px; }}

/* ═══════ INPUTS ═══════ */
.stTextInput > label, .stTextArea > label,
.stNumberInput > label, .stSelectbox > label {{
    font-size: 0.75rem !important; font-weight: 600 !important;
    color: {TEXT_MUTE} !important; margin-bottom: 4px !important;
    letter-spacing: 0.2px;
}}
.stTextInput input, .stTextArea textarea, .stNumberInput input {{
    background: {INPUT_BG} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 9px !important;
    color: {TEXT} !important;
    font-size: 0.87rem !important;
    font-family: 'Inter', sans-serif !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {{
    border-color: {INP_FOCUS} !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color: {TEXT_MUTE} !important; opacity: 0.6;
}}
.stSelectbox > div > div {{
    background: {INPUT_BG} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 9px !important;
    color: {TEXT} !important;
}}

/* ═══════ BUTTONS ═══════ */
.stButton > button {{
    background: {BTN_BG} !important;
    color: {BTN_TEXT} !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    font-size: 0.86rem !important;
    padding: 10px 18px !important;
    width: 100% !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 14px {BTN_SHADOW} !important;
    transition: all 0.18s ease !important;
    cursor: pointer !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 22px {BTN_SHADOW} !important;
    filter: brightness(1.08) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ═══════ EXPANDER ═══════ */
[data-testid="stExpander"] {{
    background: {CARD2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 11px !important;
    overflow: hidden;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600 !important; font-size: 0.83rem !important;
    color: {TEXT} !important; padding: 11px 14px !important;
}}
[data-testid="stExpander"] summary:hover {{
    background: rgba(59,130,246,0.05) !important;
}}
[data-testid="stExpander"] > div > div {{
    padding: 12px 14px !important;
}}

/* ═══════ TOGGLE ═══════ */
.stCheckbox span, .stToggle span {{ color: {TEXT} !important; }}

/* ═══════ DIVIDER ═══════ */
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 10px 0 !important; }}

/* ═══════ DISCLAIMER ═══════ */
.disclaimer {{
    background: {DISC_BG}; border: 1px solid {DISC_BD};
    border-radius: 10px; padding: 10px 12px;
    font-size: 0.72rem !important; color: {DISC_TEXT} !important;
    line-height: 1.65;
}}
.disclaimer strong {{ color: {DISC_TEXT} !important; }}

/* ═══════ DEV FOOTER ═══════ */
.dev-foot {{
    text-align: center; padding: 10px 0 0;
    font-size: 0.68rem !important; color: {TEXT_MUTE} !important;
}}
.dev-foot .dn {{ color: {ACCENT} !important; font-weight: 700 !important; }}

/* ══════════════════════════════════
   MAIN CONTENT
══════════════════════════════════ */

/* Top bar */
.topbar {{
    background: {TOPBAR}; border: 1px solid {TOPBAR_BD};
    border-radius: 14px; padding: 16px 22px; margin-bottom: 18px;
    display: flex; align-items: center; justify-content: space-between;
}}
.topbar h1 {{
    color: {TEXT} !important; font-size: 1.2rem !important;
    font-weight: 800 !important; margin: 0 !important; letter-spacing: -0.4px;
}}
.topbar p {{ color: {TEXT_MUTE} !important; font-size: 0.76rem !important; margin: 3px 0 0 !important; }}

/* KPI cards */
.kpi-card {{
    background: {KPI_CARD}; border: 1px solid {KPI_BD};
    border-radius: 13px; padding: 16px 14px; text-align: center;
    transition: transform 0.15s, box-shadow 0.15s;
}}
.kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.1); }}
.kpi-icon {{ font-size: 1.4rem; display: block; margin-bottom: 6px; }}
.kpi-val {{ font-size: 0.95rem; font-weight: 800; color: {TEXT}; display: block; }}
.kpi-lbl {{ font-size: 0.65rem; color: {TEXT_MUTE}; text-transform: uppercase;
             letter-spacing: 0.7px; font-weight: 600; display: block; margin-top: 2px; }}

/* Welcome screen */
.welcome {{
    text-align: center; padding: 40px 10px 28px;
}}
.w-icon {{
    font-size: 4rem; display: block; margin-bottom: 14px;
    animation: float 3s ease-in-out infinite;
}}
@keyframes float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-9px)}} }}
.w-title {{
    font-size: 1.75rem; font-weight: 900; color: {TEXT};
    letter-spacing: -0.8px; margin-bottom: 10px;
}}
.w-sub {{
    color: {TEXT_MUTE}; font-size: 0.9rem;
    max-width: 460px; margin: 0 auto 30px; line-height: 1.8;
}}
.chips-grid {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; max-width: 560px; margin: 0 auto;
}}
.chip {{
    background: {CHIP_BG}; border: 1px solid {CHIP_BD};
    border-radius: 11px; padding: 12px 14px;
    font-size: 0.81rem; color: {CHIP_TEXT};
    text-align: left; line-height: 1.5;
    transition: all 0.16s;
}}
.chip:hover {{
    border-color: {ACCENT};
    box-shadow: 0 4px 14px rgba(59,130,246,0.18);
    transform: translateY(-1px);
}}

/* Chat messages */
.chat-msg-wrap {{
    display: flex; margin-bottom: 18px; gap: 12px; align-items: flex-start;
}}
.chat-msg-wrap.user-wrap {{ flex-direction: row-reverse; }}
.msg-avatar {{
    width: 38px; height: 38px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
}}
.msg-avatar.bot-av {{
    background: linear-gradient(135deg, #1e3a5f, #1d4ed8);
    border: 1px solid rgba(59,130,246,0.35);
}}
.msg-avatar.user-av {{
    background: linear-gradient(135deg, #065f46, #059669);
    border: 1px solid rgba(5,150,105,0.35);
}}
.msg-bubble {{
    max-width: 68%; padding: 14px 18px; border-radius: 16px;
    font-size: 0.89rem; line-height: 1.78;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}}
.msg-bubble.bot-bubble {{
    background: {BOT_BG}; border: 1px solid {BOT_BORDER};
    border-top-left-radius: 4px; color: {BOT_TEXT};
}}
.msg-bubble.user-bubble {{
    background: {USER_BG};
    border-top-right-radius: 4px; color: {USER_TEXT};
}}
.msg-bubble p {{ margin: 0 0 8px 0; color: inherit !important; }}
.msg-bubble p:last-child {{ margin-bottom: 0; }}
.msg-bubble ul, .msg-bubble ol {{ padding-left: 18px; margin: 8px 0; }}
.msg-bubble li {{ margin-bottom: 4px; color: inherit !important; }}
.msg-bubble strong {{ font-weight: 700; color: inherit !important; }}
.msg-time {{
    font-size: 0.66rem; opacity: 0.55; margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
}}

/* Chat input area */
.chat-input-wrap {{
    background: {TOPBAR}; border: 1px solid {TOPBAR_BD};
    border-radius: 14px; padding: 14px 18px; margin-top: 14px;
}}

/* Streamlit chat input override */
[data-testid="stChatInput"] textarea {{
    background: {INPUT_BG} !important;
    color: {TEXT} !important;
    font-size: 0.93rem !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: {TEXT_MUTE} !important; }}
[data-testid="stChatInputSubmitButton"] svg {{ color: #fff !important; }}
[data-testid="stChatInputSubmitButton"] button {{
    background: {BTN_BG} !important;
    border-radius: 8px !important;
    box-shadow: 0 3px 10px {BTN_SHADOW} !important;
}}

/* Info / Success / Warning */
.stAlert > div {{ border-radius: 10px !important; font-size: 0.84rem !important; }}
[data-testid="stNotification"] {{ color: {TEXT} !important; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(59,130,246,0.25); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: rgba(59,130,246,0.45); }}

/* Main page background */
[data-testid="stAppViewContainer"] > .main {{ background: {BG} !important; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def hdr():
    t = st.session_state.access_token
    return {"Authorization": f"Bearer {t}"} if t else {}

def api_post(ep, body, timeout=30):
    try:
        r = requests.post(f"{API_BASE}{ep}", json=body, headers=hdr(), timeout=timeout)
        r.raise_for_status(); return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Please start the backend server.")
    except requests.HTTPError as e:
        try:    d = e.response.json().get("detail", str(e))
        except: d = str(e)
        st.error(d)
    return None

def api_get(ep):
    try:
        r = requests.get(f"{API_BASE}{ep}", headers=hdr(), timeout=15)
        r.raise_for_status(); return r.json()
    except: return None

def api_put(ep, body):
    try:
        r = requests.put(f"{API_BASE}{ep}", json=body, headers=hdr(), timeout=20)
        r.raise_for_status(); return r.json()
    except requests.HTTPError as e:
        try:    d = e.response.json().get("detail", str(e))
        except: d = str(e)
        st.error(d)
    except: st.error("API error saving profile.")
    return None

def ensure_session():
    if not st.session_state.session_id:
        d = api_post("/api/v1/chat/session/new", {})
        if d: st.session_state.session_id = d["session_id"]

def load_profile():
    d = api_get("/api/v1/memory/load")
    if d: st.session_state.medical_profile = d.get("medical_context", {})

def render_markdown(text: str) -> str:
    """Convert simple markdown to HTML for chat bubbles."""
    import re
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Numbered list items
    lines = text.split('\n')
    html_lines = []
    in_ul = False
    for line in lines:
        if re.match(r'^\d+\.\s', line):
            if not in_ul:
                html_lines.append('<ol style="padding-left:18px;margin:8px 0;">')
                in_ul = 'ol'
            content = re.sub(r'^\d+\.\s', '', line)
            html_lines.append(f'<li style="margin-bottom:5px;">{content}</li>')
        elif re.match(r'^[-•]\s', line):
            if in_ul != 'ul':
                if in_ul: html_lines.append(f'</{in_ul}>')
                html_lines.append('<ul style="padding-left:18px;margin:8px 0;">')
                in_ul = 'ul'
            content = re.sub(r'^[-•]\s', '', line)
            html_lines.append(f'<li style="margin-bottom:5px;">{content}</li>')
        else:
            if in_ul:
                html_lines.append(f'</{in_ul}>')
                in_ul = False
            if line.strip():
                html_lines.append(f'<p style="margin:0 0 7px 0;">{line}</p>')
            else:
                html_lines.append('<br>')
    if in_ul:
        html_lines.append(f'</{in_ul}>')
    return '\n'.join(html_lines)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="logo-wrap">
        <span class="logo-icon">🏥</span>
        <span class="logo-name">MedBotX</span>
        <span class="logo-sub">Advanced AI Medical Assistant</span>
        <div class="live-badge"><span class="live-dot"></span>&nbsp;Online &amp; Ready</div>
    </div>
    """, unsafe_allow_html=True)

    # Dark / Light toggle
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<span style="font-size:0.76rem;color:{TEXT_MUTE};">{"🌙 Dark mode" if D else "☀️ Light mode"}</span>',
                    unsafe_allow_html=True)
    with col2:
        toggled = st.toggle("", value=D, key="tm", label_visibility="collapsed")
        if toggled != D:
            st.session_state.dark_mode = toggled
            st.rerun()

    st.divider()

    # ── AUTH ──────────────────────────────────────────────────────────────────
    if not st.session_state.username:
        st.markdown(f'<span class="slabel">Account</span>', unsafe_allow_html=True)
        mode = st.radio("m", ["Guest", "Sign In", "Register"],
                        horizontal=True, label_visibility="collapsed")

        if mode == "Sign In":
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

        elif mode == "Register":
            with st.form("rf", clear_on_submit=False):
                un = st.text_input("Username", placeholder="choose_username")
                em = st.text_input("Email",    placeholder="you@email.com")
                pw = st.text_input("Password", type="password", placeholder="Min 8 characters")
                if st.form_submit_button("Create Account →"):
                    if un and em and pw:
                        d = api_post("/api/v1/auth/register",
                                     {"username": un, "email": em, "password": pw})
                        if d: st.success("✅ Account created! Please sign in.")
                    else:
                        st.warning("Please fill in all fields.")
        else:
            st.info("💬 Guest mode — history is session only.\nSign in to save everything permanently.")

    else:
        init = st.session_state.username[0].upper()
        st.markdown(f"""
        <div class="uchip">
            <div class="uav">{init}</div>
            <div>
                <div class="uname">{st.session_state.username}</div>
                <div class="urole">✓ Authenticated · Memory Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign Out"):
            for k in ["access_token","username","user_id","messages","session_id","medical_profile"]:
                st.session_state[k] = [] if k == "messages" else ({} if k == "medical_profile" else None)
            st.rerun()

        st.divider()
        st.markdown(f'<span class="slabel">🩺 Health Profile</span>', unsafe_allow_html=True)

        prof = st.session_state.medical_profile or {}

        # Summary line
        summary_parts = []
        if prof.get("age"):         summary_parts.append(f"Age {prof['age']}")
        if prof.get("blood_type"):  summary_parts.append(f"Blood {prof['blood_type']}")
        if prof.get("conditions"):  summary_parts.append(f"{len(prof['conditions'])} condition(s)")
        if prof.get("medications"): summary_parts.append(f"{len(prof['medications'])} medication(s)")
        if summary_parts:
            st.markdown(f'<p style="font-size:0.72rem;color:{TEXT_MUTE};margin:0 0 8px;">'
                        f'{" · ".join(summary_parts)}</p>', unsafe_allow_html=True)

        BLOODS = ["","A+","A-","B+","B-","AB+","AB-","O+","O-"]
        saved_blood = prof.get("blood_type") or ""
        blood_idx = BLOODS.index(saved_blood) if saved_blood in BLOODS else 0

        with st.expander("✏️ Edit Health Profile", expanded=False):
            with st.form("hf", clear_on_submit=False):
                age   = st.number_input("Age", 0, 120, int(prof.get("age") or 0))
                blood = st.selectbox("Blood Type", BLOODS, index=blood_idx)
                allerg = st.text_area("Allergies",
                    value=", ".join(prof.get("allergies") or []),
                    placeholder="e.g. Penicillin, Peanuts", height=58)
                conds  = st.text_area("Medical Conditions",
                    value=", ".join(prof.get("conditions") or []),
                    placeholder="e.g. Diabetes Type 2", height=58)
                meds   = st.text_area("Medications",
                    value=", ".join(prof.get("medications") or []),
                    placeholder="e.g. Metformin 500mg", height=58)
                notes  = st.text_area("Notes",
                    value=prof.get("notes") or "",
                    placeholder="Other health notes...", height=50)

                if st.form_submit_button("💾 Save Profile"):
                    payload = {
                        "age":         int(age) if age and age > 0 else None,
                        "blood_type":  blood or None,
                        "allergies":   [a.strip() for a in allerg.split(",") if a.strip()],
                        "conditions":  [c.strip() for c in conds.split(",")  if c.strip()],
                        "medications": [m.strip() for m in meds.split(",")   if m.strip()],
                        "notes":       notes.strip() or None,
                    }
                    r = api_put("/api/v1/memory/medical-context", payload)
                    if r:
                        st.session_state.medical_profile = r.get("medical_context", payload)
                        st.success("✅ Profile saved!")

    st.divider()

    st.markdown(f"""
    <div class="disclaimer">
        <strong>⚠️ Medical Disclaimer</strong><br>
        MedBotX provides general health information only — not a substitute
        for professional medical advice. Always consult a doctor.
    </div>
    <div class="dev-foot">
        Developed by <span class="dn">Bhaskar Shivaji Kumbhar</span><br>
        <span style="font-size:0.61rem;opacity:0.45;">MedBotX v1.0.0 · 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
user_label = st.session_state.username or "Guest"
mem_label  = "Permanent" if st.session_state.access_token else "Session"
q_count    = len([m for m in st.session_state.messages if m["role"] == "human"])

# Top bar
st.markdown(f"""
<div class="topbar">
    <div>
        <h1>🏥 MedBotX &nbsp;·&nbsp; AI Medical Assistant</h1>
        <p>Ask about symptoms, medications, conditions, nutrition, or general wellness</p>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI row
c1, c2, c3, c4 = st.columns(4)
for col, icon, val, lbl in [
    (c1, "👤", user_label, "User"),
    (c2, "🧠", mem_label,  "Memory"),
    (c3, "💬", str(q_count), "Questions"),
    (c4, "🟢", "Online",   "Status"),
]:
    col.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">{icon}</span>
        <span class="kpi-val">{val}</span>
        <span class="kpi-lbl">{lbl}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
st.divider()

# ── Chat display ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
        <span class="w-icon">🩺</span>
        <div class="w-title">How can I help you today?</div>
        <p class="w-sub">
            I'm MedBotX — your AI medical information assistant.<br>
            Ask about symptoms, medications, health conditions, nutrition, or wellness.
        </p>
        <div class="chips-grid">
            <div class="chip">🤒 What are symptoms of Type 2 Diabetes?</div>
            <div class="chip">💊 Side effects of Ibuprofen?</div>
            <div class="chip">❤️ How to lower blood pressure naturally?</div>
            <div class="chip">😴 Why do I feel tired all the time?</div>
            <div class="chip">🧬 What is cholesterol and why it matters?</div>
            <div class="chip">🍎 Best diet for someone with hypertension?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = render_markdown(msg["content"])
        ts      = msg.get("timestamp", "")
        if role == "ai":
            st.markdown(f"""
            <div class="chat-msg-wrap">
                <div class="msg-avatar bot-av">🤖</div>
                <div class="msg-bubble bot-bubble">
                    {content}
                    <div class="msg-time">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-msg-wrap user-wrap">
                <div class="msg-avatar user-av">👤</div>
                <div class="msg-bubble user-bubble">
                    {content}
                    <div class="msg-time">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
st.divider()
user_input = st.chat_input("Ask your medical question here...")

if user_input and user_input.strip():
    ensure_session()
    ts = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "human", "content": user_input.strip(), "timestamp": ts})

    with st.spinner("MedBotX is thinking..."):
        data = api_post("/api/v1/chat/", {
            "message": user_input.strip(),
            "session_id": st.session_state.session_id,
        })

    ai_ts = datetime.now().strftime("%I:%M %p")
    if data:
        st.session_state.session_id = data["session_id"]
        st.session_state.messages.append({"role": "ai", "content": data["response"], "timestamp": ai_ts})
    else:
        st.session_state.messages.append({
            "role": "ai",
            "content": "I'm having trouble connecting right now. Please try again.",
            "timestamp": ai_ts,
        })
    st.rerun()

# Footer
st.markdown(f"""
<div style="text-align:center;padding:10px 0 4px;font-size:0.69rem;color:{TEXT_MUTE};
border-top:1px solid {BORDER};margin-top:10px;">
    MedBotX &nbsp;·&nbsp;
    Developed by <span style="color:{ACCENT};font-weight:700;">Bhaskar Shivaji Kumbhar</span>
    &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp;
    Always consult a qualified healthcare professional
</div>
""", unsafe_allow_html=True)
