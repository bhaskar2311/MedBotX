"""
MedBotX — Advanced AI Medical Assistant
Developed by Bhaskar Shivaji Kumbhar
Direct OpenAI integration — no backend required
"""
import os, re, json, base64, io
from datetime import datetime
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

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

# ── Symptom Checker ───────────────────────────────────────────────────────────
def check_symptoms(symptoms: str, age: str, gender: str) -> dict:
    if not API_KEY:
        return {"error": "No API key configured."}
    client = OpenAI(api_key=API_KEY)
    prompt = f"""You are a clinical triage AI. A patient reports these symptoms: {symptoms}
Patient info — Age: {age or 'unknown'}, Gender: {gender or 'unknown'}.

Respond ONLY with valid JSON in this exact format:
{{
  "urgency": "EMERGENCY" | "URGENT" | "MODERATE" | "LOW",
  "urgency_reason": "One sentence on why this urgency level",
  "possible_conditions": [
    {{"name": "Condition name", "likelihood": "High/Medium/Low", "description": "Brief description"}}
  ],
  "red_flags": ["List any alarming symptoms that need immediate attention"],
  "recommended_actions": ["Action 1", "Action 2"],
  "home_care": ["Home care tip 1", "Home care tip 2"],
  "see_doctor_within": "Immediately / 24 hours / 2-3 days / When convenient"
}}
Provide 2-4 possible conditions. No markdown, just JSON."""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1200,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


# ── Medical Report Summarizer ──────────────────────────────────────────────────
def summarize_report(report_text: str) -> dict:
    if not API_KEY:
        return {"error": "No API key configured."}
    client = OpenAI(api_key=API_KEY)
    prompt = f"""You are a medical report interpreter helping a patient understand their report.
Report text:
\"\"\"
{report_text[:4000]}
\"\"\"

Respond ONLY with valid JSON:
{{
  "title": "Type of report (e.g. Blood Test, MRI, X-Ray)",
  "summary": "Plain English 2-3 sentence summary",
  "key_findings": [
    {{"parameter": "Test name", "value": "Result", "normal_range": "Normal range", "status": "Normal/High/Low/Abnormal", "meaning": "What this means"}}
  ],
  "abnormal_count": 0,
  "overall_impression": "Overall health impression in plain language",
  "follow_up": ["Suggested follow-up action 1", "action 2"],
  "consult_specialist": true | false,
  "specialist_type": "e.g. Cardiologist, Endocrinologist, or null"
}}
No markdown, just JSON."""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1800,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
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
tab_chat, tab_drug, tab_sym, tab_bmi, tab_rep = st.tabs([
    "💬  Chat",
    "💊  Drug Checker",
    "🩺  Symptom Checker",
    "⚖️  BMI & Health",
    "📋  Report Analyser",
])

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

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — SYMPTOM CHECKER
# ══════════════════════════════════════════════════════════════════════════════
URG_COLOR = {"EMERGENCY": "#ef4444", "URGENT": "#f97316", "MODERATE": "#facc15", "LOW": "#22c55e"}
URG_ICON  = {"EMERGENCY": "🚨", "URGENT": "🔶", "MODERATE": "⚠️", "LOW": "✅"}

