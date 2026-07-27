<div align="center">

# 🏢 VirtuWork Pro

### AI-Powered Multi-Agent Workplace Simulation Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM_API-6366F1?style=for-the-badge)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

**VirtuWork Pro** is a full-stack AI simulation platform that immerses users in realistic workplace scenarios. It generates dynamic, role-specific projects and lets users interact with **AI-powered agents** — an HR lead, a team peer, and a client — while completing technical tasks, receiving automated code evaluations, real-time soft-skill analysis, and a comprehensive AI-generated performance report with downloadable certificates.

</div>

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Multi-Agent System** | 7 specialized AI agents (Thinker, Planner, Manager, Conversation, Evaluator, Soft Skills, Performance) powered by OpenRouter LLMs |
| 🏗️ **Dynamic Project Generation** | AI generates unique, industry-relevant projects tailored to user role & education |
| 💬 **Role-Based Conversations** | Chat with 3 distinct AI personas — HR (onboarding), Peer (technical help), Client (requirements) |
| 📝 **Task Evaluation** | Upload ZIP submissions — AI evaluates code against a generated gold-standard solution |
| 🎯 **Adaptive Difficulty** | Manager Agent dynamically adjusts task complexity based on user performance |
| 🧠 **Soft Skills Analysis** | Real-time professionalism, clarity, and confidence scoring via rolling heatmap |
| 📊 **Performance Reports** | AI-generated final reports with communication, technical, and problem-solving breakdowns |
| 🏆 **Certificates** | Auto-generated completion certificates with PDF download (Playwright) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Django Templates)                   │
│   Landing • Signup • Login • Dashboard • Simulation Chat        │
│   Loading • Profile • Certificate • Final Report • How It Works │
└────────────────────────────┬────────────────────────────────────┘
                             │  Django Views (Session Auth)
┌────────────────────────────▼────────────────────────────────────┐
│                         Django 5.x                              │
│  ┌──────────┐ ┌──────────────┐ ┌───────────┐ ┌──────────────┐  │
│  │   core   │ │  simulation  │ │  agents   │ │  evaluation  │  │
│  │  ──────  │ │  ──────────  │ │  ──────   │ │  ──────────  │  │
│  │ Auth     │ │ Sim CRUD     │ │ Convers.  │ │ Submissions  │  │
│  │ Signup   │ │ Chat Views   │ │ Messages  │ │ Scores       │  │
│  │ Login    │ │ Task Submit  │ │ Summaries │ │ Progress     │  │
│  │ Dashboard│ │ AI Pipeline  │ │           │ │ Reports      │  │
│  │ Profile  │ │ Certificates │ │           │ │ Screenshots  │  │
│  └──────────┘ └──────────────┘ └───────────┘ └──────────────┘  │
│                                                                  │
│  ┌──────────────────── AI Agent Layer ────────────────────────┐  │
│  │ ThinkerAgent   → Project design + gold-standard solutions  │  │
│  │ PlannerAgent   → Break project into 5-7 subtasks           │  │
│  │ ManagerAgent   → Adaptive difficulty adjustment            │  │
│  │ ConversationAgent → HR / Peer / Client chat personas       │  │
│  │ TaskEvaluatorAgent → ZIP code review & scoring             │  │
│  │ SoftSkillsAgent    → Real-time communication analysis      │  │
│  │ PerformanceAgent   → Final report generation               │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌─────────┐  ┌──────────┐  ┌────────────┐
         │  MySQL   │  │OpenRouter│  │ Playwright │
         │ (RDBMS)  │  │(LLM API) │  │  (PDF Gen) │
         └─────────┘  └──────────┘  └────────────┘
