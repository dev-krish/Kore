# KORE
### Autonomous AI-Powered Professional Outreach Platform
*Find the right people. Build meaningful connections.*

---

## 1. Executive Summary

**KORE** is an autonomous AI-powered professional outreach platform engineered primarily for university and college students seeking:
- Software Engineering & Founding Internships
- AI/ML & Research Opportunities
- Mentorship & Open-Source Collaborations

Traditional student outreach is cumbersome, prone to spam, and involves tedious manual company research, finding leadership contacts, guessing emails, and drafting generic messages.

**KORE transforms a student's technical career profile and natural-language objective into a structured, researched, personalized, and strictly human-approved outreach campaign.**

Unlike generic AI wrappers or uncontrolled spam bots, KORE executes a genuine tool-using agent with a controlled **Observe-Decide-Act-Verify** loop, complete source attribution, atomic delivery safety, and a **zero-bypass cryptographic Human Approval Gate**.

---

## 2. Core Architecture

```
                                  USER CAREER PROFILE
                                          |
                                          v
                              NATURAL LANGUAGE OBJECTIVE
                                          |
                                          v
                                    AGENT PLANNER
                             (Structured Execution Plan)
                                          |
                                          v
                                  AGENT CONTROLLER
                        (Observe-Decide-Act-Verify Loop)
                                          |
             +----------------------------+----------------------------+
             |                            |                            |
             v                            v                            v
     [company_search]              [fetch_website]            [discover_contacts]
 (Curated & Live Discovery)     (DOM-based Extraction)     (Verified Leadership Roles)
             |                            |                            |
             +----------------------------+----------------------------+
                                          |
                                          v
                                 [research_company]
                     (Technical Focus & Engineering Analysis)
                                          |
                                          v
                                [evaluate_relevance]
                     (Profile Alignment & Contribution Fit)
                                          |
                                          v
                                  [generate_email]
                     (Concise, Tailored Cold Email Draft)
                                          |
                                          v
                       +--------------------------------------+
                       |      HUMAN APPROVAL GATE (MANDATORY) |
                       | - Cryptographic SHA-256 Hash Bound   |
                       | - Any Content Edit Invalidates Hash  |
                       | - Rejection & Archive Controls       |
                       +--------------------------------------+
                                          |
                                 [Explicit Approval]
                                          |
                                          v
                                     [send_email]
                       (Atomic Compare-and-Swap State Lock)
                       (Gmail OAuth 2.0 / User Token Scoped)
                                          |
                                          v
                            CAMPAIGN DELIVERY AUDIT LOG
```

---

## 3. Technology Stack

### Frontend
- **Framework:** Next.js 14 (App Router, Server & Client Components)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS with custom dark SaaS theme
- **Icons:** Lucide React
- **State Management:** Redux Toolkit
- **HTTP Client:** Axios (fully typed with typed API layer)
- **Design System:** Deep navy/charcoal surfaces (`#080c14`, `#0f172a`), subtle glow accents, responsive typography

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Data Validation:** Pydantic V2 & Pydantic Settings
- **Database Driver:** Motor (Async MongoDB driver)
- **HTTP Engine:** HTTPX (async client with retry and timeout policies)
- **Real-Time Streaming:** Server-Sent Events (SSE) for live agent execution timeline
- **Browser Automation:** Playwright Chromium with robust DOM-based BeautifulSoup4 fallback
- **Security:** Native `bcrypt` password hashing, Python-Jose (JWT), SHA-256 content hashing

### AI & LLM Engine
- **Local Inference:** Ollama running `qwen3:4b`
- **Provider Abstraction:** `BaseLLMProvider` interface with pluggable Ollama, OpenAI-compatible, and deterministic Mock providers
- **Reasoning Controls:** Structured Pydantic JSON schemas, `num_predict` bounds for snappy CPU execution

### Database
- **Engine:** MongoDB 7.0
- **Collections:** `users`, `profiles`, `campaigns`, `companies`, `contacts`, `research`, `emailDrafts`, `emailDeliveries`, `agentExecutions`, `oauthStates`, `integrationCredentials`
- **Isolation:** Strict user ownership verification across all endpoints

---

## 4. Agent Tools Implementation

KORE implements 7 modular agent tools inside `backend/app/engine/tools/`:

| Tool | Purpose | Source Attribution |
|---|---|---|
| `company_search` | Discovers startups matching industry, location, keywords | Public domain registrations & verified databases |
| `fetch_website` | Extracts clean textual content and meta tags from public websites | Target Website URL |
| `discover_contacts` | Identifies founders, CTOs, and technical hiring leadership | Leadership pages & verified disclosures |
| `research_company` | Investigates engineering priorities, stack, and internship alignment | Public website content & engineering blogs |
| `evaluate_relevance` | Evaluates student profile fit, skill overlap, and outreach angle | Objective Profile & Alignment Matrix |
| `generate_email` | Synthesizes concise (<170 words), tailored cold email drafts | Personalization Engine with evidence provenance |
| `send_email` | Gated email dispatcher checking Gmail OAuth & SHA-256 approval | Gmail API delivery logs |

---

## 5. Security & Human-in-the-Loop Approval Gate

KORE enforces strict safeguards against automated spam and unauthorized operations:

1. **Zero LLM Autonomy for Sending:** The LLM agent **cannot** call `send_email` autonomously. It can only generate drafts with status `generated`.
2. **Cryptographic Content Hashing:** When the user clicks **Approve Draft**, the backend computes:
   $$\text{Hash} = \text{SHA256}(\text{recipient} \parallel \text{subject} \parallel \text{body})$$
   and saves `approvedContentHash`.
