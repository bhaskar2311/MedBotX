"""
MedBotX — Advanced AI Medical Assistant
Developed by Bhaskar Shivaji Kumbhar
Direct OpenAI integration — no backend required
"""
import os, re, json
from datetime import datetime
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o")

st.set_page_config(
    page_title="MedBotX — AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────────────
DEFAULTS = {
    "messages":         [],    # current chat: [{role, content, ts}]
    "chat_history":     [],    # saved sessions: [{title, messages, ts, count}]
    "oai_history":      [],    # OpenAI format: [{role, content}]
    "drug_checks":      [],    # drug checker history: [{drugs, result, ts}]
    "health_profile": {
        "name": "", "age": "", "blood_type": "",
        "allergies": "", "conditions": "", "medications": "", "notes": "",
    },
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── System prompt ─────────────────────────────────────────────────────────────
def build_system_prompt():
    p = st.session_state.health_profile
    ctx_parts = []
    if p.get("name"):        ctx_parts.append(f"Patient name: {p['name']}")
    if p.get("age"):         ctx_parts.append(f"Age: {p['age']}")
    if p.get("blood_type"):  ctx_parts.append(f"Blood type: {p['blood_type']}")
    if p.get("allergies"):   ctx_parts.append(f"Known allergies: {p['allergies']}")
    if p.get("conditions"):  ctx_parts.append(f"Medical conditions: {p['conditions']}")
    if p.get("medications"): ctx_parts.append(f"Current medications: {p['medications']}")
    if p.get("notes"):       ctx_parts.append(f"Notes: {p['notes']}")
    ctx = ("\n\nPatient Health Context:\n" + "\n".join(ctx_parts)) if ctx_parts else ""

    return f"""You are MedBotX, an advanced AI-powered medical information assistant.
Developed by Bhaskar Shivaji Kumbhar.

Your role:
• Provide accurate, evidence-based medical information
• Answer questions about symptoms, medications, conditions, nutrition, and wellness
• Maintain context across the conversation
• Be compassionate, clear, and professional{ctx}

STRICT SAFETY RULES:
1. NEVER diagnose — always recommend consulting a licensed doctor
2. For ANY emergency symptoms (chest pain, difficulty breathing, stroke signs, severe bleeding) — IMMEDIATELY tell the user to call emergency services (112 / 911)
3. Never recommend stopping prescribed medications
4. End responses with a brief reminder to consult a healthcare professional when relevant

Format your responses clearly using bullet points and bold headings where helpful."""

# ── OpenAI call ───────────────────────────────────────────────────────────────
def ask_openai(user_message: str) -> str:
    if not API_KEY:
        return "⚠️ OpenAI API key not configured. Please add it to your .env file."
    client = OpenAI(api_key=API_KEY)
    messages = [{"role": "system", "content": build_system_prompt()}]
    messages += st.session_state.oai_history[-20:]
    messages.append({"role": "user", "content": user_message})
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1200,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error connecting to OpenAI: {str(e)}"

# ── Drug Interaction Checker ──────────────────────────────────────────────────
def check_drug_interactions(drugs: list[str]) -> dict:
    """Returns structured interaction analysis from OpenAI."""
    if not API_KEY:
        return {"error": "No API key configured."}
    client = OpenAI(api_key=API_KEY)
    drug_list = ", ".join(drugs)
    prompt = f"""You are a clinical pharmacology expert. Analyze drug interactions between: {drug_list}

For EACH pair of drugs that may interact, provide a JSON response in this exact format:
{{
  "summary": "One sentence overall safety summary",
  "severity": "SAFE" | "MILD" | "MODERATE" | "SEVERE",
  "interactions": [
    {{
      "drugs": ["Drug A", "Drug B"],
      "severity": "MILD" | "MODERATE" | "SEVERE",
      "effect": "What happens when taken together",
      "mechanism": "Why this interaction occurs",
      "recommendation": "What the patient should do"
    }}
  ],
  "general_advice": "Overall advice for the patient",
  "see_doctor": true | false
}}

If there are NO interactions, set severity to "SAFE" and interactions to [].
Respond ONLY with valid JSON. No markdown, no extra text."""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Could not parse response. Please try again.", "raw": raw}
    except Exception as e:
        return {"error": str(e)}

# ── Markdown renderer ─────────────────────────────────────────────────────────
def md_to_html(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)
    text = re.sub(r'`(.+?)`',       r'<code style="background:rgba(255,255,255,0.1);padding:1px 5px;border-radius:4px;font-size:0.85em;">\1</code>', text)
    lines = text.split('\n')
    out, in_list, ltype = [], False, ''
    for line in lines:
        num = re.match(r'^(\d+)\.\s+(.*)', line)
        bul = re.match(r'^[-•*]\s+(.*)', line)
        if num:
            if ltype != 'ol':
                if in_list: out.append(f'</{ltype}>')
                out.append('<ol style="padding-left:20px;margin:8px 0;">')
                ltype, in_list = 'ol', True
            out.append(f'<li style="margin-bottom:5px;">{num.group(2)}</li>')
        elif bul:
            if ltype != 'ul':
                if in_list: out.append(f'</{ltype}>')
                out.append('<ul style="padding-left:20px;margin:8px 0;">')
                ltype, in_list = 'ul', True
            out.append(f'<li style="margin-bottom:5px;">{bul.group(1)}</li>')
        else:
            if in_list:
                out.append(f'</{ltype}>')
                in_list, ltype = False, ''
            if line.strip():
                out.append(f'<p style="margin:0 0 8px 0;">{line}</p>')
    if in_list: out.append(f'</{ltype}>')
    return '\n'.join(out)

# ── Save current chat to history ──────────────────────────────────────────────
def save_current_chat():
    if not st.session_state.messages:
        return
    first_q = next(
        (m["content"] for m in st.session_state.messages if m["role"] == "human"), ""
    )
    if not first_q:
        return
    title = first_q[:45] + ("…" if len(first_q) > 45 else "")
    count = sum(1 for m in st.session_state.messages if m["role"] == "human")
    st.session_state.chat_history.insert(0, {
        "title":    title,
        "messages": st.session_state.messages.copy(),
        "oai":      st.session_state.oai_history.copy(),
        "ts":       datetime.now().strftime("%b %d, %I:%M %p"),
        "count":    count,
    })
    st.session_state.chat_history = st.session_state.chat_history[:15]

def start_new_chat():
    save_current_chat()
    st.session_state.messages    = []
    st.session_state.oai_history = []
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background: #060b14 !important;
}
.main .block-container {
    padding: 0 !important; max-width: 100% !important;
}
#MainMenu, footer, [data-testid="stToolbar"],
header[data-testid="stHeader"] { display: none !important; }

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {
    background: #080d18 !important;
    border-right: 1px solid #0f1e35 !important;
    width: 290px !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }
.sidebar-inner { padding: 18px 14px; }

/* Logo */
.logo-block {
    background: linear-gradient(140deg,#0a2342 0%,#0f3876 40%,#1a5fb4 100%);
    border-radius: 20px; padding: 24px 16px 20px; text-align: center;
    margin-bottom: 20px; position: relative; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 8px 32px rgba(26,95,180,0.3), inset 0 1px 0 rgba(255,255,255,0.08);
}
.logo-block::before {
    content: ''; position: absolute; top: -40%; left: -20%;
    width: 140%; height: 200%;
    background: radial-gradient(ellipse at 60% 30%, rgba(255,255,255,0.06) 0%, transparent 65%);
    pointer-events: none;
}
.logo-emoji { font-size: 2.8rem; display: block; margin-bottom: 8px;
              filter: drop-shadow(0 4px 12px rgba(59,130,246,0.6)); }
.logo-name {
    color: #fff !important; font-size: 1.7rem !important; font-weight: 900 !important;
    letter-spacing: -1px; display: block; margin-bottom: 3px;
}
.logo-tagline { color: rgba(255,255,255,0.6) !important; font-size: 0.72rem !important; display: block; }
.online-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.35);
    border-radius: 20px; padding: 4px 12px; margin-top: 12px;
    font-size: 0.68rem !important; color: #6ee7b7 !important; font-weight: 600;
}
.pulse { width: 6px; height: 6px; background: #10b981; border-radius: 50%;
         display: inline-block; animation: p 1.8s ease-in-out infinite; }
