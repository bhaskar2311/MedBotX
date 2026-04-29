# 🏥 MedBotX — Advanced Medical Chatbot with Memory

> **Developed by Bhaskar Shivaji Kumbhar**

An AI-powered healthcare chatbot built with **FastAPI**, **LangChain**, and **OpenAI GPT-4o** that provides accurate medical information while maintaining both temporary (session) and permanent (user) conversational memory.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI-Powered Q&A** | GPT-4o via LangChain for accurate, safe medical responses |
| 🧠 **Dual Memory** | Temporary session memory + permanent user memory (DB-backed) |
| 🔐 **JWT Auth** | Secure registration, login, and token refresh |
| 🩺 **Medical Profile** | Store allergies, conditions, medications for personalised context |
| 🎨 **Modern UI** | Beautiful Streamlit frontend with chat bubbles & medical theming |
| 📊 **REST API** | Full FastAPI with auto-generated Swagger/ReDoc docs |
| 🐳 **Docker Ready** | Single `docker-compose up` to run the full stack |
| 📝 **Structured Logging** | File + console logs with session tracking |
| ✅ **Test Suite** | Async pytest tests for API and memory layer |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Streamlit UI)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (REST)
┌────────────────────────▼────────────────────────────────────┐
│              FastAPI API Layer  (/api/v1)                   │
│  /auth/register  /auth/login  /chat/  /memory/             │
└──────────┬────────────────────────────┬─────────────────────┘
           │                            │
┌──────────▼──────────┐     ┌──────────▼──────────────────────┐
│   ChatbotService    │     │       MemoryManager             │
│  LangChain + OpenAI │◄────│  Temporary (dict) + Permanent   │
│      GPT-4o         │     │  (SQLite / PostgreSQL)          │
└─────────────────────┘     └─────────────────────────────────┘
```

---

## 📁 Project Structure

```
MedBotX/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py        # Register, Login, Token
│   │   │   ├── chat.py        # Chat endpoint + session mgmt
│   │   │   ├── memory.py      # Load/save/update memory
│   │   │   └── health.py      # Health check
│   │   └── router.py
│   ├── auth/
│   │   └── dependencies.py    # JWT dependencies
│   ├── core/
│   │   ├── config.py          # Pydantic settings
│   │   ├── security.py        # JWT + password hashing
│   │   └── logging_config.py
│   ├── db/
│   │   ├── database.py        # Async SQLAlchemy engine
│   │   └── models.py          # ORM models
│   ├── memory/
│   │   └── memory_manager.py  # Temp + permanent memory
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response schemas
│   ├── services/
│   │   └── chatbot_service.py # LangChain + OpenAI integration
│   └── main.py                # FastAPI app factory
├── frontend/
│   └── app.py                 # Streamlit UI
├── tests/
│   ├── test_chat.py
│   └── test_memory.py
├── Project Documents/         # HLD, LLD, Requirements PDFs
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── run.py
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/MedBotX.git
cd MedBotX
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env        # Windows
# OR
cp .env.example .env          # Mac/Linux
```

Edit `.env` and add your **OpenAI API key**:

```env
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your_random_32_char_secret_key
```

### 3. Start the API Server

```bash
python run.py
# OR
uvicorn app.main:app --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start the Frontend (new terminal)

```bash
python run.py frontend
# OR
streamlit run frontend/app.py
```

Open: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker

```bash
# Copy and configure .env
copy .env.example .env

# Run full stack
docker-compose up --build

# Stop
docker-compose down
```

- **API:** http://localhost:8000
- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET  | `/api/v1/auth/me` | Get current user |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat/` | Send message, get response |
| POST | `/api/v1/chat/session/new` | Create anonymous session |
| GET  | `/api/v1/chat/history/{session_id}` | Get chat history |
| DELETE | `/api/v1/chat/session/{session_id}` | Clear session |

### Memory

| Method | Endpoint | Description |
|---|---|---|
| GET  | `/api/v1/memory/load` | Load permanent memory |
| POST | `/api/v1/memory/save` | Save memory |
| PUT  | `/api/v1/memory/medical-context` | Update medical profile |
| DELETE | `/api/v1/memory/clear` | Delete all memory |

### Example Chat Request

```json
POST /api/v1/chat/
{
  "message": "What are the symptoms of diabetes?",
  "session_id": "optional-existing-session-id"
}
```

Response:
```json
{
  "response": "Type 2 diabetes symptoms include...",
  "session_id": "abc-123",
  "timestamp": "2026-04-29T12:00:00Z",
  "model": "gpt-4o"
}
```

---

## 🔗 Connect to GitHub

### First Time Setup

```bash
# Initialise git (already done if you cloned)
git init
git add .
git commit -m "Initial commit: MedBotX v1.0.0"

# Create repo on GitHub (via website or GitHub CLI)
gh repo create MedBotX --public --description "Advanced Medical Chatbot with Memory"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/MedBotX.git
git branch -M main
git push -u origin main
```

### Subsequent Pushes

```bash
git add .
git commit -m "feat: your change description"
git push
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🛡️ Safety & Compliance

- MedBotX provides **general medical information only** — never a diagnosis
- All emergency symptoms trigger immediate advice to call emergency services
- Data encrypted in transit (HTTPS in production) and at rest
- JWT-secured endpoints for all authenticated features
- No sensitive medical data stored for anonymous users

---

## 🔮 Roadmap & Future Enhancements

- [ ] Voice interface (Whisper API)
- [ ] EHR/EMR integration (HL7 FHIR)
- [ ] Multilingual support
- [ ] Prometheus + Grafana monitoring dashboard
- [ ] PostgreSQL production database migration
- [ ] Drug interaction checker
- [ ] Symptom severity triage scoring
- [ ] PDF medical report analysis

---

## 📄 License

MIT License — Free for educational and personal use.

---

**Developed by Bhaskar Shivaji Kumbhar**  
*MedBotX — Advanced Medical Chatbot with Memory*
