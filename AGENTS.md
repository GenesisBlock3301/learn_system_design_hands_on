# AGENTS.md

> **Agent Guide for System Design Learning Journey**
>
> This document provides context and guidelines for AI agents working on this hands-on system design learning project.

---

## 📋 Project Overview

This is a **hands-on system design learning repository** focused on mastering scalable system architecture through practical Python implementation. The project follows a 28-week structured learning path (6 phases) combining:

- **Deep theoretical foundation** (System Design fundamentals, distributed systems)
- **Job-market driven skills** (AI Engineering, MLOps, Cloud-native development)
- **Progressive project building** (60+ projects, each building on the previous)

### Learning Philosophy

The project follows a **4-Step Deep Learning Framework**:

1. **Architecture First**: Describe solutions before coding
2. **Bottleneck Search**: Identify scale failure points
3. **Active Refactoring**: Evolve from Naive → Scalable
4. **Failure Injection**: Debug design flaws intentionally

> ⚠️ **Important**: When helping users, prioritize **understanding over copy-paste**. Ask them to explain their approach before providing solutions.

---

## 🏗️ Project Structure

```
learn_system_design_hands_on/
├── README.md                    # Main project overview & navigation
├── ROADMAP.md                   # Job-market driven AI/ML roadmap (24 weeks)
├── MARGE_ROADMAP.md             # Unified system design + AI roadmap (28 weeks)
├── LEARNING_STRATEGY.md         # 4-step deep learning methodology
├── AGENTS.md                    # This file
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Postgres, Redis, RabbitMQ for local dev
│
├── phase-0-foundation/          # Weeks 1-2: Core concepts
│   ├── 01_simple_socket_server.py
│   ├── 02_mutli_request_handle_server.py
│   ├── 03_flask_rest_api.py
│   ├── 04_dns_resolver.py
│   ├── test_*.py
│   └── FOUNDATION_NOTES.md
│
├── phase-1-building-blocks/     # Weeks 3-6: Production software
│   └── 1_load_balancer_test/
│
├── phase-2-data-engineering/    # Weeks 7-10 (to be created)
├── phase-3-mlops/               # Weeks 11-14 (to be created)
├── phase-4-llm-systems/         # Weeks 15-18 (to be created)
├── phase-5-enterprise/          # Weeks 19-22 (to be created)
└── phase-6-specialization/      # Weeks 23-28 (to be created)
```

---

## 🛠️ Tech Stack

### Core Technologies
| Category | Tools |
|----------|-------|
| **Web Frameworks** | FastAPI, Flask, Uvicorn |
| **Databases** | PostgreSQL (asyncpg, SQLAlchemy), MongoDB, SQLite |
| **Caching** | Redis |
| **Message Queues** | RabbitMQ, Celery |
| **Auth** | JWT (python-jose), passlib, authlib |
| **Monitoring** | Prometheus, structlog |
| **Validation** | Pydantic v2 |
| **Networking** | dnspython, httpx, requests |

### Infrastructure (Docker Compose)
- **PostgreSQL**: Port 5432 (user: `learn`, password: `learn`)
- **Redis**: Port 6379
- **RabbitMQ**: Port 5672 (AMQP), 15672 (Management UI)

---

## 🎯 Coding Standards

### Python Style
- Use **Python 3.10+** features (type hints, async/await, walrus operator)
- Follow **PEP 8** with 4-space indentation
- Use **type hints** for function signatures
- Maximum line length: **100 characters**

### Project Conventions
```python
# Prefer async for I/O bound operations
async def fetch_data() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()

# Use Pydantic for data validation
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# Structured logging over print statements
import structlog
logger = structlog.get_logger()
logger.info("processing_request", user_id=user_id, action="create")
```

### Documentation Requirements
- Each module should have a module-level docstring
- Complex functions need docstrings explaining:
  - What it does
  - Arguments and return types
  - Any side effects
- Add comments for non-obvious logic

---

## 🔄 Development Workflow

### When Starting a Session
1. **Check current phase**: Ask which phase the user is working on
2. **Review existing code**: Check what's already implemented in the phase directory
3. **Understand the goal**: What specific concept/project are they building?
4. **Apply the 4-step framework**:
   - Ask user to describe their architecture approach first
   - Guide them through identifying bottlenecks
   - Help refactor from naive to scalable
   - Introduce intentional bugs for debugging practice (when appropriate)

### Testing Strategy
- Use `pytest` for all tests
- Test file naming: `test_<module_name>.py`
- Include both unit and integration tests
- Use `pytest-asyncio` for async test support

### Running Services
```bash
# Start infrastructure services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f <service_name>
```

---

## 📚 Key Reference Materials

When helping users, refer to these files for context:

| File | Purpose |
|------|---------|
| `README.md` | Quick start, progress tracking, core concepts reference |
| `ROADMAP.md` | Job-market focused skill progression |
| `MARGE_ROADMAP.md` | Complete 28-week unified learning path |
| `LEARNING_STRATEGY.md` | How to apply the 4-step deep learning framework |
| `phase-*/FOUNDATION_NOTES.md` | Theory notes for specific phases |

---

## 💡 Agent Guidelines

### Do's ✅
- **Ask before solving**: "How would you approach this problem?"
- **Build incrementally**: Start with the simplest working version
- **Explain trade-offs**: Why this approach vs. alternatives
- **Connect to theory**: Link code to system design concepts
- **Encourage debugging**: Guide users to find their own bugs
- **Use type hints**: Make code self-documenting
- **Follow existing patterns**: Check existing code in the phase directory

### Don'ts ❌
- **Don't dump complete solutions** without user engagement
- **Don't skip the "why"**: Explain reasoning behind design decisions
- **Don't use outdated patterns** (e.g., Flask where FastAPI is more appropriate for new code)
- **Don't ignore the learning strategy**: This is for deep learning, not quick answers
- **Don't modify existing working code** without discussing with user
- **Don't create files directly**: Provide steps, approaches, and guidance. Let the user write the code and debug. Offer thoughts, suggestions, and review their work instead of generating files for them

### Phase-Specific Guidance

| Phase | Focus | Key Concepts |
|-------|-------|--------------|
| 0 | Foundation | HTTP, TCP/UDP, DNS, sockets, latency vs bandwidth |
| 1 | Building Blocks | Load balancing, caching, databases, horizontal scaling |
| 2 | Data Engineering | Kafka, Airflow, ETL, feature stores |
| 3 | MLOps | Model serving, experiment tracking, monitoring |
| 4 | LLM Systems | RAG, vector DBs, agents, prompt engineering |
| 5 | Enterprise | Multi-cloud, security, global deployment |
| 6 | Specialization | Deep expertise in chosen track |

---

## 🚀 Quick Commands

```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Run tests
pytest -v

# Run specific test file
pytest test_flask_api.py -v

# Check running services
docker-compose ps
```

---

## 🔗 External Resources

### Books
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "System Design Interview" - Alex Xu
- "Clean Architecture" - Robert C. Martin

### Online
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [High Scalability](http://highscalability.com/)
- [Martin Fowler's Blog](https://martinfowler.com/)

---

## 📝 Notes for Agents

- This is a **learning journey**, not a production codebase
- Prioritize **conceptual understanding** over code perfection
- The user is building this incrementally over 28 weeks
- Current progress: **Phase 0 (Foundation)** - just starting
- When in doubt, ask the user what they're trying to learn from this exercise

---

**Remember**: The goal is to help the user become a skilled system designer, not just someone who can copy code. Guide them through the thinking process!
