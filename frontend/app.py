"""
MedBotX – Dark Professional UI (Dark mode only)
Developed by Bhaskar Shivaji Kumbhar
"""
import os, re, requests
import streamlit as st
from datetime import datetime

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="MedBotX — AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

for k, v in {
    "messages": [], "session_id": None,
    "access_token": None, "username": None,
    "user_id": None, "medical_profile": {},
    "chat_history": [],   # list of past sessions: [{title, messages, ts}]
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── App background ── */
.stApp, [data-testid="stAppViewContainer"] { background: #0b0f1a !important; }
.main .block-container { padding: 1.4rem 2rem 0.5rem !important; max-width: 100% !important; }
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1320 !important;
    border-right: 1px solid #1a2a45;
}
[data-testid="stSidebarContent"] { padding: 1rem 0.9rem !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Logo ── */
.logo-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 55%, #3b82f6 100%);
    border-radius: 18px; padding: 22px 16px 18px; text-align: center;
    margin-bottom: 16px; box-shadow: 0 8px 30px rgba(59,130,246,0.28);
    border: 1px solid rgba(255,255,255,0.08);
}
.logo-card .licon { font-size: 2.3rem; display: block; margin-bottom: 6px; }
.logo-card .lname {
    color: #fff !important; font-size: 1.6rem !important;
    font-weight: 900 !important; letter-spacing: -0.8px; display: block;
}
.logo-card .lsub {
    color: rgba(255,255,255,0.68) !important;
    font-size: 0.73rem !important; display: block; margin-top: 2px;
}
.logo-card .badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,0.18); border: 1px solid rgba(16,185,129,0.38);
    border-radius: 20px; padding: 3px 11px; margin-top: 11px;
    font-size: 0.69rem !important; color: #6ee7b7 !important; font-weight: 600;
}
.bdot {
    width: 6px; height: 6px; background: #10b981; border-radius: 50%;
    display: inline-block; animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.35;transform:scale(1.4)} }

/* ── Section label ── */
.slbl {
    font-size: 0.63rem !important; font-weight: 700 !important;
    letter-spacing: 1.3px !important; color: #64748b !important;
    text-transform: uppercase !important; display: block;
    margin: 14px 0 7px !important;
}