@keyframes p { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.35;transform:scale(1.5)} }

/* Section label */
.sec-lbl {
    font-size: 0.62rem !important; font-weight: 700 !important;
    letter-spacing: 1.4px !important; color: #334155 !important;
    text-transform: uppercase !important; display: block;
    margin: 16px 0 8px !important;
}

/* New Chat button */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: 0.87rem !important; padding: 11px 16px !important;
    width: 100% !important; letter-spacing: 0.2px !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.32) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(59,130,246,0.45) !important;
    filter: brightness(1.08) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* History items */
.hist-btn > button {
    background: #0c1526 !important;
    border: 1px solid #0f1e35 !important;
    border-radius: 10px !important;
    text-align: left !important;
    padding: 9px 12px !important;
    font-size: 0.78rem !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
.hist-btn > button:hover {
    border-color: #1d4ed8 !important;
    background: #0f1e35 !important;
    color: #e2e8f0 !important;
    transform: none !important;
    box-shadow: none !important;
}
.del-btn > button {
    background: transparent !important;
    border: 1px solid #1a2a45 !important;
    border-radius: 7px !important;
    color: #475569 !important;
    font-size: 0.75rem !important;
    padding: 5px 8px !important;
    box-shadow: none !important;
}
.del-btn > button:hover {
    background: rgba(239,68,68,0.15) !important;
    border-color: rgba(239,68,68,0.4) !important;
    color: #f87171 !important;
    transform: none !important;
}

/* Profile form */
.stTextInput > label, .stTextArea > label, .stSelectbox > label {
    font-size: 0.73rem !important; font-weight: 600 !important;
    color: #475569 !important; margin-bottom: 3px !important;
}
.stTextInput input, .stTextArea textarea {
    background: #0c1526 !important; border: 1.5px solid #0f1e35 !important;
    border-radius: 9px !important; color: #e2e8f0 !important; font-size: 0.85rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #334155 !important; }
.stSelectbox > div > div {
    background: #0c1526 !important; border: 1.5px solid #0f1e35 !important;
    border-radius: 9px !important; color: #e2e8f0 !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #0c1526 !important; border: 1px solid #0f1e35 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important; font-size: 0.82rem !important;
    color: #94a3b8 !important;
}
[data-testid="stExpander"] summary:hover { color: #e2e8f0 !important; }

/* Disclaimer */
.disc {
    background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px; padding: 10px 12px; font-size: 0.71rem !important;
    color: #d97706 !important; line-height: 1.6; margin-top: 8px;
}
.devfoot { text-align: center; padding: 12px 0 4px; font-size: 0.67rem !important; color: #1e3a5f !important; }
.devfoot .dn { color: #3b82f6 !important; font-weight: 700 !important; }

hr { border: none !important; border-top: 1px solid #0f1e35 !important; margin: 12px 0 !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .sec-lbl { color: #334155 !important; }
[data-testid="stSidebar"] .devfoot  { color: #1e3a5f !important; }
[data-testid="stSidebar"] .disc     { color: #d97706 !important; }

/* ══ MAIN CONTENT ══ */
.main-wrap { background: #060b14; min-height: 100vh; }

/* Top bar */
.topbar {
    background: linear-gradient(180deg, #080e1c 0%, #060b14 100%);
    border-bottom: 1px solid #0f1e35;
    padding: 16px 36px;
    display: flex; align-items: center; justify-content: space-between;
}
.topbar-title {
    font-size: 1.15rem; font-weight: 800; color: #e2e8f0;
    letter-spacing: -0.4px;
}
.topbar-sub { font-size: 0.74rem; color: #334155; margin-top: 2px; }
.topbar-badge {
    background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px; padding: 5px 14px; font-size: 0.72rem;
    color: #60a5fa; font-weight: 600;
}

/* KPI strip */
.kpi-strip {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 12px; padding: 18px 36px;
    border-bottom: 1px solid #0a1628;
}
.kpi {
    background: #080e1c; border: 1px solid #0f1e35;
    border-radius: 14px; padding: 14px 16px;
    display: flex; align-items: center; gap: 12px;
    transition: transform 0.15s, border-color 0.15s;
}
.kpi:hover { transform: translateY(-1px); border-color: #1d4ed8; }
.kpi-icon {
    width: 40px; height: 40px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; flex-shrink: 0;
}
.kpi-icon.blue   { background: rgba(59,130,246,0.15); }
.kpi-icon.purple { background: rgba(124,58,237,0.15); }
.kpi-icon.green  { background: rgba(16,185,129,0.15); }
.kpi-icon.amber  { background: rgba(245,158,11,0.15); }
.kpi-val { font-size: 0.92rem; font-weight: 800; color: #e2e8f0; }
.kpi-lbl { font-size: 0.62rem; color: #334155; text-transform: uppercase;
            letter-spacing: 0.6px; font-weight: 600; margin-top: 1px; }

/* Chat area */
.chat-area { padding: 24px 36px 0; }

/* Welcome */
.welcome {
    display: flex; flex-direction: column; align-items: center;
    padding: 56px 20px 32px; text-align: center;
}
.hero { font-size: 5rem; margin-bottom: 16px;
        filter: drop-shadow(0 0 40px rgba(59,130,246,0.45));
        animation: fl 3.5s ease-in-out infinite; display: block; }
@keyframes fl { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
.w-title {
    font-size: 2rem; font-weight: 900; color: #f1f5f9;
    letter-spacing: -1px; margin-bottom: 12px;
}
.w-title span { color: #3b82f6; }
.w-sub {
    color: #334155; font-size: 0.93rem; max-width: 500px;
    line-height: 1.85; margin-bottom: 36px;
}
.cards-grid {
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 12px; max-width: 640px; width: 100%;
}
.scard {
    background: #080e1c; border: 1px solid #0f1e35;
    border-radius: 14px; padding: 16px 14px; text-align: left;
    transition: all 0.18s; cursor: default;
}
.scard:hover {
    border-color: #1d4ed8;
    box-shadow: 0 4px 20px rgba(59,130,246,0.15);
    transform: translateY(-2px);
}
.scard .sc-icon { font-size: 1.4rem; margin-bottom: 8px; display: block; }
.scard .sc-text { font-size: 0.78rem; color: #64748b; line-height: 1.5; }

/* Messages */
.msg-row { display: flex; margin-bottom: 22px; gap: 14px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

.av {
    width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.av.bot { background: linear-gradient(135deg,#0a2342,#1d4ed8); border: 1px solid rgba(59,130,246,0.3); }
.av.usr { background: linear-gradient(135deg,#064e3b,#059669); border: 1px solid rgba(5,150,105,0.3); }

.bubble {
    max-width: 66%; padding: 15px 19px; border-radius: 18px;
    font-size: 0.9rem; line-height: 1.8;
}
.bubble.bot {
    background: #080e1c; border: 1px solid #0f1e35;
    border-top-left-radius: 4px; color: #cbd5e1;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.bubble.usr {
    background: linear-gradient(135deg,#1e3a8a,#1d4ed8);
    border-top-right-radius: 4px; color: #fff;
    box-shadow: 0 4px 20px rgba(29,78,216,0.35);
}
.bubble p  { margin: 0 0 8px; color: inherit !important; }
.bubble p:last-child { margin-bottom: 0; }
.bubble ul, .bubble ol { padding-left: 20px; margin: 8px 0; }
.bubble li { margin-bottom: 5px; color: inherit !important; }
.bubble strong { font-weight: 700; color: inherit !important; }
.bubble em     { font-style: italic; color: inherit !important; }
.btime { font-size: 0.64rem; opacity: 0.4; margin-top: 10px; letter-spacing: 0.3px; }

/* Input area */
.input-wrap {
    padding: 16px 36px 20px;
    background: linear-gradient(0deg, #060b14 0%, transparent 100%);
    position: sticky; bottom: 0;
}
[data-testid="stChatInput"] {
    background: #080e1c !important;
    border: 2px solid #0f1e35 !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #1d4ed8 !important;
    box-shadow: 0 0 0 4px rgba(29,78,216,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; color: #e2e8f0 !important;
    font-size: 0.95rem !important; font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #1e3a5f !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
    border-radius: 10px !important; box-shadow: 0 3px 12px rgba(29,78,216,0.4) !important;
}

/* Footer */
.footer {
    text-align: center; padding: 10px 0 16px;
    font-size: 0.68rem; color: #1e3a5f; margin-top: 4px;
}
.footer b { color: #3b82f6; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #0f1e35; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #1d4ed8; }

/* Alerts */
.stSuccess > div { border-radius: 10px !important; background: rgba(16,185,129,0.08) !important; }
.stError   > div { border-radius: 10px !important; background: rgba(239,68,68,0.08) !important; }
.stInfo    > div { border-radius: 10px !important; background: rgba(59,130,246,0.08) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-inner">', unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div class="logo-block">
        <span class="logo-emoji">🏥</span>
        <span class="logo-name">MedBotX</span>
        <span class="logo-tagline">Advanced AI Medical Assistant</span>
        <div class="online-pill">
            <span class="pulse"></span>&nbsp;AI Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New Chat
    if st.button("✨  Start New Chat"):
        start_new_chat()

    st.divider()

    # ── Chat History ──────────────────────────────────────────────────────────
    if st.session_state.chat_history:
        st.markdown('<span class="sec-lbl">Recent Conversations</span>', unsafe_allow_html=True)
        for i, sess in enumerate(st.session_state.chat_history):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown('<div class="hist-btn">', unsafe_allow_html=True)
                if st.button(f"💬  {sess['title']}", key=f"h{i}",
                             use_container_width=True,
                             help=f"{sess['count']} Q&A · {sess['ts']}"):
                    save_current_chat()
                    st.session_state.messages    = sess["messages"].copy()
                    st.session_state.oai_history = sess.get("oai", []).copy()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"d{i}"):
                    st.session_state.chat_history.pop(i)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

    # ── Health Profile ────────────────────────────────────────────────────────
    st.markdown('<span class="sec-lbl">🩺 My Health Profile</span>', unsafe_allow_html=True)

    p = st.session_state.health_profile
    summary = []
    if p.get("name"):       summary.append(p["name"])
    if p.get("age"):        summary.append(f"Age {p['age']}")
    if p.get("blood_type"): summary.append(f"Blood {p['blood_type']}")
    if summary:
        st.markdown(f'<p style="font-size:0.72rem;color:#334155;margin:0 0 8px;">{" · ".join(summary)}</p>',
                    unsafe_allow_html=True)

    with st.expander("✏️  Edit Profile", expanded=False):
        with st.form("prof", clear_on_submit=False):
            name  = st.text_input("Your Name",   value=p.get("name",""),  placeholder="e.g. Bhaskar")
            age   = st.text_input("Age",          value=p.get("age",""),   placeholder="e.g. 25")
            blood = st.selectbox("Blood Type",
                ["","A+","A-","B+","B-","AB+","AB-","O+","O-"],
                index=(["","A+","A-","B+","B-","AB+","AB-","O+","O-"].index(p.get("blood_type","")) 
                       if p.get("blood_type","") in ["","A+","A-","B+","B-","AB+","AB-","O+","O-"] else 0))
            allerg = st.text_area("Allergies", value=p.get("allergies",""),
                                  placeholder="e.g. Penicillin, Peanuts", height=55)
            conds  = st.text_area("Medical Conditions", value=p.get("conditions",""),
                                  placeholder="e.g. Diabetes Type 2", height=55)
            meds   = st.text_area("Medications", value=p.get("medications",""),
                                  placeholder="e.g. Metformin 500mg", height=55)
            notes  = st.text_area("Notes", value=p.get("notes",""),
                                  placeholder="Anything else...", height=46)
            if st.form_submit_button("💾  Save Profile"):
                st.session_state.health_profile = {
                    "name": name, "age": age, "blood_type": blood,
                    "allergies": allerg, "conditions": conds,
                    "medications": meds, "notes": notes,
                }
                st.success("✅ Profile saved! MedBotX now knows your health context.")

    st.divider()

    st.markdown("""
    <div class="disc">
        <strong>⚠️ Medical Disclaimer</strong><br>
        MedBotX provides general health information only.
        It is NOT a substitute for professional medical advice,
        diagnosis, or treatment. Always consult a qualified doctor.
    </div>
    <div class="devfoot">
        Developed by <span class="dn">Bhaskar Shivaji Kumbhar</span><br>
        <span style="opacity:0.4;font-size:0.62rem;">MedBotX v2.0 · 2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
msg_count = sum(1 for m in st.session_state.messages if m["role"] == "human")
profile_name = st.session_state.health_profile.get("name") or "User"

# Top bar
st.markdown(f"""
<div class="topbar">
    <div>
        <div class="topbar-title">🏥 MedBotX &nbsp;·&nbsp; AI Medical Assistant</div>
        <div class="topbar-sub">Ask anything about symptoms, medications, health conditions, or wellness</div>
    </div>
    <div class="topbar-badge">⚡ Powered by GPT-4o</div>
</div>
""", unsafe_allow_html=True)

# KPI strip
st.markdown(f"""
<div class="kpi-strip">
    <div class="kpi">
        <div class="kpi-icon blue">🧠</div>
        <div><div class="kpi-val">GPT-4o</div><div class="kpi-lbl">AI Model</div></div>
    </div>
    <div class="kpi">
        <div class="kpi-icon purple">💬</div>
        <div><div class="kpi-val">{msg_count}</div><div class="kpi-lbl">Questions Asked</div></div>
    </div>
    <div class="kpi">
        <div class="kpi-icon green">🩺</div>
        <div><div class="kpi-val">{"Set" if any(st.session_state.health_profile.values()) else "Not set"}</div><div class="kpi-lbl">Health Profile</div></div>
    </div>
    <div class="kpi">
        <div class="kpi-icon amber">🟢</div>
        <div><div class="kpi-val">Online</div><div class="kpi-lbl">Status</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_drug = st.tabs(["💬  Chat", "💊  Drug Interaction Checker"])

# ── TAB 1: Chat ────────────────────────────────────────────────────────────────
with tab_chat:
 st.markdown('<div class="chat-area">', unsafe_allow_html=True)

 if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
        <span class="hero">🩺</span>
        <div class="w-title">Hello, <span>{profile_name}</span> 👋</div>
        <p class="w-sub">
            I'm MedBotX — your personal AI medical information assistant.<br>
            Ask me anything about health, medications, symptoms, or wellness.<br>
            Your health profile is used to give personalised answers.
        </p>
        <div class="cards-grid">
            <div class="scard"><span class="sc-icon">🤒</span><div class="sc-text">Symptoms of Type 2 Diabetes?</div></div>
            <div class="scard"><span class="sc-icon">💊</span><div class="sc-text">Side effects of Ibuprofen?</div></div>
            <div class="scard"><span class="sc-icon">❤️</span><div class="sc-text">Lower blood pressure naturally?</div></div>
            <div class="scard"><span class="sc-icon">😴</span><div class="sc-text">Why do I feel tired all the time?</div></div>
            <div class="scard"><span class="sc-icon">🍎</span><div class="sc-text">Best diet for hypertension?</div></div>
            <div class="scard"><span class="sc-icon">🧬</span><div class="sc-text">What is cholesterol?</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 else:
    for msg in st.session_state.messages:
        role = msg["role"]
        html = md_to_html(msg["content"])
        ts   = msg.get("ts", "")
        if role == "ai":
            st.markdown(f"""
            <div class="msg-row">
                <div class="av bot">🤖</div>
                <div class="bubble bot">{html}<div class="btime">{ts}</div></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row user">
                <div class="av usr">👤</div>
                <div class="bubble usr">{html}<div class="btime">{ts}</div></div>
            </div>""", unsafe_allow_html=True)

 st.markdown('</div>', unsafe_allow_html=True)

 # ── Input ───────────────────────────────────────────────────────────────────
 st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
 user_input = st.chat_input("Ask your medical question…")
 st.markdown('</div>', unsafe_allow_html=True)

 if user_input and user_input.strip():
    q = user_input.strip()
    ts = datetime.now().strftime("%I:%M %p")

    st.session_state.messages.append({"role": "human", "content": q, "ts": ts})
    st.session_state.oai_history.append({"role": "user", "content": q})

    with st.spinner(""):
        answer = ask_openai(q)

    ai_ts = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "ai", "content": answer, "ts": ai_ts})
    st.session_state.oai_history.append({"role": "assistant", "content": answer})

    st.rerun()


# ── TAB 2: Drug Interaction Checker ───────────────────────────────────────────
SEV_COLOR = {"SAFE": "#22c55e", "MILD": "#facc15", "MODERATE": "#f97316", "SEVERE": "#ef4444"}
SEV_ICON  = {"SAFE": "✅", "MILD": "⚠️", "MODERATE": "🔶", "SEVERE": "🚨"}

with tab_drug:
    st.markdown("""
    <div style="margin-bottom:1rem;">
        <h2 style="color:#e2e8f0;margin:0;font-size:1.4rem;">💊 Drug Interaction Checker</h2>
        <p style="color:#94a3b8;margin:0.3rem 0 0;font-size:0.9rem;">
            Enter two or more medications to check for potential interactions.
            Powered by AI clinical pharmacology knowledge.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Drug input area
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        drug_input = st.text_input(
            "Enter drug names (comma-separated)",
            placeholder="e.g. Aspirin, Warfarin, Metformin",
            key="drug_input",
            label_visibility="collapsed",
        )
    with col_btn:
        check_clicked = st.button("🔍  Check", use_container_width=True, type="primary", key="drug_check_btn")

    # Quick examples
    st.markdown("""
    <p style="color:#64748b;font-size:0.78rem;margin:0.3rem 0 1rem;">
    Quick examples: &nbsp;
    <span style="color:#7dd3fc;">Aspirin + Warfarin</span> &nbsp;|&nbsp;
    <span style="color:#7dd3fc;">Ibuprofen + Prednisone</span> &nbsp;|&nbsp;
    <span style="color:#7dd3fc;">Metformin + Alcohol</span> &nbsp;|&nbsp;
    <span style="color:#7dd3fc;">Paracetamol + Codeine + Warfarin</span>
    </p>
    """, unsafe_allow_html=True)

    if check_clicked and drug_input.strip():
        raw_drugs = [d.strip() for d in drug_input.split(",") if d.strip()]

        if len(raw_drugs) < 2:
            st.warning("Please enter at least **2 drug names** separated by commas.")
        else:
            with st.spinner("Analysing drug interactions…"):
                result = check_drug_interactions(raw_drugs)

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                # Save to history
                st.session_state.drug_checks.insert(0, {
                    "drugs": raw_drugs,
                    "result": result,
                    "ts": datetime.now().strftime("%b %d, %I:%M %p"),
                })

                sev     = result.get("severity", "SAFE")
                sev_col = SEV_COLOR.get(sev, "#22c55e")
                sev_ico = SEV_ICON.get(sev, "✅")
                summary = result.get("summary", "")
                interactions = result.get("interactions", [])
                advice  = result.get("general_advice", "")
                see_doc = result.get("see_doctor", False)

                # Overall severity banner
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.04);border:1px solid {sev_col}44;
                            border-left:4px solid {sev_col};border-radius:10px;
                            padding:1rem 1.2rem;margin-bottom:1.2rem;">
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;">
                        <span style="font-size:1.5rem;">{sev_ico}</span>
                        <span style="font-size:1.1rem;font-weight:700;color:{sev_col};">
                            Overall Risk: {sev}
                        </span>
                    </div>
                    <p style="color:#cbd5e1;margin:0;font-size:0.95rem;">{summary}</p>
                </div>
                """, unsafe_allow_html=True)

                # Drugs analysed pills
                pills = "".join(
                    f'<span style="background:#1e40af22;border:1px solid #3b82f6;color:#93c5fd;'
                    f'padding:3px 12px;border-radius:20px;font-size:0.82rem;margin:2px;">{d}</span>'
                    for d in raw_drugs
                )
                st.markdown(f'<div style="margin-bottom:1rem;display:flex;flex-wrap:wrap;gap:4px;">{pills}</div>',
                            unsafe_allow_html=True)

                # Interaction cards
                if interactions:
                    st.markdown('<h4 style="color:#94a3b8;font-size:0.9rem;margin:0 0 0.6rem;">INTERACTIONS FOUND</h4>',
                                unsafe_allow_html=True)
                    for ix in interactions:
                        isev     = ix.get("severity", "MILD")
                        isev_col = SEV_COLOR.get(isev, "#facc15")
                        isev_ico = SEV_ICON.get(isev, "⚠️")
                        pair     = " + ".join(ix.get("drugs", []))
                        effect   = ix.get("effect", "")
                        mech     = ix.get("mechanism", "")
                        rec      = ix.get("recommendation", "")
                        st.markdown(f"""
                        <div style="background:#0f172a;border:1px solid {isev_col}55;border-radius:10px;
                                    padding:1rem 1.2rem;margin-bottom:0.8rem;">
                            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
                                <span style="font-size:1.2rem;">{isev_ico}</span>
                                <span style="font-weight:700;color:{isev_col};font-size:0.95rem;">{isev}</span>
                                <span style="color:#e2e8f0;font-weight:600;font-size:0.95rem;">— {pair}</span>
                            </div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">
                                <div>
                                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
                                                letter-spacing:0.05em;margin-bottom:2px;">What happens</div>
                                    <div style="color:#cbd5e1;font-size:0.88rem;">{effect}</div>
                                </div>
                                <div>
                                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
                                                letter-spacing:0.05em;margin-bottom:2px;">Why it occurs</div>
                                    <div style="color:#cbd5e1;font-size:0.88rem;">{mech}</div>
                                </div>
                            </div>
                            <div style="margin-top:0.6rem;background:rgba(255,255,255,0.04);
                                        border-radius:6px;padding:0.5rem 0.8rem;">
                                <span style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
                                            letter-spacing:0.05em;">Recommendation &nbsp;</span>
                                <span style="color:#e2e8f0;font-size:0.88rem;">{rec}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background:#052e16;border:1px solid #22c55e44;border-radius:10px;
                                padding:1rem 1.2rem;margin-bottom:1rem;">
                        <span style="font-size:1.2rem;">✅</span>
                        <span style="color:#4ade80;font-weight:600;margin-left:0.5rem;">
                            No significant interactions found between these medications.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                # General advice
                if advice:
                    st.markdown(f"""
                    <div style="background:rgba(99,102,241,0.08);border:1px solid #6366f133;
                                border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.8rem;">
                        <div style="color:#a5b4fc;font-size:0.75rem;text-transform:uppercase;
                                    letter-spacing:0.06em;margin-bottom:0.3rem;">General Advice</div>
                        <div style="color:#cbd5e1;font-size:0.9rem;">{advice}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # See doctor alert
                if see_doc:
                    st.markdown("""
                    <div style="background:#450a0a;border:1px solid #ef444455;border-radius:10px;
                                padding:0.9rem 1.1rem;margin-bottom:0.8rem;">
                        <span style="font-size:1.1rem;">🏥</span>
                        <span style="color:#fca5a5;font-weight:600;margin-left:0.5rem;">
                            Please consult your doctor or pharmacist before taking these medications together.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                # Disclaimer
                st.markdown("""
                <div style="background:rgba(255,255,255,0.02);border:1px solid #1e293b;
                            border-radius:8px;padding:0.7rem 1rem;margin-top:0.5rem;">
                    <span style="color:#475569;font-size:0.78rem;">
                        ⚠️ <strong style="color:#64748b;">Disclaimer:</strong>
                        This tool uses AI for informational purposes only. It is not a substitute
                        for professional medical or pharmaceutical advice. Always verify with a licensed
                        pharmacist or physician before changing your medication regimen.
                    </span>
                </div>
                """, unsafe_allow_html=True)

    elif check_clicked:
        st.info("Please enter at least two drug names to check interactions.")

    # ── Past Checks History ──────────────────────────────────────────────────
    if st.session_state.drug_checks:
        st.markdown("<hr style='border-color:#1e293b;margin:1.5rem 0 1rem;'>", unsafe_allow_html=True)
        st.markdown('<p style="color:#475569;font-size:0.8rem;text-transform:uppercase;'
                    'letter-spacing:0.08em;margin-bottom:0.6rem;">Recent Checks</p>',
                    unsafe_allow_html=True)
        for i, chk in enumerate(st.session_state.drug_checks[:5]):
            chk_sev   = chk["result"].get("severity", "SAFE")
            chk_col   = SEV_COLOR.get(chk_sev, "#22c55e")
            chk_ico   = SEV_ICON.get(chk_sev, "✅")
            chk_drugs = " + ".join(chk["drugs"])
            chk_ts    = chk["ts"]
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        background:rgba(255,255,255,0.02);border:1px solid #1e293b;
                        border-radius:8px;padding:0.5rem 0.9rem;margin-bottom:0.4rem;">
                <div>
                    <span style="font-size:1rem;margin-right:0.4rem;">{chk_ico}</span>
                    <span style="color:#e2e8f0;font-size:0.88rem;font-weight:500;">{chk_drugs}</span>
                </div>
                <div style="display:flex;align-items:center;gap:0.8rem;">
                    <span style="color:{chk_col};font-size:0.78rem;font-weight:600;">{chk_sev}</span>
                    <span style="color:#475569;font-size:0.75rem;">{chk_ts}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    MedBotX &nbsp;·&nbsp; Developed by <b>Bhaskar Shivaji Kumbhar</b>
    &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp;
    Always consult a qualified healthcare professional
</div>
""", unsafe_allow_html=True)
