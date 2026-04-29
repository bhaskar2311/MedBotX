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

# ── Full CSS ──────────────────────────────────────────────────────────────────
if D:
    BG       = "#0b0f1a"
    BG2      = "#111827"
    BG3      = "#1a2235"
    CARD     = "#161d2e"
    BORDER   = "rgba(99,179,237,0.13)"
    TEXT     = "#e2e8f0"
    TEXT2    = "#94a3b8"
    INPUT_BG = "#1e293b"
    SIDE_BG  = "#0d1320"
    BOT_BG   = "#1a2235"
    BOT_BD   = "rgba(96,165,250,0.18)"
    MSG_USER = "#1d4ed8"
    CHIP_BG  = "#1e293b"
else:
    BG       = "#f0f4f8"
    BG2      = "#ffffff"
    BG3      = "#e8edf5"
    CARD     = "#ffffff"
    BORDER   = "rgba(59,130,246,0.18)"
    TEXT     = "#1a202c"
    TEXT2    = "#64748b"
    INPUT_BG = "#ffffff"
    SIDE_BG  = "#f8fafc"
    BOT_BG   = "#eff6ff"
    BOT_BD   = "rgba(59,130,246,0.18)"
    MSG_USER = "#2563eb"
    CHIP_BG  = "#e0eaff"

ACCENT  = "#3b82f6"
ACCENT2 = "#60a5fa"
SUCCESS = "#10b981"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

/* App */
.stApp {{ background: {BG} !important; }}
.main .block-container {{ padding: 1.5rem 2rem 1rem 2rem !important; max-width: 100% !important; }}