/* ── User chip ── */
.uchip {
    display: flex; align-items: center; gap: 10px;
    background: #111827; border: 1px solid #1a2a45;
    border-radius: 12px; padding: 11px 13px; margin-bottom: 10px;
}
.uav {
    width: 36px; height: 36px; border-radius: 9px;
    background: linear-gradient(135deg, #1d4ed8, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.95rem; color: #fff; flex-shrink: 0;
}
.uname { font-weight: 700; font-size: 0.88rem; color: #e2e8f0 !important; }
.urole { font-size: 0.69rem; color: #10b981 !important; font-weight: 600; margin-top: 1px; }

/* ── Inputs ── */
.stTextInput > label, .stTextArea > label,
.stNumberInput > label, .stSelectbox > label {
    font-size: 0.75rem !important; font-weight: 600 !important;
    color: #94a3b8 !important; margin-bottom: 4px !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: #1e293b !important; border: 1.5px solid #1e3a5f !important;
    border-radius: 9px !important; color: #e2e8f0 !important;
    font-size: 0.87rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #475569 !important;
}
.stSelectbox > div > div {
    background: #1e293b !important; border: 1.5px solid #1e3a5f !important;
    border-radius: 9px !important; color: #e2e8f0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: #fff !important; border: none !important;
    border-radius: 9px !important; font-weight: 700 !important;
    font-size: 0.86rem !important; padding: 10px 18px !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.35) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 24px rgba(59,130,246,0.45) !important;
    filter: brightness(1.1) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111827 !important; border: 1px solid #1a2a45 !important;
    border-radius: 11px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important; font-size: 0.83rem !important;
    color: #e2e8f0 !important; padding: 11px 14px !important;
}

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid #1a2a45 !important; margin: 10px 0 !important; }

/* ── Disclaimer ── */
.disc {
    background: rgba(245,158,11,0.09); border: 1px solid rgba(245,158,11,0.25);
    border-radius: 10px; padding: 10px 13px;
    font-size: 0.72rem !important; color: #fbbf24 !important; line-height: 1.65;
}

/* ── Dev footer ── */
.devfoot {
    text-align: center; padding: 10px 0 0;
    font-size: 0.68rem !important; color: #475569 !important;
}
.devfoot .dn { color: #60a5fa !important; font-weight: 700 !important; }

/* ════════════════════════════
   MAIN AREA
════════════════════════════ */

/* Topbar */
.topbar {
    background: #111827; border: 1px solid #1a2a45;
    border-radius: 14px; padding: 16px 22px; margin-bottom: 16px;
}
.topbar h1 {
    color: #e2e8f0 !important; font-size: 1.2rem !important;
    font-weight: 800 !important; margin: 0 !important; letter-spacing: -0.4px;
}
.topbar p { color: #64748b !important; font-size: 0.76rem !important; margin: 3px 0 0 !important; }

/* KPI */
.kcard {
    background: #111827; border: 1px solid #1a2a45;
    border-radius: 13px; padding: 16px 14px; text-align: center;
    transition: transform 0.15s;
}
.kcard:hover { transform: translateY(-2px); }
.ki { font-size: 1.4rem; display: block; margin-bottom: 5px; }
.kv { font-size: 0.95rem; font-weight: 800; color: #e2e8f0; display: block; }
.kl { font-size: 0.63rem; color: #64748b; text-transform: uppercase;
       letter-spacing: 0.7px; font-weight: 600; display: block; margin-top: 2px; }

/* Welcome */
.welcome {
    text-align: center; padding: 48px 20px 32px;
}
.wi { font-size: 4rem; display: block; margin-bottom: 14px;
      animation: fl 3s ease-in-out infinite; }
@keyframes fl { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-9px)} }
.wt { font-size: 1.8rem; font-weight: 900; color: #e2e8f0;
      letter-spacing: -0.8px; margin-bottom: 10px; }
.ws { color: #64748b; font-size: 0.9rem; max-width: 460px;
      margin: 0 auto 28px; line-height: 1.8; }
.chips { display: grid; grid-template-columns: 1fr 1fr;
         gap: 10px; max-width: 560px; margin: 0 auto; }
.chip {
    background: #111827; border: 1px solid #1a2a45;
    border-radius: 11px; padding: 12px 14px;
    font-size: 0.81rem; color: #93c5fd; text-align: left; line-height: 1.5;
    transition: all 0.16s;
}
.chip:hover { border-color: #3b82f6; transform: translateY(-1px);
              box-shadow: 0 4px 14px rgba(59,130,246,0.18); }

/* Chat bubbles */
.mwrap { display: flex; margin-bottom: 18px; gap: 12px; align-items: flex-start; }
.mwrap.umsg { flex-direction: row-reverse; }
.mav {
    width: 38px; height: 38px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0; box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}
.mav.bav { background: linear-gradient(135deg,#1e3a5f,#1d4ed8); border: 1px solid rgba(59,130,246,0.3); }
.mav.uav { background: linear-gradient(135deg,#065f46,#059669); border: 1px solid rgba(5,150,105,0.3); }
.mbub {
    max-width: 68%; padding: 14px 18px; border-radius: 16px;
    font-size: 0.9rem; line-height: 1.78;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}
.mbub.bb {
    background: #1a2235; border: 1px solid #1e3a5f;
    border-top-left-radius: 4px; color: #e2e8f0;
}
.mbub.ub {
    background: linear-gradient(135deg,#1d4ed8,#3b82f6);
    border-top-right-radius: 4px; color: #fff;
}
.mbub p { margin: 0 0 7px; color: inherit !important; }
.mbub p:last-child { margin-bottom: 0; }
.mbub ul, .mbub ol { padding-left: 18px; margin: 7px 0; }
.mbub li { margin-bottom: 4px; color: inherit !important; }
.mbub strong { font-weight: 700; color: inherit !important; }
.mbub em { font-style: italic; color: inherit !important; }
.mtime { font-size: 0.65rem; opacity: 0.45; margin-top: 8px; }

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #1e293b !important; color: #e2e8f0 !important;
    font-size: 0.93rem !important; font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #475569 !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
    border-radius: 8px !important;
    box-shadow: 0 3px 10px rgba(59,130,246,0.35) !important;
}

/* Alerts */
.stSuccess > div, .stError > div, .stWarning > div, .stInfo > div {
    border-radius: 10px !important; font-size: 0.84rem !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.22); border-radius: 4px; }

/* New Chat button */
.new-chat-btn > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.3) !important;
}
.new-chat-btn > button:hover {
    box-shadow: 0 6px 20px rgba(16,185,129,0.45) !important;
}

/* History items */
.hist-item {
    background: #111827; border: 1px solid #1a2a45;
    border-radius: 9px; padding: 9px 12px; margin-bottom: 6px;
    cursor: pointer; transition: all 0.15s;
}
.hist-item:hover { border-color: #3b82f6; background: #1a2235; }
.hist-title { font-size: 0.78rem; font-weight: 600; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hist-meta  { font-size: 0.66rem; color: #64748b; margin-top: 2px; }
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
    return None

def ensure_session():
    if not st.session_state.session_id:
        d = api_post("/api/v1/chat/session/new", {})
        if d: st.session_state.session_id = d["session_id"]

def load_profile():
    d = api_get("/api/v1/memory/load")
    if d: st.session_state.medical_profile = d.get("medical_context", {})

def md_to_html(text: str) -> str:
    """Convert markdown bold/lists to HTML for chat bubbles."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',   r'<em>\1</em>',         text)
    lines = text.split('\n')
    out, in_list, list_type = [], False, ''
    for line in lines:
        num = re.match(r'^(\d+)\.\s+(.*)', line)
        bul = re.match(r'^[-•*]\s+(.*)', line)
        if num:
            if list_type != 'ol':
                if in_list: out.append(f'</{list_type}>')
                out.append('<ol style="padding-left:18px;margin:8px 0 8px;">')
                list_type, in_list = 'ol', True
            out.append(f'<li style="margin-bottom:4px;">{num.group(2)}</li>')
        elif bul:
            if list_type != 'ul':
                if in_list: out.append(f'</{list_type}>')
                out.append('<ul style="padding-left:18px;margin:8px 0 8px;">')
                list_type, in_list = 'ul', True
            out.append(f'<li style="margin-bottom:4px;">{bul.group(1)}</li>')
        else:
            if in_list:
                out.append(f'</{list_type}>')
                in_list, list_type = False, ''
            if line.strip():
                out.append(f'<p style="margin:0 0 7px 0;">{line}</p>')
    if in_list: out.append(f'</{list_type}>')
    return '\n'.join(out)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    st.markdown("""
    <div class="logo-card">
        <span class="licon">🏥</span>
        <span class="lname">MedBotX</span>
        <span class="lsub">Advanced AI Medical Assistant</span>
        <div class="badge"><span class="bdot"></span>&nbsp;Online &amp; Ready</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── New Chat button ───────────────────────────────────────────────────────
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("✨ New Chat", key="new_chat_btn"):
        # Save current chat to history before clearing
        if st.session_state.messages:
            first_q = next(
                (m["content"] for m in st.session_state.messages if m["role"] == "human"),
                "Chat session"
            )
            title = first_q[:40] + ("..." if len(first_q) > 40 else "")
            st.session_state.chat_history.insert(0, {
                "title": title,
                "messages": st.session_state.messages.copy(),
                "ts": datetime.now().strftime("%b %d, %I:%M %p"),
                "count": len([m for m in st.session_state.messages if m["role"] == "human"]),
            })
            # Keep only last 10 sessions
            st.session_state.chat_history = st.session_state.chat_history[:10]
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chat History ──────────────────────────────────────────────────────────
    if st.session_state.chat_history:
        st.markdown('<span class="slbl">💬 Recent Chats</span>', unsafe_allow_html=True)
        for i, sess in enumerate(st.session_state.chat_history):
            col_h, col_x = st.columns([5, 1])
            with col_h:
                if st.button(f"🗨 {sess['title']}", key=f"hist_{i}",
                             help=f"{sess['count']} questions · {sess['ts']}",
                             use_container_width=True):
                    # Save current chat first
                    if st.session_state.messages:
                        first_q = next(
                            (m["content"] for m in st.session_state.messages if m["role"] == "human"),
                            "Chat session"
                        )
                        t = first_q[:40] + ("..." if len(first_q) > 40 else "")
                        st.session_state.chat_history.insert(0, {
                            "title": t,
                            "messages": st.session_state.messages.copy(),
                            "ts": datetime.now().strftime("%b %d, %I:%M %p"),
                            "count": len([m for m in st.session_state.messages if m["role"] == "human"]),
                        })
                    st.session_state.messages = sess["messages"].copy()
                    st.session_state.session_id = None
                    st.rerun()
            with col_x:
                if st.button("✕", key=f"del_{i}", help="Delete this chat"):
                    st.session_state.chat_history.pop(i)
                    st.rerun()

    st.divider()

    # ── AUTH ──────────────────────────────────────────────────────────────────
    if not st.session_state.username:
        st.markdown('<span class="slbl">Account</span>', unsafe_allow_html=True)
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
            st.info("💬 Guest mode — session only.\nSign in to save history & medical profile.")

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
                st.session_state[k] = [] if k=="messages" else ({} if k=="medical_profile" else None)
            st.rerun()

        st.divider()
        st.markdown('<span class="slbl">🩺 Health Profile</span>', unsafe_allow_html=True)

        prof = st.session_state.medical_profile or {}
        parts = []
        if prof.get("age"):         parts.append(f"Age {prof['age']}")
        if prof.get("blood_type"):  parts.append(f"Blood {prof['blood_type']}")
        if prof.get("conditions"):  parts.append(f"{len(prof['conditions'])} condition(s)")
        if prof.get("medications"): parts.append(f"{len(prof['medications'])} med(s)")
        if parts:
            st.markdown(f'<p style="font-size:0.72rem;color:#64748b;margin:0 0 8px;">{" · ".join(parts)}</p>',
                        unsafe_allow_html=True)

        BLOODS = ["","A+","A-","B+","B-","AB+","AB-","O+","O-"]
        saved  = prof.get("blood_type","") or ""
        bidx   = BLOODS.index(saved) if saved in BLOODS else 0

        with st.expander("✏️ Edit Health Profile", expanded=False):
            with st.form("hf", clear_on_submit=False):
                age   = st.number_input("Age", 0, 120, int(prof.get("age") or 0))
                blood = st.selectbox("Blood Type", BLOODS, index=bidx)
                allerg = st.text_area("Allergies (comma-separated)",
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
                            placeholder="Other health notes...", height=48)
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
    st.markdown("""
    <div class="disc">
        <strong>⚠️ Medical Disclaimer</strong><br>
        MedBotX provides general health information only —
        not a substitute for professional medical advice.
        Always consult a qualified doctor.
    </div>
    <div class="devfoot" style="margin-top:12px;">
        Developed by <span class="dn">Bhaskar Shivaji Kumbhar</span><br>
        <span style="font-size:0.61rem;opacity:0.4;">MedBotX v1.0.0 · 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
user_lbl = st.session_state.username or "Guest"
mem_lbl  = "Permanent" if st.session_state.access_token else "Session only"
q_cnt    = len([m for m in st.session_state.messages if m["role"] == "human"])

st.markdown(f"""
<div class="topbar">
    <h1>🏥 MedBotX &nbsp;·&nbsp; AI Medical Assistant</h1>
    <p>Ask about symptoms, medications, conditions, nutrition, or general wellness</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for col, icon, val, lbl in [
    (c1, "👤", user_lbl,    "User"),
    (c2, "🧠", mem_lbl,     "Memory"),
    (c3, "💬", str(q_cnt),  "Questions Asked"),
    (c4, "🟢", "Online",    "System Status"),
]:
    col.markdown(f"""
    <div class="kcard">
        <span class="ki">{icon}</span>
        <span class="kv">{val}</span>
        <span class="kl">{lbl}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
st.divider()

# ── Messages ──────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <span class="wi">🩺</span>
        <div class="wt">How can I help you today?</div>
        <p class="ws">
            I'm MedBotX — your AI-powered medical information assistant.<br>
            Ask about symptoms, medications, conditions, nutrition, or wellness.
        </p>
        <div class="chips">
            <div class="chip">🤒 Symptoms of Type 2 Diabetes?</div>
            <div class="chip">💊 Side effects of Ibuprofen?</div>
            <div class="chip">❤️ How to lower blood pressure naturally?</div>
            <div class="chip">😴 Why do I feel tired all the time?</div>
            <div class="chip">🧬 What is cholesterol and why it matters?</div>
            <div class="chip">🍎 Best diet for hypertension?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        html = md_to_html(msg["content"])
        ts   = msg.get("timestamp", "")
        if role == "ai":
            st.markdown(f"""
            <div class="mwrap">
                <div class="mav bav">🤖</div>
                <div class="mbub bb">{html}<div class="mtime">{ts}</div></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="mwrap umsg">
                <div class="mav uav">👤</div>
                <div class="mbub ub">{html}<div class="mtime">{ts}</div></div>
            </div>""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
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
            "content": "I'm having trouble connecting. Please try again.",
            "timestamp": ai_ts,
        })
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:10px 0 4px;font-size:0.69rem;color:#475569;
border-top:1px solid #1a2a45;margin-top:10px;">
    MedBotX &nbsp;·&nbsp;
    Developed by <span style="color:#60a5fa;font-weight:700;">Bhaskar Shivaji Kumbhar</span>
    &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp;
    Always consult a qualified healthcare professional
</div>
""", unsafe_allow_html=True)
