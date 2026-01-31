# 🤖 
HR Telegram Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-316192.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**AI-Powered HR Assistant for Telegram**

A modern, intelligent HR chatbot that understands natural language (Arabic & English) and autonomously handles employee requests using Google Gemini's function calling capabilities.

[Features](#-features) • [Architecture](#-architecture) • [Setup](#-quick-start) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Usage Examples](#-usage-examples)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**HR** is an enterprise-grade HR management system delivered through Telegram. Unlike traditional chatbots with hardcoded intent matching, HR uses **Google Gemini's function calling** to autonomously understand requests and execute appropriate database operations.

### Why HR?

- **🧠 Zero Hardcoded Logic**: No if/else chains - the AI decides which functions to call
- **🌍 Bilingual Support**: Seamlessly handles Arabic and English conversations
- **⚡ Autonomous Agent**: Self-planning architecture with intelligent decision-making
- **🔒 Secure**: Role-based access control with encrypted credential management
- **📊 Production-Ready**: PostgreSQL backend with proper ORM and migrations

---

## ✨ Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **Leave Management** | Request leave, check balance, view history |
| **Employee Information** | Access personal details, department info, role |
| **Salary Queries** | View current salary and salary history |
| **Natural Language** | Understands context and conversational requests |
| **Smart Validation** | Automatic date validation, balance checking |
| **Real-time Updates** | Instant database synchronization |

### 🔐 Security Features

- Environment-based credential management
- Employee-Telegram account linking
- Session management with automatic unlinking
- Database transaction safety

### 🤖 AI Features

- **Context Awareness**: Remembers conversation flow
- **Multi-turn Dialogue**: Handles follow-up questions
- **Intent Understanding**: No keyword matching needed
- **Function Selection**: AI autonomously chooses appropriate database operations
- **Error Recovery**: Graceful handling of edge cases

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram User                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Natural Language
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Telegram Bot (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Message Handler                                    │  │
│  │  • Employee Authentication                            │  │
│  │  • Session Management                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Delegate to Agent
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Gemini AI Agent (Function Calling)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Understand Request                                │  │
│  │  2. Select Appropriate Functions                      │  │
│  │  3. Call Functions with Parameters                    │  │
│  │  4. Process Results                                   │  │
│  │  5. Generate Natural Response                         │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Database Operations
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (SQLAlchemy ORM)            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │ Employees   │ Departments │  Leaves     │  Salaries   │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Agent-Based Design**: Single `handle_message()` call delegates everything to Gemini
2. **Function Calling**: LLM autonomously selects and executes database operations
3. **Stateless Bot Layer**: Bot is a thin wrapper with zero business logic
4. **ORM Pattern**: SQLAlchemy for type-safe database operations
5. **Separation of Concerns**: Database, queries, agent, and bot are decoupled

---

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**: Core language
- **PostgreSQL 13+**: Primary database
- **SQLAlchemy 2.x**: ORM and database toolkit
- **pyTelegramBotAPI**: Telegram Bot API wrapper

### AI & NLP
- **Google Gemini 2.5 Flash**: LLM with function calling
- **google-genai**: Official Gemini Python SDK

### DevOps
- **python-dotenv**: Environment variable management
- **psycopg2**: PostgreSQL adapter

---

## 🚀 Quick Start

### Prerequisites

```bash
# System requirements
- Python 3.9 or higher
- PostgreSQL 13 or higher
- Telegram Bot Token (from @BotFather)
- Google Gemini API Key
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/HR-Telegram-Bot.git
cd HR-Telegram-Bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Setup database**
```bash
# Create PostgreSQL database
createdb hr_db

# Initialize schema
python scripts/setup_database.py

# Generate sample data (optional)
python scripts/generate_sample_data.py
```

6. **Run the bot**
```bash
python src/bot.py
```

---

## 📁 Project Structure

```
HR-Telegram-Bot/
│
├── 📄 README.md                    # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 LICENSE                      # MIT License
│
├── 📂 src/                         # Main application code
│   ├── __init__.py
│   ├── bot.py                      # Telegram bot entry point
│   ├── agent.py                    # Gemini AI agent
│   │
│   └── 📂 database/                # Database layer
│       ├── __init__.py
│       ├── config.py               # Database configuration
│       ├── models.py               # SQLAlchemy models
│       └── queries.py              # Database query operations
│
├── 📂 scripts/                     # Utility scripts
│   ├── setup_database.py           # Initialize database schema
│   ├── generate_sample_data.py    # Generate test data
│   ├── reset_database.py          # Reset database (DANGER)
│   └── test_queries.py            # Test database queries
│
├── 📂 tests/                       # Test suite
│   ├── __init__.py
│   ├── test_agent.py              # Agent tests
│   └── test_queries.py            # Query tests
│
└── 📂 docs/                        # Documentation
    ├── ARCHITECTURE.md             # System architecture details
    ├── DATABASE_SCHEMA.md          # Database schema documentation
    ├── DEPLOYMENT.md               # Production deployment guide
    └── 📂 images/                  # Diagrams and screenshots
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    DEPARTMENTS ||--o{ EMPLOYEES : has
    EMPLOYEES ||--o{ LEAVE_REQUESTS : submits
    EMPLOYEES ||--|| LEAVE_BALANCES : has
    EMPLOYEES ||--o{ SALARIES : receives
    EMPLOYEES ||--o| EMPLOYEE_CHAT_LINKS : links_to
    
    DEPARTMENTS {
        int department_id PK
        string department_name
        int manager_id FK
    }
    
    EMPLOYEES {
        int employee_id PK
        string full_name
        string email
        int department_id FK
        enum role
        date hire_date
        float salary
    }
    
    LEAVE_REQUESTS {
        int leave_id PK
        int employee_id FK
        date start_date
        date end_date
        string reason
        enum status
    }
    
    LEAVE_BALANCES {
        int employee_id PK_FK
        int total_days
        int used_days
        int remaining_days
    }
    
    SALARIES {
        int salary_id PK
        int employee_id FK
        float amount
        date effective_date
    }
    
    EMPLOYEE_CHAT_LINKS {
        int employee_id PK_FK
        string telegram_chat_id
        datetime linked_at
    }
```

### Table Details

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **departments** | Organizational structure | department_id, department_name, manager_id |
| **employees** | Employee master data | employee_id, full_name, email, role, salary |
| **leave_requests** | Leave applications | leave_id, employee_id, dates, status |
| **leave_balances** | Available leave days | employee_id, total_days, remaining_days |
| **salaries** | Salary history | salary_id, employee_id, amount, effective_date |
| **employee_chat_links** | Telegram authentication | employee_id, telegram_chat_id |

---

## 💬 Usage Examples

### Employee Registration

```
User: 12345
Bot:  ✅ Welcome, Ahmad Mohammad!
      🤖 Your AI assistant is ready.
      💬 Try asking:
      • 'What's my balance?'
      • 'بدي أعرف رصيدي'
      • 'Request 3 days leave next week'
```

### Natural Language Queries

```
User: What's my leave balance?
Bot:  📊 Your Leave Balance:
      • Total Days: 30
      • Used Days: 5
      • Remaining: 25 days
```

```
User: بدي أطلب إجازة من 15 فبراير لـ 20 فبراير
Bot:  ✅ Leave request submitted successfully!
      📅 Duration: 6 days
      📊 Remaining balance after approval: 19 days
      ⏳ Status: Pending approval
```

```
User: Show my salary info
Bot:  💰 Your Salary Information:
      • Current Salary: $8,500.00
      • Effective Date: 2020-01-15
      • Department: Information Technology
```

### Conversational Flow

```
User: Can I take leave next week?
Bot:  Let me check your balance... You have 25 days remaining. 
      Yes, you can request leave! What dates would you like?

User: Monday to Wednesday
Bot:  ✅ Leave request submitted for 3 days (Feb 12-14, 2026)
      Your new balance will be 22 days after approval.
```

---

## 📚 Documentation

### Detailed Guides

- **[Architecture Documentation](docs/ARCHITECTURE.md)**: Deep dive into system design
- **[Database Schema](docs/DATABASE_SCHEMA.md)**: Complete database documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions

### Environment Variables

Create a `.env` file with the following:

```env
# Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hr_db

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

### Available Functions

The AI agent has access to these functions:

| Function | Description | Parameters |
|----------|-------------|------------|
| `get_leave_balance` | Retrieve employee leave balance | None |
| `get_employee_info` | Get employee details | None |
| `get_salary_info` | View salary information | None |
| `get_leave_requests` | List leave request history | None |
| `request_leave` | Submit new leave request | start_date, end_date, reason |

---

## 🧪 Testing

```bash
# Run agent tests
python tests/test_agent.py

# Test database queries
python scripts/test_queries.py

# Test with sample data
python scripts/generate_sample_data.py
python src/bot.py
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Use production-grade PostgreSQL instance
- [ ] Enable SSL for database connections
- [ ] Configure proper logging (not print statements)
- [ ] Set up monitoring (e.g., Sentry, DataDog)
- [ ] Use environment-specific configs
- [ ] Enable database connection pooling
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Use webhook mode instead of polling (for scale)

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write tests for new features
- Update documentation as needed

---

.

---

## 👏 Acknowledgments

- **Google Gemini API** for advanced function calling capabilities
- **Telegram** for their excellent Bot API
- **SQLAlchemy** for the robust ORM framework
- **PostgreSQL** for reliable database management

---



---

<div align="center">

**Yousef hedayah**


</div>
