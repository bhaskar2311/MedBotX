"""
MedBotX - Streamlit Frontend
Developed by Bhaskar Shivaji Kumbhar
"""
import os
import time
import requests
import streamlit as st
from datetime import datetime

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedBotX — AI Medical Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/BhaskarKumbhar/MedBotX",
        "About": "MedBotX — Advanced Medical Chatbot with Memory\nDeveloped by Bhaskar Shivaji Kumbhar",
    },
)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header Banner ── */
    .medbotx-header {
        background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 50%, #3a86ff 100%);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(58,134,255,0.25);
        color: white;
    }
    .medbotx-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 4px 0;
        letter-spacing: -0.5px;
    }
    .medbotx-header p {
        font-size: 0.95rem;
        opacity: 0.88;
        margin: 0;
    }
    .medbotx-header .badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        margin-top: 10px;
    }

    /* ── Chat Bubbles ── */
    .chat-container {
        max-height: 520px;
        overflow-y: auto;
        padding: 8px 4px;
        scroll-behavior: smooth;
    }
    .msg-row {
        display: flex;
        margin-bottom: 16px;
        gap: 10px;
        align-items: flex-start;
    }
    .msg-row.user { flex-direction: row-reverse; }

    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    .avatar.bot  { background: linear-gradient(135deg,#0f4c75,#3a86ff); }
    .avatar.user { background: linear-gradient(135deg,#2d6a4f,#52b788); }

    .bubble {
        max-width: 72%;
        padding: 13px 18px;
        border-radius: 16px;
        font-size: 0.92rem;
        line-height: 1.65;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .bubble.bot {
        background: #f0f7ff;
        border: 1px solid #c9e0ff;
        border-top-left-radius: 4px;
        color: #1a1a2e;
    }
    .bubble.user {
        background: linear-gradient(135deg,#2d6a4f,#52b788);
        color: white;
        border-top-right-radius: 4px;
    }
    .bubble .ts {
        font-size: 0.72rem;
        opacity: 0.6;
        margin-top: 6px;
    }

    /* ── Sidebar Card ── */
    .sidebar-card {
        background: linear-gradient(135deg,#0f4c75,#1b6ca8);
        border-radius: 12px;
        padding: 16px;
        color: white;
        margin-bottom: 16px;
    }
    .sidebar-card h4 { margin: 0 0 4px 0; font-size: 1rem; }
    .sidebar-card p  { margin: 0; font-size: 0.8rem; opacity: 0.85; }

    /* ── Developer Footer ── */
    .dev-footer {
        text-align: center;
        color: #888;
        font-size: 0.78rem;
        padding: 12px 0 0 0;
        border-top: 1px solid #eee;
        margin-top: 20px;
    }
    .dev-footer span { color: #3a86ff; font-weight: 600; }

    /* ── Alert boxes ── */
    .info-box {
        background: #e8f4fd;
        border-left: 4px solid #3a86ff;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.87rem;
        color: #1a3a5c;
        margin-bottom: 12px;
    }

    /* ── Input area ── */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #c9e0ff;
        padding: 12px 16px;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3a86ff;
        box-shadow: 0 0 0 3px rgba(58,134,255,0.15);
    }
    .stButton button {
        background: linear-gradient(135deg,#0f4c75,#3a86ff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 0.9rem;
        width: 100%;
        transition: opacity .2s;
    }
    .stButton button:hover { opacity: 0.88; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session State Defaults ────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "session_id": None,
    "access_token": None,
    "refresh_token": None,
    "username": None,
    "user_id": None,
    "auth_mode": "guest",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def auth_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def api_post(endpoint: str, payload: dict, timeout: int = 30) -> dict | None:
    try:
        r = requests.post(
            f"{API_BASE}{endpoint}",
            json=payload,
            headers=auth_headers(),
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to MedBotX API. Is the backend running?")
        return None
    except requests.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.json().get('detail', 'Unknown error')}")
        return None


def api_get(endpoint: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(
            f"{API_BASE}{endpoint}",
            headers=auth_headers(),
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to MedBotX API. Is the backend running?")
        return None
    except requests.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.json().get('detail', 'Unknown error')}")
        return None


def ensure_session():
    if not st.session_state.session_id:
        data = api_post("/api/v1/chat/session/new", {})
        if data:
            st.session_state.session_id = data["session_id"]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-card"><h4>🏥 MedBotX</h4>'
        '<p>Advanced Medical Chatbot with Memory</p></div>',
        unsafe_allow_html=True,
    )

    # Auth section
    st.markdown("### 🔐 Account")
    auth_tab = st.radio("Mode", ["Guest", "Login", "Register"], horizontal=True, label_visibility="collapsed")

    if auth_tab == "Login":
        with st.form("login_form"):
            un = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                data = api_post("/api/v1/auth/login", {"username": un, "password": pw})
                if data:
                    st.session_state.access_token = data["access_token"]
                    st.session_state.refresh_token = data["refresh_token"]
                    st.session_state.username = un
                    st.session_state.auth_mode = "authenticated"
                    st.success(f"Welcome back, {un}!")
                    st.rerun()

    elif auth_tab == "Register":
        with st.form("register_form"):
            un = st.text_input("Username")
            em = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Create Account"):
                data = api_post("/api/v1/auth/register", {"username": un, "email": em, "password": pw})
                if data:
                    st.success("Account created! Please sign in.")

    if st.session_state.username:
        st.markdown(f"✅ **Signed in as:** `{st.session_state.username}`")
        if st.button("Sign Out"):
            for k in ["access_token", "refresh_token", "username", "user_id", "messages", "session_id"]:
                st.session_state[k] = None if "token" in k or k == "session_id" else ([] if k == "messages" else None)
            st.rerun()

    st.divider()

    # Medical Profile (authenticated only)
    if st.session_state.access_token:
        st.markdown("### 🩺 Medical Profile")
        with st.expander("Update Health Info"):
            with st.form("med_profile"):
                age = st.number_input("Age", min_value=0, max_value=120, value=0)
                blood = st.selectbox("Blood Type", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                allergies = st.text_area("Allergies (comma-separated)")
                conditions = st.text_area("Medical Conditions (comma-separated)")
                medications = st.text_area("Current Medications (comma-separated)")
                if st.form_submit_button("Save Profile"):
                    me = api_get("/api/v1/auth/me")
                    if me:
                        payload = {
                            "user_id": me["id"],
                            "age": age if age > 0 else None,
                            "blood_type": blood or None,
                            "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                            "conditions": [c.strip() for c in conditions.split(",") if c.strip()],
                            "medications": [m.strip() for m in medications.split(",") if m.strip()],
                        }
                        r = api_post("/api/v1/memory/medical-context", payload)
                        if r:
                            st.success("Profile saved!")

    st.divider()
    st.markdown("### ⚠️ Disclaimer")
    st.caption(
        "MedBotX provides general medical information only. "
        "It does NOT replace professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider."
    )

    st.markdown(
        '<div class="dev-footer">Developed by <span>Bhaskar Shivaji Kumbhar</span></div>',
        unsafe_allow_html=True,
    )


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="medbotx-header">
        <h1>🏥 MedBotX</h1>
        <p>Advanced AI-Powered Medical Chatbot with Contextual Memory</p>
        <span class="badge">Powered by GPT-4o + LangChain</span>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Model", "GPT-4o")
with col2:
    st.metric("Memory", "Enabled" if st.session_state.access_token else "Session Only")
with col3:
    st.metric("Status", "🟢 Online")

st.divider()

st.markdown(
    '<div class="info-box">💡 Ask me about symptoms, medications, health conditions, nutrition, or general wellness. '
    'I\'ll always remind you to consult a doctor for personal medical decisions.</div>',
    unsafe_allow_html=True,
)

# ── Chat Display ──────────────────────────────────────────────────────────────
chat_area = st.container()

with chat_area:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        ts = msg.get("timestamp", "")

        if role == "ai":
            st.markdown(
                f'<div class="msg-row"><div class="avatar bot">🤖</div>'
                f'<div class="bubble bot">{content}<div class="ts">{ts}</div></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-row user"><div class="avatar user">👤</div>'
                f'<div class="bubble user">{content}<div class="ts">{ts}</div></div></div>',
                unsafe_allow_html=True,
            )

# ── Input Area ────────────────────────────────────────────────────────────────
st.divider()
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([8, 2])
    with cols[0]:
        user_input = st.text_input(
            "Your message",
            placeholder="e.g. What are the symptoms of diabetes?",
            label_visibility="collapsed",
        )
    with cols[1]:
        submitted = st.form_submit_button("Send 💬")

if submitted and user_input.strip():
    ensure_session()

    st.session_state.messages.append({
        "role": "human",
        "content": user_input.strip(),
        "timestamp": datetime.now().strftime("%H:%M"),
    })

    with st.spinner("MedBotX is thinking..."):
        payload = {
            "message": user_input.strip(),
            "session_id": st.session_state.session_id,
        }
        data = api_post("/api/v1/chat/", payload)

    if data:
        st.session_state.session_id = data["session_id"]
        st.session_state.messages.append({
            "role": "ai",
            "content": data["response"],
            "timestamp": datetime.now().strftime("%H:%M"),
        })

    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="dev-footer" style="margin-top:32px;">'
    'MedBotX v1.0.0 · Developed by <span>Bhaskar Shivaji Kumbhar</span> · '
    'For informational purposes only · Always consult a healthcare professional'
    '</div>',
    unsafe_allow_html=True,
)
