# 🚀 System Design Learning Journey

> **Your Complete Reference Guide for Mastering System Design with Python**

This repository is your comprehensive learning companion for mastering system design concepts through practical Python implementation. Each phase builds upon the previous, creating a solid foundation for understanding scalable systems.

## 📋 Quick Navigation

- [📚 Learning Phases](#-learning-phases)
- [🧠 Learning Strategy](#-learning-strategy)
- [🎯 Current Focus](#-current-focus)
- [📊 Progress Tracking](#-progress-tracking)
- [🛠️ Tech Stack](#️-tech-stack)
- [📖 Core Concepts Reference](#-core-concepts-reference)
- [🏃‍♂️ Quick Start](#️-quick-start)
- [📅 Daily Learning Routine](#-daily-learning-routine)

## 📚 Learning Phases

---

## 🧠 Learning Strategy

To ensure deep learning and avoid becoming a "copy-paste engineer", we follow a strict **4-Step Deep Learning Framework**:

1.  **Architecture First**: Always describe the solution before coding.
2.  **Bottleneck Search**: Identify where the system fails at scale.
3.  **Active Refactoring**: Evolve from a "Naive" to a "Scalable" version.
4.  **Failure Injection**: Intentionally debug design flaws to build muscle memory.

Detailed strategy can be found in [LEARNING_STRATEGY.md](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/LEARNING_STRATEGY.md).

---

### 🎬 **PHASE 0 – Foundation (Weeks 1-2)**
**Foundation concepts before diving into system design**

**📖 Theory Topics:**
- What "designing a system" actually means
- Functional vs Non-functional requirements  
- Client → Server model
- What happens when you type a URL
- IP, DNS, HTTP/HTTPS
- Latency vs Bandwidth
- TCP vs UDP

**💻 Python Projects:**
- Simple HTTP Server using `http.server`
- Basic REST API with Flask
- DNS Resolver Tool using `socket`
- Network Latency Measurement Tool

### 🧱 **PHASE 1 – Core Building Blocks (Weeks 3-6)**
**Essential components of scalable systems**

**📖 Theory Topics:**
- Vertical vs Horizontal scaling
- Load balancers (L4 vs L7, Round robin, least connections)
- SQL vs NoSQL databases
- Database scaling (replication, sharding)
- CAP theorem
- Caching fundamentals and Redis

**💻 Python Projects:**
- Multi-server Fast Application
- Simple Load Balancer
- SQL vs NoSQL Comparison Tool
- Database Sharding Simulator
- Redis Cache Implementation with LRU

### ⚡ **PHASE 2 – Performance & Reliability (Weeks 7-10)**
**Performance optimization and system reliability**

**📖 Theory Topics:**
- CDNs and static content delivery
- Asynchronous processing (sync vs async)
- Message queues (Kafka/RabbitMQ)
- Rate limiting (token bucket, leaky bucket)
- Fault tolerance and high availability
- Data consistency (strong vs eventual)

**💻 Python Projects:**
- Local CDN Simulator
- Async Task Queue System with `asyncio`
- Rate Limiting Middleware
- Circuit Breaker Pattern
- Consistency Simulator

### 🔐 **PHASE 3 – Real-World Concerns (Weeks 11-13)**
**Production system requirements**

**📖 Theory Topics:**
- Authentication (Sessions vs JWT)
- OAuth basics
- Role-based access control
- Logging, monitoring, and alerts
- Security basics (HTTPS, firewalls, DDoS)
- Input validation

**💻 Python Projects:**
- JWT Authentication System
- OAuth Integration with Google/GitHub
- Logging and Metrics Dashboard
- Security Scanner Tool
- HTTPS Server Setup

### 🧠 **PHASE 4 – Design Patterns (Weeks 14-15)**
**Architectural patterns for scalable systems**

**📖 Theory Topics:**
- Microservices vs Monolith
- API Gateway pattern
- Event-driven architecture
- Producers & consumers
- Loose coupling

**💻 Python Projects:**
- Monolith to Microservices Migration
- API Gateway Implementation
- Event-Driven System with `pydispatch`
- Service Discovery Tool

### 🏗️ **PHASE 5 – System Design Case Studies (Weeks 16-21)**
**Real-world system implementations**

**📖 Case Studies:**
- **URL Shortener (like Bitly)**: Hashing, database schema, read optimization
- **Instagram Clone**: Image upload, CDN, metadata storage
- **WhatsApp Clone**: Real-time messaging, WebSockets, message queues
- **YouTube Clone**: Video pipeline, transcoding, CDN delivery
- **Twitter Clone**: Feed system, fanout strategies, caching
- **Uber Clone**: Location tracking, matching algorithms

**💻 Each Project Includes:**
- Problem statement and requirements
- High-level design diagram
- Component deep-dive
- Performance optimization
- Trade-off analysis

### 🚀 **PHASE 6 – Advanced (Weeks 22-24)**
**Distributed systems concepts**

**📖 Theory Topics:**
- Distributed transactions (two-phase commit)
- Consistent hashing for sharding & caching
- Leader election (Raft/Paxos intuition)

**💻 Python Projects:**
- Distributed Transaction Coordinator
- Consistent Hashing Ring
- Leader Election Algorithm
- Distributed Lock Manager

## 🎯 Current Focus

**📍 You are here:** Phase 0 - Foundation

**🎯 This Week's Goal:** Build your first HTTP server and understand web architecture basics

**📅 Next Milestone:** Complete Phase 0 projects and move to Phase 1

## 📊 Progress Tracking

### Overall Progress
- [ ] **Phase 0: Foundation** (0/4 projects)
- [ ] **Phase 1: Core Building Blocks** (0/5 projects)
- [ ] **Phase 2: Performance & Reliability** (0/5 projects)
- [ ] **Phase 3: Real-World Concerns** (0/5 projects)
- [ ] **Phase 4: Design Patterns** (0/4 projects)
- [ ] **Phase 5: Case Studies** (0/6 projects)
- [ ] **Phase 6: Advanced** (0/5 projects)

**Total Projects Completed:** 0/34

### This Week's Tasks
- [ ] Read system design fundamentals
- [ ] Build simple HTTP server
- [ ] Create basic REST API
- [ ] Implement DNS resolver
- [ ] Document learnings

## 🛠️ Tech Stack

### Core Technologies
```python
# Web Frameworks
flask==2.3.3
fastapi==0.103.1
uvicorn==0.23.2

# HTTP & Networking
requests==2.31.0
aiohttp==3.8.5

# Databases
sqlite3  # Built-in
pymongo==4.5.0
psycopg2-binary==2.9.7

# Caching
redis==4.6.0

# Message Queues
pika==1.3.2  # RabbitMQ

# Async Programming
asyncio  # Built-in

# Authentication & Security
pyjwt==2.8.0
cryptography==41.0.4

# Testing
pytest==7.4.2
locust==2.16.1  # Load testing

# Monitoring
prometheus-client==0.17.1

# Event-Driven
pydispatch==1.0.0
python-socketio==5.8.0
```

## 📖 Core Concepts Reference

### System Design Fundamentals
- **Functional Requirements**: What the system should do
- **Non-Functional Requirements**: How well the system should perform (scalability, reliability, etc.)
- **Scalability**: Ability to handle increased load
- **Reliability**: Probability system works correctly over time
- **Availability**: Percentage of time system is operational

### Web Architecture
- **Client-Server Model**: Request-response pattern
- **REST APIs**: Stateless communication using HTTP methods
- **DNS**: Domain Name System for URL resolution
- **HTTP vs HTTPS**: Plain text vs encrypted communication

### Performance Metrics
- **Latency**: Time to complete a request
- **Throughput**: Requests processed per second
- **Bandwidth**: Data transfer capacity
- **Response Time**: Total time for request-response cycle

## 🏃‍♂️ Quick Start

### 1. Setup Environment
```bash
# Clone and navigate to project
cd /Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/system-design-journey

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Choose Your Phase
```bash
# Start with Phase 0 (Foundation)
cd phase-0-foundation

# Follow the README in each phase directory
# Each phase has specific projects and learning objectives
```

### 3. Daily Learning Routine
1. **📖 Morning (30 min)**: Read theory topics
2. **💻 Afternoon (2 hours)**: Code implementation
3. **📝 Evening (30 min)**: Document learnings and update progress

## 📅 Daily Learning Routine

### 🌅 Morning Session (30 minutes)
- [ ] Read assigned theory topics
- [ ] Take notes on key concepts
- [ ] Watch related videos/tutorials
- [ ] Review previous day's code

### 🌞 Afternoon Session (2 hours)
- [ ] Implement the day's project
- [ ] Test your implementation
- [ ] Debug and optimize code
- [ ] Add comments and documentation

### 🌙 Evening Session (30 minutes)
- [ ] Update progress in this README
- [ ] Commit code to GitHub
- [ ] Write learning summary
- [ ] Plan next day's tasks

## 🎯 Success Metrics

### Knowledge Goals
- [ ] Understand 28+ core system design concepts
- [ ] Master 34+ practical implementations
- [ ] Build portfolio of working systems
- [ ] Deploy 5+ projects to cloud platforms

### Technical Goals
- [ ] Write 1000+ lines of Python code
- [ ] Implement 10+ design patterns
- [ ] Create 5+ production-ready systems
- [ ] Master async programming concepts

### Career Goals
- [ ] Build impressive portfolio projects
- [ ] Gain confidence in system design interviews
- [ ] Understand enterprise architecture patterns
- [ ] Become proficient in distributed systems

## 📚 Additional Resources

### 📖 Books
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu
- "Clean Architecture" by Robert C. Martin

### 🎥 Videos
- System Design Primer on YouTube
- Gaurav Sen's System Design Tutorials
- Tech Dummies for System Design

### 🌐 Websites
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [High Scalability](http://highscalability.com/)
- [Martin Fowler's Blog](https://martinfowler.com/)

## 🤝 Contributing

This is your personal learning journey, but feel free to:
- Add new project ideas
- Improve existing implementations
- Share your learning experience
- Document additional resources

## 📞 Need Help?

**Common Issues:**
- Check Python version (3.8+ required)
- Verify virtual environment is activated
- Ensure all dependencies are installed
- Check port availability for web servers

**Learning Support:**
- Review theory before coding
- Start with simple implementations
- Test frequently as you build
- Document your thought process

---

**🎯 Remember**: This is a marathon, not a sprint. Focus on understanding concepts deeply rather than rushing through phases. Each project you complete builds your expertise and confidence in system design.

**📅 Start Date**: ________________
**🎯 Target Completion**: ________________

**Happy Learning! 🚀**