3. **Anti-Tampering Invalidation:** If the user edits the draft subject or body after approval, the approval status is instantly invalidated (`pending_review`, hash cleared) and a fresh approval is required.
4. **Atomic Conditional State Transition (Compare-And-Swap):** Sending utilizes MongoDB's `find_one_and_update` on status `APPROVED` and matching hash. Concurrent duplicate requests are immediately blocked (HTTP 409 Conflict), guaranteeing zero duplicate sends.
5. **Cross-User Data Isolation:** Every campaign, company, contact, and draft is scoped to the authenticated user ID. Cross-user attempts receive HTTP 404 or 403.
6. **Strict Authentication & Scoped OAuth:** Passwords are encrypted with native `bcrypt` (minimum 8 characters). Bearer JWTs verify user existence in the database. Google OAuth utilizes cryptographic CSRF state parameters consumed atomically upon callback.

---

## 6. Quickstart & Local Setup

### Prerequisites
- Linux OS (or WSL2 / macOS)
- Node.js 18+ and npm
- Python 3.12+
- Docker & Docker Compose
- (Optional for live local LLM) Ollama with `qwen3:4b`

### 1. Clone & Configure Environment
```bash
cd /home/krish/Desktop/kore
cp .env.example .env
```

### 2. Start MongoDB
```bash
docker run -d --name kore-mongodb -p 27017:27017 -v kore-mongo-data:/data/db mongo:7.0
```

### 3. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API available at: `http://localhost:8000`*  
*Swagger Documentation: `http://localhost:8000/docs`*

### 4. Start Frontend
```bash
cd frontend
npm run dev
```
*Frontend Application available at: `http://localhost:3000`*

### 5. Or Run via Docker Compose
```bash
docker-compose up --build
```

---

## 7. Verification & Automated Test Suite

KORE includes an automated test suite verifying unit tool operations, security hardening, user isolation, and end-to-end workflows:

```bash
cd backend
source venv/bin/activate
LLM_PROVIDER=mock pytest tests/ -v
```

### Complete Test Suite Results (24 Passed, 0 Failed):

- `tests/test_api.py::test_root_and_health`: PASSED
- `tests/test_api.py::test_profile_api`: PASSED
- `tests/test_api.py::test_campaign_api`: PASSED
- `tests/test_api.py::test_integrations_status_api`: PASSED
- `tests/test_approval_gate.py::test_approval_gate_blocks_unapproved_draft`: PASSED
- `tests/test_approval_gate.py::test_approval_gate_verifies_valid_hash`: PASSED
- `tests/test_approval_gate.py::test_approval_gate_blocks_modified_content_tampering`: PASSED
- `tests/test_campaign_flow.py::test_agent_controller_end_to_end_execution`: PASSED
- `tests/test_live_workflow.py::test_full_user_journey_end_to_end`: PASSED
- `tests/test_planner.py::test_agent_planner_creates_structured_plan`: PASSED
- `tests/test_security_hardened.py::test_registration_validation`: PASSED
- `tests/test_security_hardened.py::test_login_password_verification`: PASSED
- `tests/test_security_hardened.py::test_token_enforcement_and_validation`: PASSED
- `tests/test_security_hardened.py::test_cross_user_isolation`: PASSED
- `tests/test_security_hardened.py::test_gmail_oauth_lifecycle_and_csrf`: PASSED
- `tests/test_security_hardened.py::test_approval_hash_invalidation_on_edit`: PASSED
- `tests/test_security_hardened.py::test_concurrent_duplicate_send_atomic_cas`: PASSED
- `tests/test_security_hardened.py::test_missing_gmail_tokens_in_live_mode`: PASSED
- `tests/test_security_hardened.py::test_demo_session_disabled_in_production`: PASSED
- `tests/test_tools.py::test_company_search_tool`: PASSED
- `tests/test_tools.py::test_fetch_website_tool`: PASSED
- `tests/test_tools.py::test_discover_contacts_tool`: PASSED
- `tests/test_tools.py::test_evaluate_relevance_tool`: PASSED
- `tests/test_tools.py::test_generate_email_tool`: PASSED

---

## 8. Definition of Done Checklist

- [x] **Student Profile:** Create, view, update personal background, technical skills, projects, and target preferences.
- [x] **Campaign Manager:** Natural-language campaign creation with industry, location, and role targeting.
- [x] **Agent Planning:** Multi-step structured execution plan generated by the planning agent.
- [x] **Company Discovery:** Curated and live company discovery with verified public domains and descriptions.
- [x] **Website Research:** Textual extraction via Playwright / async HTTP client.
- [x] **Contact Identification:** Verified founders and technical leaders with confidence score and source provenance.
- [x] **Relevance Fit Evaluation:** Algorithmic and LLM-based profile matching with rationale and angle suggestions.
- [x] **Personalized Drafts:** Draft generation referencing verified facts without hallucinations.
- [x] **Human Review & Editor:** Real-time subject and body editing with auto-invalidation safeguards.
- [x] **Human Approval Gate:** SHA-256 cryptographic authorization.
- [x] **Atomic Delivery Guard:** Concurrency-safe CAS locking preventing duplicate email sends.
- [x] **Gmail Dispatch:** Gmail OAuth 2.0 integration with transparent demo delivery simulation fallback.
- [x] **Execution Observability:** Live SSE event stream, step history, and tool invocation inspector.