```

---

## 🤖 Multi-Agent System

VirtuWork Pro orchestrates **7 specialized AI agents**, each powered by curated LLM model pools via OpenRouter:

### 1. Thinker Agent
- **Purpose**: Designs the project concept and generates gold-standard task solutions
- **Models**: Heavy Reasoning + Thinking models (DeepSeek R1, Arcee Trinity Large)
- **Output**: Project title, description, agent persona names, reference code solutions

### 2. Planner Agent
- **Purpose**: Breaks the project into 5–7 logical subtasks with metadata
- **Models**: General Purpose + Heavy Reasoning models
- **Output**: Ordered task list with instructions, submission requirements, and file extensions

### 3. Manager Agent
- **Purpose**: Dynamically adjusts upcoming task difficulty based on user performance
- **Models**: Heavy Reasoning + General Purpose models
- **Logic**: Score > 85% → increase complexity | Score < 55% → simplify with scaffolding

### 4. Conversation Agent (HR / Peer / Client)
- **Purpose**: Provides role-specific chat interactions with distinct personalities
- **Models**: Fast Chat models (Gemma 3, Arcee Trinity Mini, Liquid LFM)
- **Personas**:
  - **HR**: Professional onboarding guidance
  - **Peer**: Casual technical assistance and hints
  - **Client**: Business-oriented requirements and feedback

### 5. Task Evaluator Agent
- **Purpose**: Evaluates user-submitted ZIP files against the gold-standard solution
- **Models**: Evaluation models (Nemotron, GPT-OSS) + Heavy Reasoning
- **Criteria**: Completeness, logic correctness, accuracy vs. reference, best practices

### 6. Soft Skills Agent
- **Purpose**: Analyzes each user message for workplace communication quality
- **Models**: Fast Chat models for real-time scoring
- **Metrics**: Professionalism (0–100), Clarity (0–100), Confidence (0–100)
- **Tracking**: Rolling average heatmap updated per message

### 7. Performance Agent
- **Purpose**: Generates the comprehensive final simulation report
- **Models**: Evaluation + Thinking models
- **Output**: Overall score, communication/technical/problem-solving breakdowns, strengths, weaknesses

### LLM Model Pools

| Pool | Models | Use Case |
|---|---|---|
| **Thinking** | DeepSeek R1, Liquid LFM Thinking | Deep reasoning tasks |
| **Coding** | Qwen3 Coder, Llama 3.3 70B, Hermes 3 405B | Code generation & solutions |
| **Fast Chat** | Arcee Trinity Mini, Gemma 3 4B, Liquid LFM | Real-time conversation |
| **Heavy Reasoning** | Arcee Trinity Large, Gemma 3 27B, Mistral Small 3.1 | Complex analysis |
| **Evaluation** | Nemotron Nano, GPT-OSS 120B/20B | Scoring & assessment |
| **General Purpose** | GLM 4.5, Gemma 3 12B, Qwen3 4B | Planning & misc tasks |

---

## 🔄 Simulation Workflow

```
User Selects Role + Education
         │
         ▼
┌────────────────────┐
│ 1. ThinkerAgent    │  → Generates project concept + agent names
└────────┬───────────┘
         ▼
┌────────────────────┐
│ 2. PlannerAgent    │  → Creates 5-7 ordered subtasks
└────────┬───────────┘
         ▼
┌────────────────────┐
│ 3. Setup Phase     │  → Creates HR/Peer/Client conversations + HR greeting
└────────┬───────────┘
         ▼
┌─────────────────────────────────────────────┐
│ 4. Simulation Loop (per task)               │
│   ┌─────────────────────────────────────┐   │
│   │ Chat with Agents (HR/Peer/Client)   │   │
│   │  → SoftSkillsAgent scores each msg  │   │
│   └──────────────┬──────────────────────┘   │
│                  ▼                           │
│   ┌─────────────────────────────────────┐   │
│   │ Submit Task (ZIP upload)            │   │
│   │  → TaskEvaluatorAgent scores code   │   │
│   │  → 3 attempts max per task          │   │
│   │  → ManagerAgent adjusts difficulty  │   │
│   └──────────────┬──────────────────────┘   │
│                  ▼                           │
│   Discussion tasks auto-complete on keyword │
└─────────────────────┬───────────────────────┘
                      ▼
