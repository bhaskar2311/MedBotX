# 🏥 MedBotX — Advanced AI Medical Assistant

> **Developed by Bhaskar Shivaji Kumbhar**

An AI-powered medical assistant built with **Streamlit** and **OpenAI GPT-4o** that provides accurate, personalised health information. No backend required — everything runs directly in the browser via the Streamlit frontend.

🔗 **Live App:** [Deployed on Streamlit Community Cloud]([https://share.streamlit.io](https://medbotx.streamlit.app/))

---

## ✨ Features

| Tab | Feature | Description |
|---|---|---|
| 💬 | **AI Medical Chat** | GPT-4o powered chatbot with full conversation memory and health profile context |
| 💊 | **Drug Interaction Checker** | Check interactions between 2+ medications — SAFE / MILD / MODERATE / SEVERE severity |
| 🩺 | **Symptom Checker** | Describe symptoms → urgency triage, possible conditions, red flags, home care tips |
| ⚖️ | **BMI & Health Calculator** | BMI meter, ideal weight, BMR, daily calorie needs, weight goals, personalised tips |
| 📋 | **Medical Report Analyser** | Upload PDF, image, or paste text — get a plain-English findings table with status indicators |

### Additional Highlights
- 🧠 **Persistent Chat Memory** — context maintained across the full conversation
- 🩺 **Health Profile** — store name, age, blood type, allergies, conditions, medications for personalised answers
- 💾 **Chat Session History** — save and revisit past conversations within the session
- 🌙 **Dark UI** — professional medical-grade dark theme throughout
- ⚡ **New Chat** button to start fresh while keeping session history
- 🛡️ **Safety Rules** — emergency detection, never diagnoses, always recommends a doctor

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│             Streamlit Frontend (app.py)           │
│                                                  │
│  💬 Chat  💊 Drug  🩺 Symptom  ⚖️ BMI  📋 Report  │
└──────────────────────┬───────────────────────────┘
                       │ Direct API calls
              ┌────────▼────────┐
              │  OpenAI GPT-4o  │
              │  (Chat + Vision)│
              └─────────────────┘
```

No database. No backend server. All state is held in Streamlit session state.

---

## 📁 Project Structure

```
MedBotX/
├── frontend/
│   └── app.py                 # All UI + AI logic (single file)
├── .streamlit/
│   └── config.toml            # Dark theme + toolbar config
├── Project Documents/         # HLD, LLD, Requirements PDFs
├── .env                       # Your API key (never committed)
├── .env.example               # Template for environment variables
├── requirements.txt           # Minimal dependencies
├── START_FRONTEND.bat         # Double-click to run on Windows
├── Dockerfile.frontend        # Docker support
└── README.md
```

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup

```bash
git clone https://github.com/bhaskar2311/MedBotX.git
cd MedBotX

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o
```

> ⚠️ Never commit your `.env` file — it is already in `.gitignore`.

### 3. Run the App

```bash
streamlit run frontend/app.py
```

Or on Windows, simply double-click **`START_FRONTEND.bat`**.

Open: [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deploy on Streamlit Community Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"** and set:
   - **Repository:** `bhaskar2311/MedBotX`
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`
4. Click **"Advanced settings" → Secrets** and add:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   OPENAI_MODEL = "gpt-4o"
   ```
5. Click **Deploy** — you'll get a public URL instantly.

---

## 📋 Report Analyser — Input Modes

The Medical Report Analyser supports three ways to submit a report:

| Mode | How it works |
|---|---|
| 📝 **Paste Text** | Copy-paste your lab report text directly |
| 📄 **Upload PDF** | PyMuPDF extracts text from the PDF automatically |
| 🖼️ **Upload Image** | JPG/PNG scan sent to GPT-4o Vision — no OCR library needed |

All three modes produce the same structured output:
- Parameter table with Normal / High / Low / Abnormal status
- Overall impression in plain English
- Follow-up action recommendations
- Specialist referral suggestion if needed

---

## 💊 Drug Interaction Checker

Enter 2 or more drug names (comma-separated) to get:

- **Overall severity** — SAFE / MILD / MODERATE / SEVERE
- **Per-pair interaction cards** — what happens, why it occurs, what to do
- **General advice** and doctor consultation alert
- **Recent checks history** panel

---

## 🛡️ Safety & Disclaimer

- MedBotX provides **general health information only** — it is **not** a medical diagnosis tool
- Emergency symptom detection always advises calling **112 / 911**
- The app never recommends stopping prescribed medications
- All AI outputs include a disclaimer to consult a qualified healthcare professional

---

## 🔮 Roadmap

- [ ] Voice input (Whisper API)
- [ ] Multilingual support
- [ ] EHR/EMR integration (HL7 FHIR)
- [ ] Export chat / report as PDF
- [ ] Health News Feed (live medical news)

---

## 📦 Dependencies

```
openai>=1.30.0       # GPT-4o API + Vision
streamlit>=1.34.0    # Web UI framework
pymupdf>=1.24.0      # PDF text extraction
python-dotenv>=1.0.0 # Environment variable loading
```

---

## 🔗 Git Workflow

```bash
# Make changes, then:
git add .
git commit -m "feat: your change description"
git push
```

Streamlit Cloud auto-deploys on every push to `main`.

---

## 📄 License

MIT License — Free for educational and personal use.

---

**Developed by Bhaskar Shivaji Kumbhar**
*MedBotX v2.0 — Advanced AI Medical Assistant · 2026*
