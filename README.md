<p align="center">
  <h1 align="center">🧞 HRGenie AI</h1>
  <p align="center"><strong>Next-Generation AI-Powered HR Management Platform</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-18-blue?logo=react" alt="React" />
    <img src="https://img.shields.io/badge/TypeScript-5.4-blue?logo=typescript" alt="TypeScript" />
    <img src="https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Gemini-1.5%20Flash-purple?logo=google" alt="Gemini AI" />
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
  </p>
</p>

---

## 🌟 Overview

HRGenie AI is a comprehensive, enterprise-grade HR Management System powered by **Google Gemini AI**. It modernizes every aspect of human resource management — from recruitment and onboarding to performance reviews and payroll — with intelligent AI assistance at every step.

## 🚀 Key Features

### Core HR Modules
| Module | Features |
|--------|----------|
| **🔐 Authentication** | JWT + refresh tokens, RBAC (4 roles), rate limiting, password reset |
| **👥 Employee Management** | Directory, profiles, org chart, onboarding wizard, document management |
| **📋 Recruitment** | Job postings, candidate pipeline, Kanban board, application tracking |
| **⏰ Attendance** | Clock in/out, monthly calendar, team view, regularization requests |
| **🏖️ Leave Management** | Apply/approve flow, balance tracking, holiday calendar |
| **💰 Payroll** | Auto-compute (PF/ESI/TDS), payslips, Indian tax regime support |
| **📊 Performance** | OKR goals, 360° reviews, performance cycles, score tracking |
| **📈 Analytics** | Role-based dashboards, workforce composition, trend charts |

### 🤖 AI-Powered Systems (12 Engines)
1. **Resume Intelligence** — Extract structured data from PDF/DOCX resumes
2. **Candidate Matching** — Semantic matching of candidates to job requirements
3. **Candidate Evaluation** — AI scoring (fit, skill, experience) with recommendations
4. **Candidate Ranking** — Stack-rank all candidates for a position
5. **Interview Generator** — Role-specific interview question generation
6. **Voice Screening** — Transcribe and evaluate voice interviews via Whisper
7. **HR Copilot** — Conversational AI assistant for HR professionals
8. **Skill Gap Analyzer** — Identify team and individual skill gaps
9. **Performance Insights** — AI-generated review summaries and feedback
10. **Promotion Recommender** — Data-driven promotion scoring
11. **Workforce Analytics** — AI-powered workforce trend analysis
12. **Attrition Predictor** — Employee flight risk prediction

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                │
│   React 18 │ TypeScript │ MUI v5 │ TailwindCSS │ Recharts │
└──────────────────────┬─────────────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────┴─────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│   FastAPI │ SQLAlchemy 2.0 │ Pydantic v2 │ JWT Auth       │
├────────────────────────────────────────────────────────────┤
│   AI Layer: Gemini 1.5 Flash │ SentenceTransformers       │
│   Whisper │ HuggingFace Transformers │ spaCy              │
├──────────┬──────────┬──────────┬──────────────────────────┤
│ PostgreSQL│  Redis   │  Celery  │  File Storage           │
│    16     │    7     │  Workers │  /uploads               │
└──────────┴──────────┴──────────┴──────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | 0.111 | API framework |
| SQLAlchemy | 2.0 | ORM (async) |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Caching + sessions |
| Celery | 5.4 | Background tasks |
| Alembic | 1.13 | DB migrations |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18 | UI framework |
| TypeScript | 5.4 | Type safety |
| Vite | 5.3 | Build tool |
| MUI | 5.15 | Component library |
| TailwindCSS | 3.4 | Utility CSS |
| React Query | 5.45 | Server state |
| Zustand | 4.5 | Client state |
| Recharts | 2.12 | Charts |

### AI / ML
| Technology | Purpose |
|-----------|---------|
| Google Gemini 1.5 Flash | LLM (free tier) |
| SentenceTransformers | Embeddings |
| OpenAI Whisper | Speech-to-text |
| HuggingFace Transformers | NLP |
| spaCy | Text processing |
| PyMuPDF | PDF parsing |

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@demo.hrgenie.ai | Demo@1234 |
| **Senior Manager** | manager@demo.hrgenie.ai | Demo@1234 |
| **HR Recruiter** | hr@demo.hrgenie.ai | Demo@1234 |
| **Employee** | employee@demo.hrgenie.ai | Demo@1234 |

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16
- Redis 7
- Docker (optional)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/hrgenie-ai.git
cd hrgenie-ai

# Copy environment files
cp backend/.env.example backend/.env
# Edit backend/.env — add your GEMINI_API_KEY

# Start all services
docker-compose up -d

# Run migrations and seed data
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed_demo_data.py

# Access the app
# API: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

### Option 2: Local Development

```bash
# ── Backend ──
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
# Edit .env: add GEMINI_API_KEY, set JWT_SECRET_KEY

# Start Postgres and Redis (via Docker or local install)
docker-compose up postgres redis -d

# Run migrations + seed
alembic upgrade head
python scripts/seed_demo_data.py

# Start API
uvicorn app.main:app --reload

# ── Frontend ──
cd ../frontend
npm install
npm run dev
```

### 🎯 Verify Installation
- **Swagger UI**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173/login
- Login with `admin@demo.hrgenie.ai` / `Demo@1234`

## 📖 API Documentation

FastAPI auto-generates interactive API docs:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints Overview

| Module | Endpoints | Auth Required |
|--------|-----------|---------------|
| `/api/v1/auth/*` | Login, refresh, logout, password reset | Partial |
| `/api/v1/admin/setup` | First-time setup | No |
| `/api/v1/employees/*` | CRUD, org chart, documents | Yes |
| `/api/v1/recruitment/*` | Jobs, applications, AI evaluation | Yes |
| `/api/v1/attendance/*` | Clock in/out, team view | Yes |
| `/api/v1/leaves/*` | Apply, approve, balances | Yes |
| `/api/v1/payroll/*` | Runs, payslips | Yes |
| `/api/v1/performance/*` | Goals, reviews, scores | Yes |
| `/api/v1/analytics/*` | Dashboard data | Yes |
| `/api/v1/ai/*` | Copilot, AI scoring | Yes |
| `/api/v1/ws/*` | WebSocket notifications | Yes |

## 🚢 Deployment

### Backend → Render
1. Push to GitHub
2. Connect repo to Render
3. Use `render.yaml` blueprint
4. Set environment variables

### Frontend → Vercel
1. Import frontend directory to Vercel
2. Build command: `npm run build`
3. Output directory: `dist`
4. Set `VITE_API_BASE_URL` env var

## 📸 Screenshots

> Screenshots will be added once the application is deployed.

| Dashboard | Employee Directory | Recruitment Pipeline |
|:---------:|:------------------:|:--------------------:|
| *Admin Dashboard* | *Employee List* | *Kanban Board* |

| Performance | Payroll | AI Copilot |
|:-----------:|:-------:|:----------:|
| *Goals & Reviews* | *Payslip View* | *Chat Assistant* |

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  Built with ❤️ and AI by R.Rohit Mani
</p>