┌────────────────────────────────┐
│ 5. PerformanceAgent            │  → Final report + certificate
└────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
virtuwork_pro/
├── virtuwork_pro/           # Django project config
│   ├── settings.py          # All configurations (DB, API keys, apps)
│   ├── urls.py              # Root URL routing (20+ endpoints)
│   ├── wsgi.py              # WSGI entry point
│   └── asgi.py              # ASGI entry point
│
├── core/                    # Core app (Auth & Navigation)
│   ├── models.py            # UserProfile (extends Django User)
│   └── views.py             # Landing, signup, login, dashboard, profile
│
├── simulation/              # Simulation engine (Main app)
│   ├── models.py            # Simulation, Task
│   ├── views.py             # Create/delete/resume sim, chat, submit,
│   │                        #   end report, certificate, PDF download
│   ├── agents.py            # All 7 AI agents (BaseAgent + specialists)
│   ├── utils/               # Certificate PDF generation
│   └── templatetags/        # Custom Django template filters
│
├── agents/                  # Agent data models
│   └── models.py            # Conversation, Message, SharedSummary
│
├── evaluation/              # Evaluation & reporting
│   └── models.py            # TaskSubmission, SubmissionScreenshot,
│                            #   ProgressReport
│
├── templates/               # 13 Django HTML templates
│   ├── index.html           # Landing page
│   ├── signup.html          # User registration
│   ├── login.html           # User authentication
│   ├── dashboard.html       # Simulation management hub
│   ├── loading.html         # AI project generation loading screen
│   ├── simulation_chat.html # Main simulation interface (chat + tasks)
│   ├── explain.html         # How It Works page
│   ├── profile.html         # User profile + certificates
│   ├── certificate.html     # Completion certificate view
│   ├── certificate_pdf.html # Print-optimized certificate for PDF
│   ├── final_report.html    # AI-generated performance report
│   ├── demo.html            # Demo / hero landing variant
│   └── base.html            # Base template
│
├── submissions/             # User uploaded ZIP files (gitignored)
│   └── zips/
│
├── manage.py                # Django CLI
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10+
- **MySQL** 8.0+
- **pip** (Python package manager)
- [OpenRouter](https://openrouter.ai) API key(s) (free models available)
- [Playwright](https://playwright.dev/python/) (for certificate PDF generation)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/virtuwork-pro.git
cd virtuwork-pro
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django mysqlclient requests

# PDF Certificate Generation
pip install playwright
playwright install chromium
```

### 4. Configure API Keys

Open `virtuwork_pro/settings.py` and add your OpenRouter API keys:

```python
OPENROUTER_API_KEYS = [
    "sk-or-v1-your-key-here",
    # Add multiple keys for rotation / rate-limit resilience
]
```

> **Tip**: For production, move API keys to environment variables or a `.env` file.

### 5. Set Up the Database

```bash
# Create MySQL database
mysql -u root -p -e "CREATE DATABASE virtuwork CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
python manage.py makemigrations core agents simulation evaluation
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Run the Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to see the landing page.

---

## 🛣️ URL Endpoints

### Authentication & Navigation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET/POST | `/signup/` | User registration |
| GET/POST | `/login/` | User login |
| GET | `/logout/` | Logout (redirects to landing) |
| GET | `/dashboard/` | Simulation management dashboard |
| GET | `/profile/` | User profile with certificates |
| GET | `/how-it-works/` | Platform explainer page |

### Simulation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/simulation/create/` | Create new simulation (role + education) |
| POST | `/simulation/delete/<id>/` | Delete a simulation |
| GET | `/simulation/resume/<id>/` | Resume an ongoing simulation |
| GET | `/simulation/chat/<id>/` | Main simulation chat interface |
| GET | `/simulation/initiate-ai/<id>/` | Trigger AI project generation pipeline |
| POST | `/simulation/submit-task/` | Submit ZIP file for evaluation |
| GET | `/simulation/end-simulation-report/<id>/` | Generate final AI performance report |

### AJAX APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send-message-ajax/` | Send chat message (returns JSON with AI response) |
| GET | `/api/check-email/` | Check if email exists (signup validation) |

### Certificates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/certificate/<id>/` | View completion certificate |
| GET | `/certificate/download/<id>/` | Download certificate as PDF |

---

## 📊 Database Schema

```
users (Django Auth)          simulations                 tasks
├── id                       ├── id                      ├── id
├── username                 ├── user_id (FK)            ├── simulation_id (FK)
├── email                    ├── role_title              ├── title
├── password (hashed)        ├── education               ├── instruction
└── ...                      ├── project_title           ├── difficulty (1-3)
                             ├── description             ├── is_completed
user_profiles                ├── status (ongoing/        ├── is_skipped
├── user_id (1:1)            │    paused/completed)      ├── order
└── education                ├── hr_name                 ├── requires_submission
                             ├── peer_name               ├── attempts (max 3)
conversations                ├── client_name             ├── score (0-100)
├── simulation_id (FK)       ├── expected_output_        ├── feedback
├── agent_type               │    template               └── expected_file_extension
│   (HR/PEER/CLIENT)         ├── final_report_data
└── session_id               ├── soft_skills_data        task_submissions
                             └── created_at              ├── task_id (FK)
messages                                                 ├── zip_file
├── conversation_id (FK)     progress_reports            ├── attempt_number
├── sender                   ├── simulation_id (1:1)     ├── score
├── text                     ├── overall_score           ├── feedback
└── timestamp                ├── technical_skills        ├── is_success
                             ├── communication_skills    └── created_at
shared_summaries             └── ai_feedback
├── simulation_id (FK)
├── summary_text
└── last_message_count
```

---

## ⚙️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Django 5.x, Django Template Engine |
| **Database** | MySQL 8.0 |
| **AI / LLM** | OpenRouter API (20+ free models with key rotation & model fallback) |
| **PDF Generation** | Playwright (headless Chromium) |
| **Frontend** | HTML5, CSS3, JavaScript, Tailwind CSS (demo) |
| **Auth** | Django session-based authentication |

---

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test core
python manage.py test simulation
python manage.py test agents
python manage.py test evaluation
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using Django, OpenRouter, and Multi-Agent AI**

</div>
