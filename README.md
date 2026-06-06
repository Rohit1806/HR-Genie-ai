<p align="center">
  <h1 align="center">🧞 HRGenie AI</h1>
  <p align="center"><strong>Next-Generation AI-Powered HR Management Platform</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-18-blue?logo=react" alt="React" />
    <img src="https://img.shields.io/badge/TypeScript-5.4-blue?logo=typescript" alt="TypeScript" />
    <img src="https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-purple?logo=google" alt="Gemini AI" />
    <img src="https://img.shields.io/badge/Docker-Compose-blue?logo=docker" alt="Docker" />
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
  </p>
  <p align="center">
    <a href="https://your-app.vercel.app">🌐 Live Demo</a> •
    <a href="https://your-api.onrender.com/docs">📖 API Docs</a> •
    <a href="https://github.com/Rohit1806/HR-Genie-ai">💻 GitHub</a>
  </p>
</p>

---

## 🌟 Overview

**HRGenie AI** is a comprehensive, enterprise-grade Human Resource Management System powered by **Google Gemini AI**. It modernizes every aspect of human resource management — from recruitment and onboarding to performance reviews and payroll — with intelligent AI assistance at every step, featuring **12 custom AI engines** at its core.

Built with a scalable microservices architecture, it supports **5,000+ employee logins** with real-time data processing, mobile-responsive UI, and deep AI automation across all HR workflows.

### Why HRGenie AI?

- ✅ **AI-driven resume screening & evaluation** without human intervention
- ✅ **Multi-role login system** with tailored access for Admin, Senior Manager, HR Recruiter & Employee
- ✅ **Personalized dashboards** per role with real-time analytics
- ✅ **Voice-powered candidate screening** using speech-to-text AI
- ✅ **End-to-end HR automation** — attendance, payroll, leaves, performance, recruitment
- ✅ **Mobile responsive** — optimized for both web and mobile access
- ✅ **Scalable** — designed to handle 5,000+ concurrent employee logins

---

## 🚀 Live Links

| Service | URL |
|---------|-----|
| 🌐 Frontend (Vercel) | https://your-app.vercel.app |
| ⚙️ Backend API (Render) | https://your-api.onrender.com |
| 📖 Swagger API Docs | https://your-api.onrender.com/docs |
| 📘 ReDoc API Docs | https://your-api.onrender.com/redoc |

---

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| 🔑 **Admin** | admin@demo.hrgenie.ai | Demo@1234 |
| 📈 **Senior Manager** | manager@demo.hrgenie.ai | Demo@1234 |
| 👥 **HR Recruiter** | hr@demo.hrgenie.ai | Demo@1234 |
| 👤 **Employee** | employee@demo.hrgenie.ai | Demo@1234 |

---

## ✨ Key Features

### Core HR Modules

| Module | Features |
|--------|----------|
| 🔐 **Authentication & Security** | JWT + HTTP-only refresh tokens, RBAC (4 roles), rate limiting, password reset |
| 👥 **Employee Management** | Directory, profiles, dynamic org chart, onboarding wizard, document management |
| 📋 **Recruitment Pipeline** | Job postings, candidate pipeline, interactive Kanban board, application tracking |
| ⏰ **Attendance Management** | Clock in/out, monthly calendar, team view, attendance regularization workflow |
| 🏖️ **Leave Management** | Apply/approve flow, balance tracking, holiday calendar |
| 💰 **Payroll (Indian Regime)** | Auto-compute PF/ESI/TDS, payslip generation, Indian tax regime support |
| 📊 **Performance & OKRs** | Goal setting, 360° reviews, performance cycles, score tracking |
| 📈 **Analytics Dashboards** | Role-based dashboards, workforce composition, real-time trend charts |

---

## 🤖 AI-Powered Systems — 12 Engine Architecture

All AI engines are located under `backend/app/ai/engines/` and powered by **Google Gemini 2.5 Flash**:

| # | Engine | Description |
|---|--------|-------------|
| 1 | 📄 **Resume Intelligence** | Parses PDF/DOCX resumes using PyMuPDF to extract structured contact info, job history, and skills |
| 2 | 🎯 **Candidate Matching** | Computes semantic similarity between candidate profiles and job descriptions using SentenceTransformers |
| 3 | 🧠 **Candidate Evaluation** | Gemini-powered scoring for fit, experience, and skills with pros/cons/recommendations |
| 4 | 🏆 **Candidate Ranking** | Auto stack-ranks all applicants for a position, prioritizing highest matches |
| 5 | 💬 **Interview Generator** | Curates customized behavioral and technical interview questions tailored to candidate background |
| 6 | 🎤 **Voice Screening** | Transcribes voice interviews using Faster-Whisper and evaluates responses for semantic depth |
| 7 | 🤖 **HR Copilot** | Persistent conversational AI assistant for drafting emails, offer letters, and HR policy queries |
| 8 | 📚 **Skill Gap Analyzer** | Audits employee skills against job profiles and recommends learning targets |
| 9 | 📊 **Performance Insights** | Summarizes peer/manager/self-review feedback into actionable growth metrics |
| 10 | 🚀 **Promotion Recommender** | Data-driven readiness scoring using tenure, reviews, and training history |
| 11 | 🏢 **Workforce Analytics** | Structural analysis on departmental composition and employee trends |
| 12 | ⚠️ **Attrition Predictor** | Identifies flight risks by evaluating tenure, review trends, and regularization patterns |

---

## 👥 Multi-Role Login System (RBAC)

| Role | Scope | Key Capabilities |
|------|-------|-----------------|
| 🔑 **Admin** | Full system access | CRUD on employee directory, payroll runs, system configs, enterprise analytics |
| 📈 **Senior Manager** | Team supervision | Attendance tracking, leave approvals, regularization reviews, OKR evaluation |
| 👥 **HR Recruiter** | Talent acquisition | Job postings, Kanban pipeline, AI resume parsing, candidate matching & ranking |
| 👤 **Employee** | Self-service | Clock in/out, leave applications, payslip downloads, OKR management, AI Copilot |

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  Frontend (React 18 + Vite)                    │
│     TypeScript │ MUI v5 │ TailwindCSS │ Zustand │ Recharts    │
└───────────────────────────┬────────────────────────────────────┘
                            │ REST API + WebSocket
┌───────────────────────────┴────────────────────────────────────┐
│                   Backend (FastAPI 0.111)                      │
│        SQLAlchemy 2.0 │ Pydantic v2 │ JWT Auth │ Alembic      │
├────────────────────────────────────────────────────────────────┤
│    AI Layer: Gemini 2.5 Flash │ SentenceTransformers          │
│    Faster-Whisper │ HuggingFace Transformers │ spaCy          │
├──────────┬───────────┬──────────┬─────────────────────────────┤
│PostgreSQL│   Redis   │  Celery  │  File Storage (/uploads)    │
│    16    │     7     │  Workers │  Resume PDFs & Documents    │
└──────────┴───────────┴──────────┴─────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | 0.111.0 | Async API framework |
| SQLAlchemy | 2.0.30 | ORM (async) |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Caching + message broker |
| Celery | 5.4.0 | Background task queue |
| Alembic | 1.13.1 | Database migrations |
| asyncpg | 0.29.0 | Async PostgreSQL driver |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18 | UI framework |
| TypeScript | 5.4 | Type safety |
| Vite | 5.3 | Build tool |
| MUI | v5.15 | Component library |
| TailwindCSS | 3.4 | Utility CSS + dark theme |
| React Query | v5.45 | Server state management |
| Zustand | 4.5 | Client state management |
| Recharts | 2.12 | Data visualization |

### AI / ML
| Technology | Purpose |
|-----------|---------|
| Google Gemini 2.5 Flash | Primary LLM (free tier) |
| SentenceTransformers | Semantic embeddings |
| Faster-Whisper | Speech-to-text transcription |
| HuggingFace Transformers | NLP processing |
| spaCy | Text analysis |
| PyMuPDF | PDF parsing for resumes |

---

## ✨ Extra Features

| Feature | Description |
|---------|-------------|
| 🤖 **Persistent AI Copilot Drawer** | Slide-out AI assistant accessible from any screen in the system |
| 📅 **Attendance Regularization Workflow** | Employees dispute missed punches → manager approval queue |
| 🏢 **Dynamic Interactive Org Chart** | Auto-visualizes reporting hierarchies from database relationships |
| 🎤 **Voice Screening Interface** | Simulates telephone screening by transcribing and analyzing voice responses |
| 📋 **Interactive Kanban Pipeline** | Drag-and-drop recruitment board (Screening → Interview → Offered → Hired) |
| 🌙 **HSL Dark Mode** | 12 distinct dark theme variations with micro-animations |
| 🔔 **WebSocket Notifications** | Real-time notifications across all user roles |

---

