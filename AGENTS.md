# Project: Vet Reputation AI

## Overview

This project aims to build a SaaS (subscription-based) application for veterinary clinics and individual veterinarians.

The system acts as an AI-powered reputation protection agent that monitors public online content 24/7, detects mentions, evaluates risk, and assists in responding appropriately.

The goal is NOT to generate fake reviews, but to:

- protect reputation,
- detect harmful or false content early,
- support professional and compliant communication,
- increase the number of authentic customer reviews.

---

## Core Product Principles

- Never auto-publish responses to negative or sensitive content.
- Always require human approval for medium/high-risk cases.
- Do not manipulate or bias customer reviews.
- Respect GDPR (RODO) and platform terms of service.
- Monitor only public or legally accessible data sources.
- Store evidence (link, timestamp, source) for each detected mention.
- System must be scalable as a SaaS platform.

---

## Core Features

### 1. Online Monitoring (24/7)

The system monitors mentions related to a clinic or veterinarian based on:

- full name of veterinarian
- clinic name
- address
- phone number
- related names (staff, owner)
- common phrases (e.g. “this vet”, “that clinic”)
- misspellings
- nicknames or slang
- local references (e.g. “vet on [street/city]”)

Keyword database must be:

- editable by user/admin
- dynamically expandable
- versioned if possible

---

### 2. Data Sources (MVP vs Future)

#### MVP:

- mock data
- manually imported mentions
- simple external sources (where legal)

#### Future:

- Google reviews (official APIs if available)
- Facebook public posts/comments (only if compliant)
- forums and public websites
- review platforms (e.g. ZnanyLekarz-like)
- public content from X / TikTok / Instagram (if legally accessible)

IMPORTANT:
Do NOT implement scraping of restricted/private data.

---

### 3. AI Analysis

Each mention should be classified into:

- positive
- neutral
- negative
- harmful
- hate
- defamation risk
- crisis escalation

Each mention must include:

- sentiment
- risk_level: low / medium / high
- short summary
- reasoning (short explanation)
- suggested response draft

Risk interpretation:

- low → informational or positive
- medium → requires response
- high → potential legal/reputation risk

---

### 4. Alerts System

Trigger alerts when:

- new mention detected
- risk level >= medium

Channels:

- email (MVP)
- SMS (future)
- in-app notifications

Example:
“New negative mention detected on Facebook. Risk level: HIGH. Review required.”

---

### 5. Response Suggestions

The system generates response drafts, such as:

- thanking for positive feedback
- calm professional response to negative opinion
- request for private contact
- legal-safe response (no disclosure of medical details)

Rules:

- NEVER auto-send responses
- ALWAYS require approval
- responses must be neutral, professional, compliant

---

### 6. Review Request Module

After each visit:

System sends:

- email (MVP)
- SMS (future)

Message example:
“Thank you for your visit at [clinic]. We would appreciate your feedback: [link]”

Features:

- delay (e.g. 2–6 hours)
- reminder after 24h
- tracking responses
- statistics dashboard

IMPORTANT:

- message must be neutral
- no suggestion of positive rating
- include unsubscribe option

---

### 7. User Dashboard

User must see:

- list of mentions
- source (platform)
- date
- sentiment
- risk level
- response status
- AI response suggestion

Additionally:

- review request history
- number of collected reviews
- average rating

---

### 8. Subscription Model (SaaS)

Plans:

- Basic:
  monitoring + alerts

- Pro:
  monitoring + AI responses + review requests

- Premium:
  full system + analytics + priority alerts

Billing:

- monthly subscription
- modular upgrade capability

---

## Legal & Compliance Requirements

- GDPR (RODO) compliance
- consent management for communication (email/SMS)
- unsubscribe mechanism required
- data minimization principles
- no scraping against platform policies
- no automated defamatory judgments (AI suggests, user decides)

---

## Technical Stack

Backend:

- Python (FastAPI)

Database:

- PostgreSQL

Queue / background jobs:

- Celery or RQ

Frontend:

- React / Next.js

Notifications:

- email (SMTP / provider)
- SMS (future integration)

AI:

- classification
- summarization
- response generation

---

## Development Guidelines

- Start with MVP only
- Use mock data instead of real integrations initially
- Build modular architecture (microservices optional later)
- Avoid overengineering
- Prioritize readability and maintainability
- Log all important actions
- Add basic tests for critical logic

---

## MVP Scope (Phase 1)

- user + clinic account
- keyword management
- manual/mock mentions
- AI classification (mock or real API)
- dashboard (basic)
- response suggestions
- email-based review requests (mock or basic)

---

## Future Expansion

- real-time monitoring integrations
- advanced AI (trend detection, crisis prediction)
- multi-clinic support
- analytics & reporting
- legal support module
- automated workflows
- integrations with booking systems

---

## Complexity Awareness

This is a complex, multi-layer SaaS product involving:

- AI processing
- external data sources
- legal constraints
- real-time monitoring
- notification systems

Development should be incremental.

Do NOT attempt full-scale implementation at once.

Always break tasks into small steps.

---

## Cost & Time Awareness (Guidance for AI)

When proposing features:

- consider implementation complexity
- prefer MVP-first approach
- highlight trade-offs (cost vs functionality)
- avoid unnecessary paid integrations early

---

## Instruction to Codex

When generating code or architecture:

- follow MVP-first approach
- prefer simple working solutions
- clearly separate modules
- document assumptions
- ask before adding external APIs
- never implement illegal or non-compliant data collection

---
