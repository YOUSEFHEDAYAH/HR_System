# System Architecture

## Overview

HR uses a modern **agent-based architecture** where an AI agent autonomously handles all business logic through function calling, eliminating the need for traditional intent classification and hardcoded rules.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                           │
│                   (Telegram Mobile/Desktop)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Natural Language Messages
                       │ (Arabic/English)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Bot Layer (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Responsibilities:                                     │  │
│  │ • Telegram API handling                              │  │
│  │ • Employee authentication (ID ↔ Chat ID)            │  │
│  │ • Session management                                  │  │
│  │ • Agent caching                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Delegate to Agent
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Layer (Gemini AI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Autonomous Decision Making:                          │  │
│  │                                                       │  │
│  │ 1. Understand Request → NLP Processing               │  │
│  │ 2. Select Functions → Autonomous Decision            │  │
│  │ 3. Execute Functions → Call with Parameters          │  │
│  │ 4. Process Results → Intelligent Synthesis           │  │
│  │ 5. Generate Response → Natural Language              │  │
│  │                                                       │  │
│  │ Available Functions:                                 │  │
│  │ • get_leave_balance()                                │  │
│  │ • get_employee_info()                                │  │
│  │ • get_salary_info()                                  │  │
│  │ • get_leave_requests()                               │  │
│  │ • request_leave(start, end, reason)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Database Queries
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Query Layer (SQLAlchemy ORM)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ HRQueries Class:                                     │  │
│  │ • Employee operations                                │  │
│  │ • Leave management                                   │  │
│  │ • Salary queries                                     │  │
│  │ • Department operations                              │  │
│  │ • Statistics & reporting                             │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ SQL Queries
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Database Layer (PostgreSQL)                        │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐  │
│  │ employees    │ departments  │ leave_       │ salaries│  │
│  │              │              │ requests     │         │  │
│  └──────────────┴──────────────┴──────────────┴─────────┘  │
│  ┌──────────────┬──────────────────────────────────────┐   │
│  │ leave_       │ employee_chat_links                  │   │
│  │ balances     │                                      │   │
│  └──────────────┴──────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Architectural Patterns

### 1. Agent-Based Design

**Traditional Approach (What we DON'T do):**
```python
# ❌ Hardcoded intent matching
if "balance" in message or "رصيد" in message:
    return get_balance()
elif "salary" in message or "راتب" in message:
    return get_salary()
elif "leave" in message and "request" in message:
    return request_leave()
```

**Our Approach (What we DO):**
```python
# ✅ Agent autonomously decides
response = agent.handle_message(user_message)
# Agent internally:
# - Understands intent
# - Selects appropriate function(s)
# - Executes with validation
# - Generates natural response
```

### 2. Function Calling Architecture

The agent has access to predefined functions but decides:
- **Which** functions to call
- **When** to call them
- **What** parameters to use
- **How** to combine results

This is powered by **Gemini's native function calling** capability.

### 3. Separation of Concerns

```
┌─────────────────────────────────────────┐
│ Bot Layer (bot.py)                      │
│ • Telegram API                          │
│ • Authentication                        │
│ • NO business logic                     │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Agent Layer (agent.py)                  │
│ • Request understanding                 │
│ • Function selection                    │
│ • Validation logic                      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Query Layer (queries.py)                │
│ • Database operations                   │
│ • Transaction management                │
│ • Data aggregation                      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Model Layer (models.py)                 │
│ • Table definitions                     │
│ • Relationships                         │
│ • Business rules                        │
└─────────────────────────────────────────┘
```

## Data Flow Examples

### Example 1: Simple Query

**User:** "What's my leave balance?"

```
1. Bot receives message
2. Bot authenticates user (Telegram ID → Employee)
3. Bot delegates to Agent
4. Agent understands intent: "Check leave balance"
5. Agent calls: get_leave_balance()
6. Query layer executes: SELECT * FROM leave_balances WHERE employee_id = ?
7. Agent receives: {total: 30, used: 5, remaining: 25}
8. Agent generates: "You have 25 days remaining out of 30 total days"
9. Bot sends response to Telegram
```

### Example 2: Complex Operation

**User:** "بدي أطلب إجازة من 15 فبراير لـ 20 فبراير"

```
1. Bot receives Arabic message
2. Bot authenticates user
3. Bot delegates to Agent
4. Agent understands:
   - Intent: Request leave
   - Start: 2026-02-15
   - End: 2026-02-20
5. Agent calls: request_leave(start_date="2026-02-15", end_date="2026-02-20", reason="Personal")
6. Agent function validates:
   - Dates are valid
   - Start < End
   - Not in past
   - Sufficient balance
   - Not exceeding pending request limit
7. Query layer creates leave request
8. Agent receives: {success: true, duration: 6 days}
9. Agent generates Arabic response: "تم تقديم طلب الإجازة بنجاح..."
10. Bot sends response
```

## Scalability Considerations

### Current Architecture (Single Instance)
- ✅ Good for: Small to medium teams (< 1000 employees)
- ✅ Simple deployment
- ✅ Easy debugging

### Production Scaling Options

1. **Database Connection Pooling**
   ```python
   engine = create_engine(url, pool_size=20, max_overflow=40)
   ```

2. **Agent Caching Strategy**
   - Currently: In-memory per-process
   - Scale: Redis for distributed caching

3. **Webhook Mode**
   - Currently: Polling
   - Scale: Webhooks for better performance

4. **Load Balancing**
   - Multiple bot instances
   - Session affinity by employee_id

## Security Architecture

### Authentication Flow

```
1. User sends Employee ID
2. Bot queries database: get_employee_by_id(id)
3. If exists: create link (employee_id ↔ telegram_chat_id)
4. Store in employee_chat_links table
5. Future messages: authenticate via telegram_chat_id
```

### Access Control

- **Employee**: Can only access own data
- **Manager**: Can access department data
- **HR**: Can access all data

Implemented in `Employee.can_access_employee_data()`.

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Telegram | User interface |
| Bot Framework | pyTelegramBotAPI | Telegram integration |
| AI Engine | Google Gemini 2.5 Flash | Natural language understanding |
| Application | Python 3.9+ | Business logic |
| ORM | SQLAlchemy 2.x | Database abstraction |
| Database | PostgreSQL 13+ | Data persistence |
| Config | python-dotenv | Environment management |

## Design Principles

1. **Single Responsibility**: Each layer has one clear purpose
2. **Dependency Injection**: Components receive dependencies
3. **Open/Closed**: Easy to add new functions without modifying core
4. **DRY**: Query logic centralized in HRQueries
5. **Type Safety**: Using Enums for status values

## Future Enhancements

### Short-term
- [ ] Add logging framework (structlog)
- [ ] Add metrics collection (Prometheus)
- [ ] Add unit tests (pytest)
- [ ] Add database migrations (Alembic)

### Long-term
- [ ] Multi-language model switching
- [ ] Voice message support
- [ ] Document processing (upload leave certificates)
- [ ] Manager approval workflow
- [ ] Calendar integration
- [ ] Notification system

## Comparison: Traditional vs Agent-Based

| Aspect | Traditional Chatbot | HR (Agent-Based) |
|--------|-------------------|---------------------|
| Intent Recognition | Regex/NLP classifier | Gemini understanding |
| Business Logic | Hardcoded if/else | Function calling |
| Adding Features | Modify intent handler | Add function definition |
| Conversation Flow | State machine | Autonomous agent |
| Context Handling | Session variables | LLM context |
| Multilingual | Separate training | Native understanding |
| Maintenance | High (update rules) | Low (add functions) |

## Code Organization Philosophy

```
• Simple over clever
• Explicit over implicit  
• Documentation over tricks
• Production-ready over quick-fix
```

Every file has:
- Clear docstring
- Single responsibility
- Minimal dependencies
- Error handling
