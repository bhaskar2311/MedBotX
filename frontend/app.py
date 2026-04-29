"""
MedBotX - Streamlit Frontend
Developed by Bhaskar Shivaji Kumbhar
"""
import os
import requests
import streamlit as st
from datetime import datetime

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedBotX — AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Background ── */
.stApp {
    background: #0a0e1a;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e1a 100%);
    border-right: 1px solid rgba(99,179,237,0.12);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Sidebar Logo Area ── */
.sidebar-logo {
    background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
    border: 1px solid rgba(99,179,237,0.2);
}
.sidebar-logo h2 {
    color: #fff !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.5px;
}
.sidebar-logo p {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.78rem !important;
    margin: 0 !important;
}

/* ── Sidebar status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(72,187,120,0.15);
    border: 1px solid rgba(72,187,120,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: #68d391 !important;
    margin-top: 10px;
}

/* ── Sidebar auth card ── */
.auth-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}

/* ── Forms ── */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(99,179,237,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,179,237,0.1) !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label {
    color: #a0aec0 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2b6cb0, #4299e1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 20px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(66,153,225,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(66,153,225,0.4) !important;
}

/* ── Main Chat Area ── */
.main-wrapper {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #0a0e1a;
}

/* ── Top Header Bar ── */
.top-header {
    background: linear-gradient(90deg, #0d1117 0%, #0f1923 100%);
    border-bottom: 1px solid rgba(99,179,237,0.1);
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.top-header h1 {
    color: #e2e8f0;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.3px;
}
.top-header .subtitle {
    color: #718096;
    font-size: 0.8rem;
    margin: 2px 0 0 0;
}

/* ── Stats Bar ── */
.stats-bar {
    display: flex;
    gap: 16px;
    padding: 14px 32px;
    background: rgba(255,255,255,0.02);
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: #a0aec0;
}
.stat-item .val {
    color: #63b3ed;
    font-weight: 600;
}

/* ── Chat Messages ── */
.chat-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
}

.msg-wrapper {
    display: flex;
    margin-bottom: 20px;
    gap: 12px;
    animation: fadeSlide 0.3s ease;
}
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-wrapper.user-msg { flex-direction: row-reverse; }

.avatar-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.avatar-circle.bot-av {
    background: linear-gradient(135deg, #1a365d, #2b6cb0);
    border: 1px solid rgba(99,179,237,0.3);
}
.avatar-circle.user-av {
    background: linear-gradient(135deg, #276749, #38a169);
    border: 1px solid rgba(72,187,120,0.3);
}

.msg-bubble {
    max-width: 68%;
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 0.9rem;
    line-height: 1.7;
}
.msg-bubble.bot-bubble {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(99,179,237,0.15);
    border-top-left-radius: 4px;
    color: #e2e8f0;
}
.msg-bubble.user-bubble {
    background: linear-gradient(135deg, #2b6cb0, #3182ce);
    border: 1px solid rgba(99,179,237,0.2);
    border-top-right-radius: 4px;
    color: white;
}
.msg-time {
    font-size: 0.68rem;
    opacity: 0.5;
    margin-top: 6px;
}

/* ── Welcome screen ── */
.welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
}
.welcome-screen .big-icon {
    font-size: 4rem;
    margin-bottom: 16px;
    filter: drop-shadow(0 0 30px rgba(66,153,225,0.4));
}
.welcome-screen h2 {
    color: #e2e8f0;
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}
.welcome-screen p {
    color: #718096;
    font-size: 0.95rem;
    max-width: 480px;
    line-height: 1.7;
    margin-bottom: 30px;
}
.suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
}
.chip {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.82rem;
    color: #90cdf4;
    cursor: pointer;
    transition: all 0.2s;
}
.chip:hover {
    background: rgba(99,179,237,0.1);
    border-color: rgba(99,179,237,0.4);
}

/* ── Input Bar ── */
.input-bar {
    background: rgba(255,255,255,0.03);
    border-top: 1px solid rgba(255,255,255,0.07);
    padding: 16px 32px;
}
.input-bar .stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(99,179,237,0.25) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
    padding: 14px 18px !important;
}

/* ── Footer ── */
.footer-bar {
    text-align: center;
    padding: 8px;
    font-size: 0.72rem;
    color: #4a5568;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.footer-bar span { color: #4299e1; font-weight: 600; }

/* ── Disclaimer box ── */
.disclaimer {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.76rem;
    color: #f6ad55;
    line-height: 1.5;
}

/* ── Success / error ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 10px !important;
    font-size: 0.85rem !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Radio buttons ── */
.stRadio label { color: #a0aec0 !important; font-size: 0.85rem !important; }
.stRadio div[role="radiogroup"] label { padding: 4px 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,179,237,0.2); border-radius: 4px; }

/* ── Metric tweaks ── */
[data-testid="stMetricValue"] { color: #63b3ed !important; font-size: 1.1rem !important; }
[data-testid="stMetricLabel"] { color: #718096 !important; font-size: 0.78rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {
    "messages": [], "session_id": None,
    "access_token": None, "username": None, "auth_mode": "guest",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def auth_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def api_post(endpoint, payload, timeout=30):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=auth_headers(), timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the MedBotX API. Make sure the backend is running.")
        return None
    except requests.HTTPError as e:
        try:
            detail = e.response.json().get("detail", "Unknown error")
        except Exception:
            detail = str(e)
        st.error(f"Error: {detail}")
        return None

def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=auth_headers(), params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def ensure_session():
    if not st.session_state.session_id:
        data = api_post("/api/v1/chat/session/new", {})
        if data:
            st.session_state.session_id = data["session_id"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🏥 MedBotX</h2>
        <p>AI Medical Assistant</p>
        <div class="status-pill">● Online</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Auth ──────────────────────────────────────────────────────────────────
    if not st.session_state.username:
        tab = st.radio("", ["Guest", "Sign In", "Register"], horizontal=True, label_visibility="collapsed")

        if tab == "Sign In":
            with st.form("login_form", clear_on_submit=False):
                un = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In →"):
                    if un and pw:
                        data = api_post("/api/v1/auth/login", {"username": un, "password": pw})
                        if data:
                            st.session_state.access_token = data["access_token"]
                            st.session_state.username = un
                            st.session_state.auth_mode = "authenticated"
                            st.success(f"Welcome back, {un}!")
                            st.rerun()
                    else:
                        st.warning("Please fill in all fields.")

        elif tab == "Register":
            with st.form("register_form", clear_on_submit=False):
                un = st.text_input("Username")
                em = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Create Account →"):
                    if un and em and pw:
                        data = api_post("/api/v1/auth/register", {"username": un, "email": em, "password": pw})
                        if data:
                            st.success("Account created! Sign in now.")
                    else:
                        st.warning("Please fill in all fields.")
        else:
            st.caption("You're chatting as a guest. Sign in to save your history and medical profile across sessions.")

    else:
        st.markdown(f"""
        <div class="auth-card">
            <div style="color:#68d391;font-weight:600;font-size:0.9rem;">✓ {st.session_state.username}</div>
            <div style="color:#718096;font-size:0.75rem;margin-top:3px;">Authenticated · Memory enabled</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out"):
            for k in ["access_token", "username", "messages", "session_id"]:
                st.session_state[k] = None if k != "messages" else []
            st.rerun()

    st.divider()

    # ── Medical Profile ───────────────────────────────────────────────────────
    if st.session_state.access_token:
        st.markdown("**🩺 Health Profile**")
        with st.expander("Update my profile"):
            with st.form("med_profile"):
                age    = st.number_input("Age", 0, 120, 0, label_visibility="visible")
                blood  = st.selectbox("Blood Type", ["", "A+","A-","B+","B-","AB+","AB-","O+","O-"])
                allerg = st.text_area("Allergies", placeholder="e.g. Penicillin, Peanuts", height=70)
                conds  = st.text_area("Conditions", placeholder="e.g. Diabetes Type 2", height=70)
                meds   = st.text_area("Medications", placeholder="e.g. Metformin 500mg", height=70)
                if st.form_submit_button("Save Profile"):
                    me = api_get("/api/v1/auth/me")
                    if me:
                        payload = {
                            "user_id": me["id"],
                            "age": age if age > 0 else None,
                            "blood_type": blood or None,
                            "allergies":   [a.strip() for a in allerg.split(",") if a.strip()],
                            "conditions":  [c.strip() for c in conds.split(",")  if c.strip()],
                            "medications": [m.strip() for m in meds.split(",")   if m.strip()],
                        }
                        r = api_post("/api/v1/memory/medical-context", payload)
                        if r:
                            st.success("Profile saved!")
        st.divider()

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="disclaimer">
        ⚠️ MedBotX provides general health information only — not a substitute for professional medical advice.
        Always consult a qualified doctor.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:16px; text-align:center; font-size:0.72rem; color:#4a5568;">
        Developed by <span style="color:#4299e1;font-weight:600;">Bhaskar Shivaji Kumbhar</span>
    </div>
    """, unsafe_allow_html=True)


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <div>
        <h1>🏥 MedBotX — AI Medical Assistant</h1>
        <p class="subtitle">Ask me about symptoms, medications, conditions, or general health advice</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Stats row
mem_status = "Permanent (DB)" if st.session_state.access_token else "Session only"
user_label = st.session_state.username or "Guest"
msg_count  = len(st.session_state.messages)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("User", user_label)
with col2:
    st.metric("Memory", mem_status)
with col3:
    st.metric("Messages", msg_count)
with col4:
    st.metric("Status", "🟢 Connected")

st.divider()

# ── Chat Messages ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-screen">
        <div class="big-icon">🩺</div>
        <h2>How can I help you today?</h2>
        <p>I can answer questions about symptoms, medications, health conditions,
        nutrition, and general wellness. I'll always encourage you to see a doctor
        for personal medical decisions.</p>
        <div class="suggestion-chips">
            <span class="chip">💊 What are common side effects of ibuprofen?</span>
            <span class="chip">🤒 What are symptoms of Type 2 diabetes?</span>
            <span class="chip">❤️ How do I lower my blood pressure naturally?</span>
            <span class="chip">😴 Why am I always feeling tired?</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("timestamp", "")
        if role == "ai":
            st.markdown(f"""
            <div class="msg-wrapper">
                <div class="avatar-circle bot-av">🤖</div>
                <div class="msg-bubble bot-bubble">
                    {content}
                    <div class="msg-time">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-wrapper user-msg">
                <div class="avatar-circle user-av">👤</div>
                <div class="msg-bubble user-bubble">
                    {content}
                    <div class="msg-time">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.divider()
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([9, 1])
    with cols[0]:
        user_input = st.text_input(
            "message",
            placeholder="Type your health question here...",
            label_visibility="collapsed",
        )
    with cols[1]:
        send = st.form_submit_button("Send")

if send and user_input.strip():
    ensure_session()
    st.session_state.messages.append({
        "role": "human",
        "content": user_input.strip(),
        "timestamp": datetime.now().strftime("%I:%M %p"),
    })
    with st.spinner(""):
        data = api_post("/api/v1/chat/", {
            "message": user_input.strip(),
            "session_id": st.session_state.session_id,
        })
    if data:
        st.session_state.session_id = data["session_id"]
        st.session_state.messages.append({
            "role": "ai",
            "content": data["response"],
            "timestamp": datetime.now().strftime("%I:%M %p"),
        })
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    MedBotX · Developed by <span>Bhaskar Shivaji Kumbhar</span> ·
    For informational purposes only · Always consult a healthcare professional
</div>
""", unsafe_allow_html=True)