with tab_sym:
    st.markdown("""
    <div style="margin-bottom:1rem;">
        <h2 style="color:#e2e8f0;margin:0;font-size:1.4rem;">🩺 Symptom Checker</h2>
        <p style="color:#94a3b8;margin:0.3rem 0 0;font-size:0.9rem;">
            Describe your symptoms and get an AI-powered triage assessment with possible conditions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([3, 1, 1])
    with sc1:
        sym_input = st.text_area(
            "Describe your symptoms",
            placeholder="e.g. I have had a headache for 2 days, fever 38.5°C, stiff neck and sensitivity to light...",
            height=100, key="sym_input", label_visibility="collapsed",
        )
    with sc2:
        sym_age = st.text_input("Age", placeholder="e.g. 35",
                                value=st.session_state.health_profile.get("age", ""),
                                key="sym_age", label_visibility="collapsed")
    with sc3:
        sym_gender = st.selectbox("Gender", ["", "Male", "Female", "Other"],
                                  key="sym_gender", label_visibility="collapsed")

    sym_btn = st.button("🔍  Analyse Symptoms", type="primary", key="sym_btn")

    if sym_btn and sym_input.strip():
        with st.spinner("Analysing your symptoms…"):
            sym_result = check_symptoms(sym_input.strip(), sym_age, sym_gender)

        if "error" in sym_result:
            st.error(sym_result["error"])
        else:
            urg      = sym_result.get("urgency", "LOW")
            urg_col  = URG_COLOR.get(urg, "#22c55e")
            urg_ico  = URG_ICON.get(urg, "✅")
            urg_why  = sym_result.get("urgency_reason", "")
            see_when = sym_result.get("see_doctor_within", "")
            conditions = sym_result.get("possible_conditions", [])
            red_flags  = sym_result.get("red_flags", [])
            actions    = sym_result.get("recommended_actions", [])
            home_care  = sym_result.get("home_care", [])

            if urg == "EMERGENCY":
                st.markdown("""
                <div style="background:#450a0a;border:2px solid #ef4444;border-radius:10px;
                            padding:1rem 1.2rem;margin-bottom:1rem;text-align:center;">
                    <span style="font-size:2rem;">🚨</span>
                    <div style="color:#ef4444;font-size:1.2rem;font-weight:700;margin:0.3rem 0;">
                        EMERGENCY — Call 112 / 911 Immediately
                    </div>
                    <div style="color:#fca5a5;font-size:0.9rem;">These symptoms may indicate a life-threatening condition.</div>
                </div>
                """, unsafe_allow_html=True)

            # Urgency banner
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid {urg_col}44;
                        border-left:4px solid {urg_col};border-radius:10px;
                        padding:0.9rem 1.2rem;margin-bottom:1.2rem;
                        display:flex;align-items:center;gap:1rem;">
                <span style="font-size:1.8rem;">{urg_ico}</span>
                <div>
                    <div style="color:{urg_col};font-weight:700;font-size:1rem;">Urgency: {urg}</div>
                    <div style="color:#94a3b8;font-size:0.88rem;">{urg_why}</div>
                    <div style="color:#64748b;font-size:0.8rem;margin-top:0.2rem;">
                        See a doctor: <strong style="color:{urg_col};">{see_when}</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Red flags
            if red_flags:
                flags_html = "".join(f'<li style="color:#fca5a5;font-size:0.88rem;">{f}</li>' for f in red_flags)
                st.markdown(f"""
                <div style="background:#1c0a0a;border:1px solid #ef444433;border-radius:10px;
                            padding:0.8rem 1rem;margin-bottom:1rem;">
                    <div style="color:#ef4444;font-size:0.75rem;text-transform:uppercase;
                                letter-spacing:0.06em;margin-bottom:0.4rem;">⚠ Red Flag Symptoms</div>
                    <ul style="margin:0;padding-left:1.2rem;">{flags_html}</ul>
                </div>
                """, unsafe_allow_html=True)

            # Possible conditions
            if conditions:
                st.markdown('<h4 style="color:#94a3b8;font-size:0.85rem;text-transform:uppercase;'
                            'letter-spacing:0.06em;margin:0 0 0.6rem;">Possible Conditions</h4>',
                            unsafe_allow_html=True)
                LIKE_COLOR = {"High": "#ef4444", "Medium": "#f97316", "Low": "#22c55e"}
                for cond in conditions:
                    lk    = cond.get("likelihood", "Low")
                    lk_c  = LIKE_COLOR.get(lk, "#94a3b8")
                    st.markdown(f"""
                    <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                                padding:0.8rem 1rem;margin-bottom:0.6rem;
                                display:flex;justify-content:space-between;align-items:flex-start;">
                        <div style="flex:1;">
                            <div style="color:#e2e8f0;font-weight:600;font-size:0.95rem;
                                        margin-bottom:0.3rem;">{cond.get('name','')}</div>
                            <div style="color:#94a3b8;font-size:0.85rem;">{cond.get('description','')}</div>
                        </div>
                        <span style="background:{lk_c}22;border:1px solid {lk_c}55;color:{lk_c};
                                    padding:2px 10px;border-radius:20px;font-size:0.75rem;
                                    font-weight:600;white-space:nowrap;margin-left:1rem;">{lk}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Recommended actions + home care side by side
            col_a, col_b = st.columns(2)
            with col_a:
                if actions:
                    acts_html = "".join(f'<li style="color:#cbd5e1;font-size:0.88rem;margin-bottom:4px;">{a}</li>' for a in actions)
                    st.markdown(f"""
                    <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                                padding:0.8rem 1rem;margin-top:0.6rem;">
                        <div style="color:#7dd3fc;font-size:0.75rem;text-transform:uppercase;
                                    letter-spacing:0.06em;margin-bottom:0.5rem;">Recommended Actions</div>
                        <ul style="margin:0;padding-left:1.2rem;">{acts_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)
            with col_b:
                if home_care:
                    hc_html = "".join(f'<li style="color:#cbd5e1;font-size:0.88rem;margin-bottom:4px;">{h}</li>' for h in home_care)
                    st.markdown(f"""
                    <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                                padding:0.8rem 1rem;margin-top:0.6rem;">
                        <div style="color:#86efac;font-size:0.75rem;text-transform:uppercase;
                                    letter-spacing:0.06em;margin-bottom:0.5rem;">Home Care Tips</div>
                        <ul style="margin:0;padding-left:1.2rem;">{hc_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px solid #1e293b;
                        border-radius:8px;padding:0.7rem 1rem;margin-top:1rem;">
                <span style="color:#475569;font-size:0.78rem;">
                    ⚠️ <strong style="color:#64748b;">Disclaimer:</strong>
                    This is an AI triage aid, not a medical diagnosis. Always consult a qualified
                    healthcare professional for proper evaluation.
                </span>
            </div>
            """, unsafe_allow_html=True)

    elif sym_btn:
        st.info("Please describe your symptoms to get an assessment.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — BMI & HEALTH CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_bmi:
    st.markdown("""
    <div style="margin-bottom:1rem;">
        <h2 style="color:#e2e8f0;margin:0;font-size:1.4rem;">⚖️ BMI & Health Calculator</h2>
        <p style="color:#94a3b8;margin:0.3rem 0 0;font-size:0.9rem;">
            Calculate your BMI, ideal weight, calorie needs, and get personalised health insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)
    with bc1:
        b_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0,
                                   value=70.0, step=0.5, key="b_weight")
        b_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0,
                                   value=170.0, step=0.5, key="b_height")
    with bc2:
        b_age    = st.number_input("Age (years)", min_value=1, max_value=120,
                                   value=int(st.session_state.health_profile.get("age") or 30),
                                   key="b_age")
        b_gender = st.selectbox("Gender", ["Male", "Female"], key="b_gender")
        b_act    = st.selectbox("Activity Level", [
            "Sedentary (office job, little exercise)",
            "Lightly active (light exercise 1-3 days/week)",
            "Moderately active (moderate exercise 3-5 days/week)",
            "Very active (hard exercise 6-7 days/week)",
            "Extremely active (athlete, physical job)",
        ], key="b_act")

    calc_btn = st.button("📊  Calculate", type="primary", key="bmi_btn")

    if calc_btn:
        h_m  = b_height / 100
        bmi  = round(b_weight / (h_m ** 2), 1)
        if bmi < 18.5:   bmi_cat, bmi_col = "Underweight", "#facc15"
        elif bmi < 25.0: bmi_cat, bmi_col = "Normal weight", "#22c55e"
        elif bmi < 30.0: bmi_cat, bmi_col = "Overweight", "#f97316"
        else:            bmi_cat, bmi_col = "Obese", "#ef4444"

        # Ideal weight (Devine formula)
        if b_gender == "Male":
            ideal_low  = round(50 + 2.3 * ((b_height - 152.4) / 2.54), 1)
        else:
            ideal_low  = round(45.5 + 2.3 * ((b_height - 152.4) / 2.54), 1)
        ideal_high = round(ideal_low + 8, 1)

        # BMR (Mifflin-St Jeor)
        if b_gender == "Male":
            bmr = round(10 * b_weight + 6.25 * b_height - 5 * b_age + 5)
        else:
            bmr = round(10 * b_weight + 6.25 * b_height - 5 * b_age - 161)

        act_mult = [1.2, 1.375, 1.55, 1.725, 1.9][["Sedentary", "Lightly", "Moderately", "Very", "Extremely"]
                    .index(next(a for a in ["Sedentary","Lightly","Moderately","Very","Extremely"] if a in b_act))]
        tdee     = round(bmr * act_mult)
        lose_cal = tdee - 500
        gain_cal = tdee + 300

        # BMI meter visual
        bmi_pct = min(max((bmi - 10) / (45 - 10) * 100, 0), 100)
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;
                    padding:1.2rem 1.5rem;margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.8rem;">
                <span style="color:#94a3b8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;">Your BMI</span>
                <span style="color:{bmi_col};font-size:2.2rem;font-weight:800;">{bmi}</span>
            </div>
            <div style="background:#1e293b;border-radius:20px;height:12px;margin-bottom:0.5rem;position:relative;">
                <div style="position:absolute;left:0;top:0;height:100%;border-radius:20px;
                            width:{bmi_pct}%;background:linear-gradient(90deg,#22c55e,#facc15,#f97316,#ef4444);"></div>
                <div style="position:absolute;left:{bmi_pct}%;top:-4px;transform:translateX(-50%);
                            width:20px;height:20px;background:{bmi_col};border-radius:50%;
                            border:3px solid #0f172a;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#475569;">
                <span>Underweight &lt;18.5</span><span>Normal 18.5–24.9</span>
                <span>Overweight 25–29.9</span><span>Obese ≥30</span>
            </div>
            <div style="text-align:center;margin-top:0.8rem;">
                <span style="background:{bmi_col}22;border:1px solid {bmi_col}55;color:{bmi_col};
                            padding:4px 16px;border-radius:20px;font-weight:700;font-size:0.95rem;">{bmi_cat}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Stats grid
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;margin-bottom:1rem;">
            <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;">Ideal Weight</div>
                <div style="color:#7dd3fc;font-size:1.3rem;font-weight:700;">{ideal_low}–{ideal_high} kg</div>
            </div>
            <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;">Basal Metabolic Rate</div>
                <div style="color:#a5b4fc;font-size:1.3rem;font-weight:700;">{bmr} kcal/day</div>
            </div>
            <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;">Daily Calorie Need</div>
                <div style="color:#86efac;font-size:1.3rem;font-weight:700;">{tdee} kcal/day</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-bottom:1rem;">
            <div style="background:#0f172a;border:1px solid #22c55e33;border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;">To Lose Weight (−0.5 kg/wk)</div>
                <div style="color:#4ade80;font-size:1.2rem;font-weight:700;">{lose_cal} kcal/day</div>
            </div>
            <div style="background:#0f172a;border:1px solid #6366f133;border-radius:10px;padding:0.9rem;text-align:center;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;">To Gain Weight (+0.3 kg/wk)</div>
                <div style="color:#a5b4fc;font-size:1.2rem;font-weight:700;">{gain_cal} kcal/day</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Health tips based on BMI
        tips = {
            "Underweight": ["Increase calorie intake with nutrient-dense foods",
                            "Include protein-rich foods: eggs, legumes, lean meat",
                            "Consult a dietitian for a personalised meal plan",
                            "Rule out underlying causes (thyroid, digestion issues)"],
            "Normal weight": ["Maintain current habits — you're in a healthy range!",
                              "Focus on balanced nutrition and regular exercise",
                              "Aim for 150 min of moderate activity per week",
                              "Annual health check-ups are recommended"],
            "Overweight": ["Reduce refined carbohydrates and added sugars",
                           "Aim for a 300–500 kcal daily deficit",
                           "Include 30 min of brisk walking daily",
                           "Stay well hydrated — drink 8 glasses of water"],
            "Obese": ["Consult your doctor before starting any diet programme",
                      "Small sustainable changes are more effective long-term",
                      "Consider referral to a dietitian or weight-loss programme",
                      "Monitor blood pressure, blood sugar, and cholesterol regularly"],
        }
        tips_html = "".join(f'<li style="color:#cbd5e1;font-size:0.88rem;margin-bottom:4px;">{t}</li>'
                            for t in tips.get(bmi_cat, []))
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:0.9rem 1rem;">
            <div style="color:#fbbf24;font-size:0.75rem;text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:0.5rem;">💡 Personalised Tips</div>
            <ul style="margin:0;padding-left:1.2rem;">{tips_html}</ul>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — MEDICAL REPORT ANALYSER  (Text · PDF · Image)
# ══════════════════════════════════════════════════════════════════════════════
STATUS_COL = {"Normal": "#22c55e", "High": "#ef4444", "Low": "#facc15",
              "Abnormal": "#f97316", "Critical": "#dc2626"}

def render_report_results(rep_result: dict):
    """Render the structured report analysis — shared by all input modes."""
    title    = rep_result.get("title", "Medical Report")
    summary  = rep_result.get("summary", "")
    findings = rep_result.get("key_findings", [])
    abn_cnt  = rep_result.get("abnormal_count", 0)
    overall  = rep_result.get("overall_impression", "")
    followup = rep_result.get("follow_up", [])
    consult  = rep_result.get("consult_specialist", False)
    spec     = rep_result.get("specialist_type", "")

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.04);border:1px solid #334155;
                border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;">
        <div style="color:#7dd3fc;font-size:0.75rem;text-transform:uppercase;
                    letter-spacing:0.06em;margin-bottom:0.3rem;">{title}</div>
        <p style="color:#e2e8f0;font-size:0.95rem;margin:0;">{summary}</p>
        <div style="margin-top:0.6rem;display:flex;gap:1rem;flex-wrap:wrap;">
            <span style="color:#94a3b8;font-size:0.82rem;">
                🔍 <strong style="color:#e2e8f0;">{len(findings)}</strong> parameters checked
            </span>
            <span style="color:#94a3b8;font-size:0.82rem;">
                ⚠️ <strong style="color:{'#ef4444' if abn_cnt > 0 else '#22c55e'};">{abn_cnt}</strong> abnormal
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if findings:
        st.markdown('<h4 style="color:#94a3b8;font-size:0.82rem;text-transform:uppercase;'
                    'letter-spacing:0.06em;margin:0 0 0.6rem;">Key Findings</h4>',
                    unsafe_allow_html=True)
        rows = ""
        for f in findings:
            sc = STATUS_COL.get(f.get("status", "Normal"), "#22c55e")
            rows += f"""
            <tr>
                <td style="padding:8px 10px;color:#e2e8f0;font-weight:500;">{f.get('parameter','')}</td>
                <td style="padding:8px 10px;color:#cbd5e1;">{f.get('value','')}</td>
                <td style="padding:8px 10px;color:#64748b;font-size:0.82rem;">{f.get('normal_range','')}</td>
                <td style="padding:8px 10px;text-align:center;">
                    <span style="background:{sc}22;border:1px solid {sc}55;color:{sc};
                                padding:2px 8px;border-radius:12px;font-size:0.75rem;font-weight:600;">
                        {f.get('status','')}
                    </span>
                </td>
                <td style="padding:8px 10px;color:#94a3b8;font-size:0.82rem;">{f.get('meaning','')}</td>
            </tr>"""
        st.markdown(f"""
        <div style="overflow-x:auto;margin-bottom:1rem;">
            <table style="width:100%;border-collapse:collapse;background:#0f172a;
                          border-radius:10px;overflow:hidden;">
                <thead><tr style="background:#1e293b;">
                    <th style="padding:8px 10px;text-align:left;color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">Parameter</th>
                    <th style="padding:8px 10px;text-align:left;color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">Value</th>
                    <th style="padding:8px 10px;text-align:left;color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">Normal Range</th>
                    <th style="padding:8px 10px;text-align:center;color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">Status</th>
                    <th style="padding:8px 10px;text-align:left;color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;">Meaning</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    if overall:
        st.markdown(f"""
        <div style="background:rgba(99,102,241,0.08);border:1px solid #6366f133;
                    border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.8rem;">
            <div style="color:#a5b4fc;font-size:0.75rem;text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:0.3rem;">Overall Impression</div>
            <div style="color:#e2e8f0;font-size:0.92rem;">{overall}</div>
        </div>
        """, unsafe_allow_html=True)

    if followup:
        fu_html = "".join(f'<li style="color:#cbd5e1;font-size:0.88rem;margin-bottom:4px;">{fu}</li>' for fu in followup)
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                    padding:0.8rem 1rem;margin-bottom:0.8rem;">
            <div style="color:#fbbf24;font-size:0.75rem;text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:0.5rem;">Follow-up Actions</div>
            <ul style="margin:0;padding-left:1.2rem;">{fu_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    if consult and spec:
        st.markdown(f"""
        <div style="background:#1c1207;border:1px solid #f9731655;border-radius:10px;
                    padding:0.8rem 1rem;margin-bottom:0.8rem;">
            <span style="font-size:1rem;">🏥</span>
            <span style="color:#fdba74;font-weight:600;margin-left:0.5rem;">
                Consider consulting a <strong>{spec}</strong> based on these results.
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid #1e293b;
                border-radius:8px;padding:0.7rem 1rem;margin-top:0.5rem;">
        <span style="color:#475569;font-size:0.78rem;">
            ⚠️ <strong style="color:#64748b;">Disclaimer:</strong>
            AI interpretation is for educational purposes only. Always have your reports
            reviewed by a qualified healthcare professional.
        </span>
    </div>
    """, unsafe_allow_html=True)


with tab_rep:
    st.markdown("""
    <div style="margin-bottom:1rem;">
        <h2 style="color:#e2e8f0;margin:0;font-size:1.4rem;">📋 Medical Report Analyser</h2>
        <p style="color:#94a3b8;margin:0.3rem 0 0;font-size:0.9rem;">
            Upload or paste your medical report — blood test, MRI findings, X-ray, pathology etc.
            Get a plain-English explanation with status indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Input mode selector ───────────────────────────────────────────────────
    input_mode = st.radio(
        "Choose input method",
        ["📝  Paste Text", "📄  Upload PDF", "🖼️  Upload Image"],
        horizontal=True, key="rep_mode", label_visibility="collapsed",
    )
    st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)

    rep_content_ready = False
    rep_text_final    = ""
    rep_image_b64     = None
    rep_image_mime    = None

    # ── TEXT mode ─────────────────────────────────────────────────────────────
    if input_mode == "📝  Paste Text":
        rep_text_in = st.text_area(
            "Paste your report here",
            placeholder="""Example — CBC Report:
Haemoglobin: 10.2 g/dL  (Normal: 13.5–17.5)
WBC: 11,500 /μL          (Normal: 4,500–11,000)
Platelets: 420,000 /μL   (Normal: 150,000–400,000)
Glucose (Fasting): 126 mg/dL  (Normal: 70–100)""",
            height=220, key="rep_text_in",
        )
        if rep_text_in.strip():
            rep_text_final    = rep_text_in.strip()
            rep_content_ready = True

    # ── PDF mode ──────────────────────────────────────────────────────────────
    elif input_mode == "📄  Upload PDF":
        if not HAS_PYMUPDF:
            st.warning("PyMuPDF is not installed. Run `pip install pymupdf` and restart the app.")
        else:
            pdf_file = st.file_uploader(
                "Upload your PDF report", type=["pdf"], key="rep_pdf",
                help="Max ~20 MB. Text will be extracted automatically.",
            )
            if pdf_file:
                with st.spinner("Extracting text from PDF…"):
                    try:
                        pdf_bytes = pdf_file.read()
                        doc       = fitz.open(stream=pdf_bytes, filetype="pdf")
                        pages_txt = []
                        for page in doc:
                            pages_txt.append(page.get_text())
                        doc.close()
                        rep_text_final = "\n".join(pages_txt).strip()
                        if rep_text_final:
                            rep_content_ready = True
                            st.success(f"Extracted {len(rep_text_final):,} characters from {len(pages_txt)} page(s).")
                            with st.expander("Preview extracted text"):
                                st.text(rep_text_final[:2000] + ("…" if len(rep_text_final) > 2000 else ""))
                        else:
                            st.warning("No text found in this PDF. It may be a scanned image — try the Image upload instead.")
                    except Exception as e:
                        st.error(f"Could not read PDF: {e}")

    # ── IMAGE mode ────────────────────────────────────────────────────────────
    elif input_mode == "🖼️  Upload Image":
        img_file = st.file_uploader(
            "Upload your report image",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            key="rep_img",
            help="Scanned reports, lab printouts, X-ray screenshots etc.",
        )
        if img_file:
            rep_image_mime = img_file.type or "image/jpeg"
            img_bytes      = img_file.read()
            rep_image_b64  = base64.b64encode(img_bytes).decode("utf-8")
            rep_content_ready = True
            st.image(img_bytes, caption="Uploaded report", use_container_width=False, width=480)

    # ── Analyse button ────────────────────────────────────────────────────────
    rep_btn = st.button("🔬  Analyse Report", type="primary", key="rep_btn",
                        disabled=not rep_content_ready)

    if rep_btn and rep_content_ready:
        if rep_image_b64:
            # Vision path — send image directly to GPT-4o
            with st.spinner("Reading and analysing report image…"):
                if not API_KEY:
                    st.error("No API key configured.")
                else:
                    try:
                        client = OpenAI(api_key=API_KEY)
                        vision_prompt = """You are a clinical expert. Analyse this medical report image.
Respond ONLY with valid JSON (no markdown):
{
  "title": "Report type",
  "summary": "2-3 sentence plain-English summary",
  "key_findings": [
    {"parameter": "...", "value": "...", "normal_range": "...", "status": "Normal|High|Low|Abnormal|Critical", "meaning": "..."}
  ],
  "abnormal_count": 0,
  "overall_impression": "Overall health interpretation",
  "follow_up": ["action 1", "action 2"],
  "consult_specialist": true,
  "specialist_type": "e.g. Haematologist or null"
}"""
                        resp = client.chat.completions.create(
                            model=MODEL,
                            messages=[{"role": "user", "content": [
                                {"type": "text",       "text": vision_prompt},
                                {"type": "image_url",  "image_url": {
                                    "url": f"data:{rep_image_mime};base64,{rep_image_b64}",
                                    "detail": "high",
                                }},
                            ]}],
                            temperature=0.1,
                            max_tokens=1800,
                        )
                        raw = resp.choices[0].message.content.strip()
                        raw = re.sub(r'^```json\s*', '', raw)
                        raw = re.sub(r'\s*```$', '', raw)
                        rep_result = json.loads(raw)
                        render_report_results(rep_result)
                    except json.JSONDecodeError:
                        st.error("Could not parse AI response. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            # Text / PDF path
            with st.spinner("Analysing your medical report…"):
                rep_result = summarize_report(rep_text_final)
            if "error" in rep_result:
                st.error(rep_result["error"])
            else:
                render_report_results(rep_result)

    elif rep_btn:
        st.info("Please provide a report to analyse.")


# Footer
st.markdown("""
<div class="footer">
    MedBotX &nbsp;·&nbsp; Developed by <b>Bhaskar Shivaji Kumbhar</b>
    &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp;
    Always consult a qualified healthcare professional
</div>
""", unsafe_allow_html=True)