/* Hide chrome */
#MainMenu, footer, [data-testid="stToolbar"] {{ display: none !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: {SIDE_BG} !important; border-right: 1px solid {BORDER}; }}
[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
[data-testid="stSidebarContent"] {{ padding: 1.2rem 1rem !important; }}

/* Logo */
.logo-card {{
    background: linear-gradient(135deg,#1e3a5f,#1d4ed8 60%,#3b82f6);
    border-radius: 18px; padding: 22px 16px; text-align: center;
    margin-bottom: 18px;
    box-shadow: 0 8px 32px rgba(59,130,246,0.28);
}}
.logo-card .logo-icon {{ font-size: 2.4rem; }}
.logo-card h2 {{
    color: #fff !important; font-size: 1.65rem !important;
    font-weight: 900 !important; margin: 6px 0 2px !important;
    letter-spacing: -0.8px;
}}
.logo-card .sub {{ color: rgba(255,255,255,0.75) !important; font-size: 0.76rem !important; }}
.badge {{
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.4);
    border-radius: 20px; padding: 3px 10px; font-size: 0.7rem !important;
    color: #6ee7b7 !important; margin-top: 10px;
}}
.bdot {{ width:6px; height:6px; background:#10b981; border-radius:50%;
         display:inline-block; animation: blink 1.8s infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}

/* Section header */
.sec {{ font-size:0.65rem !important; font-weight:700 !important;
        letter-spacing:1.4px !important; color:{TEXT2} !important;
        text-transform:uppercase !important; margin:14px 0 6px 0 !important; }}

/* User chip */
.uchip {{
    display:flex; align-items:center; gap:10px;
    background:{BG3}; border:1px solid {BORDER};
    border-radius:12px; padding:12px; margin-bottom:10px;
}}
.uav {{
    width:36px; height:36px; border-radius:10px;
    background:linear-gradient(135deg,#1d4ed8,#7c3aed);
    display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:1rem; color:#fff; flex-shrink:0;
}}
.uname {{ font-weight:700; font-size:0.88rem; color:{TEXT}; }}
.urole {{ font-size:0.7rem; color:{SUCCESS}; font-weight:500; }}

/* Form inputs */
.stTextInput > label, .stTextArea > label,
.stNumberInput > label, .stSelectbox > label {{
    font-size:0.77rem !important; font-weight:600 !important;
    color:{TEXT2} !important; margin-bottom:2px !important;
}}
.stTextInput input, .stTextArea textarea, .stNumberInput input {{
    background:{INPUT_BG} !important; border:1.5px solid {BORDER} !important;
    border-radius:10px !important; color:{TEXT} !important;
    font-size:0.88rem !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color:{ACCENT} !important;
    box-shadow:0 0 0 3px rgba(59,130,246,0.13) !important;
}}
.stSelectbox > div > div {{
    background:{INPUT_BG} !important; border:1.5px solid {BORDER} !important;
    border-radius:10px !important; color:{TEXT} !important;
}}

/* Buttons */
.stButton > button {{
    background:linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; font-size:0.87rem !important;
    padding:10px 20px !important; width:100% !important;
    box-shadow:0 4px 14px rgba(59,130,246,0.32) !important;
    transition:all 0.18s !important;
}}
.stButton > button:hover {{
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(59,130,246,0.42) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
    background:{BG3} !important; border:1px solid {BORDER} !important;
    border-radius:12px !important; overflow:hidden;
}}
[data-testid="stExpander"] summary {{
    font-weight:600 !important; font-size:0.84rem !important;
    color:{TEXT} !important; padding:12px 14px !important;
}}
[data-testid="stExpander"] summary:hover {{ background:rgba(59,130,246,0.06) !important; }}

/* ── Chat messages via st.chat_message ── */
[data-testid="stChatMessage"] {{
    background:transparent !important;
    border:none !important;
    padding: 4px 0 !important;
}}

/* Bot bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {{
    background: {BOT_BG} !important;
    border: 1px solid {BOT_BD} !important;
    border-radius: 0 16px 16px 16px !important;
    padding: 14px 18px !important;
    color: {TEXT} !important;
    font-size: 0.91rem !important;
    line-height: 1.75 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    max-width: 75%;
}}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {{
    background: linear-gradient(135deg,{MSG_USER},{ACCENT}) !important;
    border-radius: 16px 0 16px 16px !important;
    padding: 14px 18px !important;
    color: #fff !important;
    font-size: 0.91rem !important;
    line-height: 1.75 !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.3);
    max-width: 75%;
    margin-left: auto;
}}

/* Avatar icons */
[data-testid="chatAvatarIcon-assistant"] {{
    background: linear-gradient(135deg,#1e3a5f,#1d4ed8) !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-radius: 12px !important;
}}
[data-testid="chatAvatarIcon-user"] {{
    background: linear-gradient(135deg,#065f46,#059669) !important;
    border: 1px solid rgba(5,150,105,0.3) !important;
    border-radius: 12px !important;
}}

/* Chat message text color */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong {{
    color: inherit !important;
}}

/* Chat input */
[data-testid="stChatInput"] {{
    background: {INPUT_BG} !important;
    border: 2px solid {BORDER} !important;
    border-radius: 14px !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.12) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: {TEXT} !important; font-size:0.95rem !important;
    background:transparent !important;
}}
[data-testid="stChatInputSubmitButton"] button {{
    background: linear-gradient(135deg,#1d4ed8,{ACCENT}) !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.35) !important;
}}

/* KPI cards */
.kpi {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
    padding:16px; text-align:center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.kpi .ki {{ font-size:1.5rem; margin-bottom:6px; }}
.kpi .kv {{ font-size:1rem; font-weight:800; color:{TEXT}; }}
.kpi .kl {{ font-size:0.68rem; color:{TEXT2}; text-transform:uppercase;
             letter-spacing:0.6px; margin-top:2px; font-weight:500; }}

/* Top bar */
.topbar {{
    background:{BG2}; border:1px solid {BORDER}; border-radius:16px;
    padding:18px 24px; margin-bottom:20px;
    display:flex; align-items:center; justify-content:space-between;
}}
.topbar h1 {{
    color:{TEXT}; font-size:1.3rem; font-weight:800;
    margin:0; letter-spacing:-0.4px;
}}
.topbar p {{ color:{TEXT2}; font-size:0.78rem; margin:3px 0 0 0; }}

/* Welcome */
.welcome {{
    text-align:center; padding:40px 20px 20px;
}}
.welcome .wi {{ font-size:4rem; margin-bottom:14px;
               animation:float 3s ease-in-out infinite; display:block; }}
@keyframes float {{
    0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-8px)}}
}}
.welcome h2 {{
    font-size:1.8rem; font-weight:900; color:{TEXT};
    letter-spacing:-0.8px; margin-bottom:10px;
}}
.welcome p {{ color:{TEXT2}; font-size:0.92rem; max-width:480px;
              margin:0 auto 28px; line-height:1.8; }}
.chips {{
    display:grid; grid-template-columns:1fr 1fr;
    gap:10px; max-width:580px; margin:0 auto;
}}
.chip {{
    background:{CHIP_BG}; border:1px solid {BORDER};
    border-radius:12px; padding:12px 15px;
    font-size:0.82rem; color:{ACCENT2};
    text-align:left; line-height:1.5;
    transition:all 0.18s; cursor:pointer;
}}
.chip:hover {{
    background:rgba(59,130,246,0.1); border-color:{ACCENT};
    transform:translateY(-2px);
    box-shadow:0 4px 12px rgba(59,130,246,0.18);
}}

/* Disclaimer */
.disc {{
    background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.22);
    border-radius:10px; padding:10px 13px;
    font-size:0.73rem !important; color:#fbbf24 !important; line-height:1.6;
}}

/* Footer */
.footer {{
    text-align:center; padding:10px 0; margin-top:8px;
    font-size:0.71rem; color:{TEXT2};
    border-top:1px solid {BORDER};
}}
.footer b {{ color:{ACCENT2}; }}

hr {{ border-color:{BORDER} !important; margin:10px 0 !important; }}
::-webkit-scrollbar {{ width:4px; }}
::-webkit-scrollbar-thumb {{ background:rgba(59,130,246,0.22); border-radius:4px; }}

/* Alerts */
div[data-baseweb="notification"] {{ border-radius:10px !important; font-size:0.85rem !important; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def hdr():
    t = st.session_state.access_token
    return {"Authorization": f"Bearer {t}"} if t else {}

def post(ep, body, timeout=30):
    try:
        r = requests.post(f"{API_BASE}{ep}", json=body, headers=hdr(), timeout=timeout)
        r.raise_for_status(); return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Please start the backend server.")
    except requests.HTTPError as e:
        try:    detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        st.error(detail)
    return None

def get(ep):
    try:
        r = requests.get(f"{API_BASE}{ep}", headers=hdr(), timeout=15)
        r.raise_for_status(); return r.json()
    except: return None

def put(ep, body):
    try:
        r = requests.put(f"{API_BASE}{ep}", json=body, headers=hdr(), timeout=20)
        r.raise_for_status(); return r.json()
    except requests.HTTPError as e:
        try:    detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        st.error(detail)
    except: st.error("API error")
    return None

def ensure_session():
    if not st.session_state.session_id:
        d = post("/api/v1/chat/session/new", {})
        if d: st.session_state.session_id = d["session_id"]

def load_profile():
    d = get("/api/v1/memory/load")
    if d: st.session_state.medical_profile = d.get("medical_context", {})


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="logo-card">
        <div class="logo-icon">🏥</div>
        <h2>MedBotX</h2>
        <div class="sub">Advanced AI Medical Assistant</div>
        <div class="badge"><span class="bdot"></span> Online &amp; Ready</div>
    </div>
    """, unsafe_allow_html=True)

    # Dark / Light toggle
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(f'<p style="font-size:0.75rem;color:{TEXT2};margin:8px 0 4px;">🌙 Dark &nbsp; ☀️ Light</p>', unsafe_allow_html=True)
    with col_b:
        new_dark = st.toggle("", value=D, key="theme_toggle", label_visibility="collapsed")
        if new_dark != D:
            st.session_state.dark_mode = new_dark
            st.rerun()

    st.divider()

    # ── AUTH ──────────────────────────────────────────────────────────────────
    if not st.session_state.username:
        st.markdown(f'<p class="sec">Account</p>', unsafe_allow_html=True)
        mode = st.radio("mode", ["Guest", "Sign In", "Register"],
                        horizontal=True, label_visibility="collapsed")

        if mode == "Sign In":
            with st.form("lf"):
                un = st.text_input("Username", placeholder="your_username")
                pw = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Sign In →"):
                    if un and pw:
                        d = post("/api/v1/auth/login", {"username": un, "password": pw})
                        if d:
                            st.session_state.access_token = d["access_token"]
                            st.session_state.username = un
                            me = get("/api/v1/auth/me")
                            if me: st.session_state.user_id = me["id"]
                            load_profile()
                            st.success(f"Welcome back, {un}!")
                            st.rerun()
                    else:
                        st.warning("Fill in all fields.")

        elif mode == "Register":
            with st.form("rf"):
                un = st.text_input("Username", placeholder="choose_username")
                em = st.text_input("Email",    placeholder="you@email.com")
                pw = st.text_input("Password", type="password", placeholder="Min 8 characters")
                if st.form_submit_button("Create Account →"):
                    if un and em and pw:
                        d = post("/api/v1/auth/register",
                                 {"username": un, "email": em, "password": pw})
                        if d: st.success("✅ Account created! Now sign in.")
                    else:
                        st.warning("Fill in all fields.")
        else:
            st.info("💬 Guest mode — history is session only. Sign in to save everything permanently.")

    else:
        # User chip
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

        # ── Health Profile inside expander ────────────────────────────────────
        st.markdown(f'<p class="sec">🩺 Health Profile</p>', unsafe_allow_html=True)

        prof = st.session_state.medical_profile

        # Summary outside expander
        if prof:
            items = []
            if prof.get("age"):         items.append(f"Age {prof['age']}")
            if prof.get("blood_type"):  items.append(f"Blood {prof['blood_type']}")
            if prof.get("allergies"):   items.append(f"{len(prof['allergies'])} allerg.")
            if prof.get("medications"): items.append(f"{len(prof['medications'])} meds")
            if items:
                st.markdown(f'<p style="font-size:0.73rem;color:{TEXT2};margin:0 0 8px 0;">{" · ".join(items)}</p>',
                            unsafe_allow_html=True)

        with st.expander("✏️ Edit Health Profile", expanded=False):
            with st.form("hf", clear_on_submit=False):
                age   = st.number_input("Age", min_value=0, max_value=120,
                                        value=int(prof.get("age") or 0))
                blood = st.selectbox("Blood Type",
                    ["","A+","A-","B+","B-","AB+","AB-","O+","O-"],
                    index=(["","A+","A-","B+","B-","AB+","AB-","O+","O-"].index(
                        prof.get("blood_type","") or ""
                    ) if (prof.get("blood_type","") or "") in
                          ["","A+","A-","B+","B-","AB+","AB-","O+","O-"] else 0))
                allerg = st.text_area("Allergies (comma-separated)",
                    value=", ".join(prof.get("allergies") or []),
                    placeholder="e.g. Penicillin, Peanuts", height=60)
                conds = st.text_area("Medical Conditions",
                    value=", ".join(prof.get("conditions") or []),
                    placeholder="e.g. Diabetes Type 2", height=60)
                meds  = st.text_area("Current Medications",
                    value=", ".join(prof.get("medications") or []),
                    placeholder="e.g. Metformin 500mg", height=60)
                notes = st.text_area("Notes",
                    value=prof.get("notes") or "",
                    placeholder="Any other health notes...", height=50)

                if st.form_submit_button("💾 Save Profile"):
                    payload = {
                        "age":         int(age) if age and age > 0 else None,
                        "blood_type":  blood or None,
                        "allergies":   [a.strip() for a in allerg.split(",") if a.strip()],
                        "conditions":  [c.strip() for c in conds.split(",")  if c.strip()],
                        "medications": [m.strip() for m in meds.split(",")   if m.strip()],
                        "notes":       notes.strip() or None,
                    }
                    r = put("/api/v1/memory/medical-context", payload)
                    if r:
                        st.session_state.medical_profile = r.get("medical_context", payload)
                        st.success("✅ Profile saved!")

    st.divider()

    # Disclaimer + footer
    st.markdown(f"""
    <div class="disc">
        ⚠️ <strong>Medical Disclaimer</strong><br>
        MedBotX provides general health information only —
        not a substitute for professional medical advice.
        Always consult a qualified doctor.
    </div>
    <div class="footer" style="margin-top:12px;">
        Developed by <b>Bhaskar Shivaji Kumbhar</b><br>
        <span style="font-size:0.63rem;opacity:0.5;">MedBotX v1.0.0 · 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

user_label = st.session_state.username or "Guest"
mem_label  = "Permanent DB" if st.session_state.access_token else "Session only"
q_count    = len([m for m in st.session_state.messages if m["role"] == "human"])

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div>
        <h1>🏥 MedBotX &nbsp;·&nbsp; AI Medical Assistant</h1>
        <p>Ask about symptoms, medications, conditions, nutrition, or general wellness</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi"><div class="ki">👤</div><div class="kv">{user_label}</div><div class="kl">User</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi"><div class="ki">🧠</div><div class="kv">{mem_label}</div><div class="kl">Memory</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi"><div class="ki">💬</div><div class="kv">{q_count}</div><div class="kl">Questions</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi"><div class="ki">🟢</div><div class="kv">Online</div><div class="kl">Status</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Chat area ─────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
        <span class="wi">🩺</span>
        <h2>How can I help you today?</h2>
        <p>I'm MedBotX — your AI-powered medical information assistant.<br>
        Ask me about symptoms, medications, health conditions, nutrition, or wellness tips.</p>
        <div class="chips">
            <div class="chip">🤒 What are the symptoms of Type 2 Diabetes?</div>
            <div class="chip">💊 What are common side effects of Ibuprofen?</div>
            <div class="chip">❤️ How to lower blood pressure naturally?</div>
            <div class="chip">😴 Why do I feel tired all the time?</div>
            <div class="chip">🧬 What is cholesterol and why does it matter?</div>
            <div class="chip">🍎 Best diet for someone with hypertension?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render all messages using st.chat_message (handles markdown perfectly)
    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "ai" else "user"
        avatar = "🤖" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])
            st.caption(msg.get("timestamp", ""))

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask your medical question here...", key="chat_input")

if user_input and user_input.strip():
    ensure_session()
    ts = datetime.now().strftime("%I:%M %p")

    st.session_state.messages.append({
        "role": "human", "content": user_input.strip(), "timestamp": ts,
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input.strip())
        st.caption(ts)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(""):
            data = post("/api/v1/chat/", {
                "message": user_input.strip(),
                "session_id": st.session_state.session_id,
            })
        if data:
            st.session_state.session_id = data["session_id"]
            ai_ts = datetime.now().strftime("%I:%M %p")
            st.markdown(data["response"])
            st.caption(ai_ts)
            st.session_state.messages.append({
                "role": "ai", "content": data["response"], "timestamp": ai_ts,
            })
        else:
            err = "I'm having trouble connecting right now. Please try again."
            st.markdown(err)
            st.session_state.messages.append({
                "role": "ai", "content": err, "timestamp": ts,
            })

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    MedBotX &nbsp;·&nbsp; Developed by <b>Bhaskar Shivaji Kumbhar</b>
    &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp;
    Always consult a qualified healthcare professional
</div>
""", unsafe_allow_html=True)