## 📁 Project Structure

```
hrgenie-ai/
├── backend/
│   ├── alembic/             # Database migrations
│   │   └── versions/        # Migration history
│   ├── app/
│   │   ├── api/v1/          # API endpoints (auth, employees, recruitment, etc.)
│   │   ├── ai/engines/      # 12 AI engine modules
│   │   ├── core/            # Security, config, RBAC middleware
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic v2 validation schemas
│   │   ├── services/        # Business logic (attendance, payroll, etc.)
│   │   ├── utils/           # PDF export, email helpers
│   │   └── workers/         # Celery task definitions
│   ├── scripts/             # DB initialization and seed data scripts
│   ├── uploads/             # Resume and document storage
│   ├── .env.example         # Environment variable template
│   ├── runtime.txt          # Python 3.11.9 pinned for Render
│   ├── Dockerfile           # Backend container setup
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client functions
│   │   ├── components/      # UI components, layouts, charts
│   │   ├── hooks/           # React Query & WebSocket hooks
│   │   ├── pages/           # Role-based dashboards and pages
│   │   ├── store/           # Zustand state configs
│   │   └── types/           # TypeScript interfaces
│   ├── tailwind.config.ts   # Custom design tokens
│   ├── vite.config.ts       # Build configuration
│   └── vercel.json          # Vercel deployment config
├── render.yaml              # Render deployment blueprint
├── docker-compose.yml       # Full stack orchestration
├── .gitignore               # Excludes venv, node_modules, .env
└── README.md                # This file
```

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
# Application
APP_ENV=development
APP_NAME=HRGenie AI
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://hrgenie:hrgenie123@localhost:5432/hrgenie_db

# Cache & Queue
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Auth
JWT_SECRET_KEY=your-super-secret-key-minimum-64-characters-long
JWT_ALGORITHM=HS256

# AI
GEMINI_API_KEY=your-gemini-api-key-from-google-ai-studio
GEMINI_MODEL=gemini-2.5-flash

# Storage
STORAGE_PROVIDER=local
LOCAL_STORAGE_PATH=./uploads
```

---

## ⚡ Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Rohit1806/HR-Genie-ai.git
cd HR-Genie-ai

# Setup environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# Start all services
docker-compose up -d --build

# Run migrations and seed demo data
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed_demo_data.py

# Access the app
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

```bash
# ── Backend ──
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
# Edit .env: add GEMINI_API_KEY and JWT_SECRET_KEY

# Start Postgres and Redis
docker-compose up postgres redis -d

# Run migrations and seed
alembic upgrade head
python scripts/seed_demo_data.py

# Start API server
uvicorn app.main:app --reload

# ── Frontend ──
cd ../frontend
npm install
npm run dev
```

### Verify Installation
- **Frontend:** http://localhost:5173/login
- **API Docs:** http://localhost:8000/docs
- Login with `admin@demo.hrgenie.ai` / `Demo@1234`

---

## 📖 API Documentation

FastAPI auto-generates interactive docs:

| Doc Type | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### API Endpoints Overview

| Module | Base Path | Auth |
|--------|-----------|------|
| Authentication | `/api/v1/auth/*` | Partial |
| Employees | `/api/v1/employees/*` | ✅ Required |
| Recruitment | `/api/v1/recruitment/*` | ✅ Required |
| Attendance | `/api/v1/attendance/*` | ✅ Required |
| Leave | `/api/v1/leaves/*` | ✅ Required |
| Payroll | `/api/v1/payroll/*` | ✅ Required |
| Performance | `/api/v1/performance/*` | ✅ Required |
| Analytics | `/api/v1/analytics/*` | ✅ Required |
| AI Engines | `/api/v1/ai/*` | ✅ Required |
| WebSocket | `/api/v1/ws/*` | ✅ Required |

---

## 🚢 Deployment

### Backend → Render
1. Push code to GitHub
2. Connect repo to [Render](https://render.com)
3. Use `render.yaml` blueprint (auto-configured)
4. Set environment variables in Render dashboard
5. Run: `alembic upgrade head && python scripts/seed_demo_data.py`

### Frontend → Vercel
1. Import `frontend/` directory to [Vercel](https://vercel.com)
2. Build command: `npm run build`
3. Output directory: `dist`
4. Add env variable: `VITE_API_BASE_URL=https://your-api.onrender.com`

---

<p align="center">
  Built with ❤️ and AI by <strong>Rohit Mani</strong>
</p>
