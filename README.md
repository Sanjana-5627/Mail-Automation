# 📧 CrewAI Gmail Automation & Executive Inbox Assistant

An intelligent, safety-first email management assistant designed for freelancers, creators, and professionals drowning in email. Powered by **CrewAI** and **Google Gemini**, this project categorizes incoming communications, prioritizes urgent matters, generates context-aware draft replies, flags unsubscribe candidates, and safely cleans up low-value clutter with built-in human-in-the-loop guardrails.

---

## 🏗️ Architecture

```
[1. IMAP Inbox Fetch (@before_kickoff)]
       │ (Fetch unread emails & calculate age_days)
       ▼
[output/fetched_emails.json]
       │
       ├─────────────────────────────────────────────────────────────────────────┐
       ▼                                                                         ▼
[2. Categorization & Priority Agent]                                 [VIP Sender Learning]
   (Categorizes: NEWSLETTERS, PROMOTIONS, PERSONAL, GITHUB,          (Bumps repeat senders
    YOUTUBE, RECEIPTS_INVOICES, etc.)                                 from MEDIUM → HIGH)
       │
       ▼
[output/categorization_report.json]
       │
       ├───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
       ▼                               ▼                               ▼                               ▼
[3. Organization Agent]      [4. Response Generator Agent]   [5. Notification Agent]     [6. Cleanup Agent]
(Applies Gmail labels        (Generates drafts with style    (Sends urgent alerts        (Archives/deletes low-prio
 & star markers)              matching & Calendar slots)      to Slack)                   clutter & expunges trash)
       │                               │                               │                               │
       └───────────────────────────────┴───────────────┬───────────────┴───────────────────────────────┘
                                                       ▼
                                            [7. Human Approval Guardrail]
                                            (REQUIRE_APPROVAL & DRY_RUN check)
                                                       │
                                                       ▼
                                            [8. Run Digest & Observability]
                                            (Logs to decisions.jsonl & sends summary)
```

---

## ✨ Features & Enhancements

- 📋 **Intelligent Categorization**: Classifies emails into `NEWSLETTERS`, `PROMOTIONS`, `PERSONAL`, `GITHUB`, `YOUTUBE`, `RECEIPTS_INVOICES`, `SPONSORSHIPS`, `RECRUITMENT`, and `EVENT_INVITATIONS`.
- 🔔 **Strict Priority Levels**: Assigns `HIGH`, `MEDIUM`, or `LOW` priority based on content urgency and sender context.
- ⭐ **Gmail Organization**: Automatically stars and applies labels (`URGENT`, `ACTION_NEEDED`, category labels) via IMAP.
- ✍️ **Personalized Response Drafts**: Crafts context-aware reply drafts matching your writing style without modifying your actual Inbox.
- 📅 **Calendar-Aware Scheduling Assist**: Checks Google Calendar availability to suggest free slots in meeting replies.
- 👑 **VIP Sender Learning**: Recognizes frequent contacts and automatically upgrades their priority level.
- 📩 **Unsubscribe Assistant**: Identifies heavy promotional senders with `List-Unsubscribe` headers and compiles candidate suggestions.
- 🛡️ **Human-in-the-Loop Safety**: All destructive operations (delete, archive, trash clear) default to `DRY_RUN=true` and require explicit CLI approval (`REQUIRE_APPROVAL=true`).
- 📊 **Evaluation Harness**: Benchmark classification accuracy against synthetic test datasets.
- 📜 **Decision Logging**: Appends all agent decisions to `logs/decisions.jsonl` with CLI table viewing tool (`scripts/view_log.py`).

---

## 🛡️ Safety & Design Decisions

1. **Dry-Run Default (`DRY_RUN=true`)**: Protects your real inbox by default. All deletion, archiving, and trash emptying tools run in simulated dry-run mode until you explicitly set `DRY_RUN=false` in `.env`.
2. **Human-in-the-Loop Approval (`REQUIRE_APPROVAL=true`)**: Before executing inbox-mutating operations, the CLI pauses and prompts for confirmation.
3. **Suggestion-Only Unsubscribe**: To prevent accidental loss of important newsletters or subscriptions, unsubscribe candidates are collected into digest reports for manual action rather than auto-executing.
4. **IMAP Security**: Uses direct SSL IMAP connections with standard Gmail App Passwords. Your credentials remain stored locally on your machine in `.env` and are never shared.

---

## 🔑 How to Get API Keys (100% Free Option Available)

### Option A: Free Google Gemini API Key (Recommended)
1. Go to [Google AI Studio (aistudio.google.com)](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API Key**.
4. Copy the generated key and set it in your `.env`:
   ```env
   MODEL=gemini/gemini-2.0-flash
   GEMINI_API_KEY=AIzaSy...
   ```

### Option B: Gmail App Password
1. Go to your Google Account settings: [myaccount.google.com](https://myaccount.google.com/).
2. Select **Security** from the left panel.
3. Under "Signing in to Google", enable **2-Step Verification** if not already enabled.
4. Search for or select **App passwords**.
5. Select **Mail** as the app and **Other (Custom name)** as the device (name it `Gmail CrewAI`).
6. Click **Generate** and copy the 16-character password into `.env`:
   ```env
   EMAIL_ADDRESS=your_email@gmail.com
   APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## 🚀 Quick Start

### 1. Installation
```powershell
# Clone repository & enter project folder
cd mail_automation

# Create virtual environment & install dependencies
.venv\Scripts\python.exe -m pip install -e .
```

### 2. Configure Environment
Copy `.env_example` to `.env` and enter your keys:
```powershell
Copy-Item .env_example .env
```

### 3. Run Application
```powershell
.venv\Scripts\python.exe -m gmail_crew_ai.main
```

---

## 📊 Evaluation & Utilities

### Run Categorization Accuracy Benchmark
Test classification rules against 15 synthetic test fixtures:
```powershell
.venv\Scripts\python.exe eval/run_eval.py
```

### View Decision Logs Table
View recent agent classification & action logs in a terminal table:
```powershell
.venv\Scripts\python.exe scripts/view_log.py -n 10
```

---

## 🆕 What's New / Enhancements Over Original

- Added **Configurable LLM Support** (`gemini/gemini-2.0-flash` default).
- Added **Missing `GmailArchiveTool`** for tax & receipt archiving.
- Added **Dry-Run & Human Approval Guardrails**.
- Added **Evaluation Harness** (`eval/fixtures.json` & `eval/run_eval.py`).
- Added **Decision Logger & Viewer** (`logs/decisions.jsonl` & `scripts/view_log.py`).
- Added **VIP Sender Recognition & Override**.
- Added **Unsubscribe Candidate Detection**.
- Added **Google Calendar Availability Assist**.
- Added **Writing Style Analyzer**.
- Added **Per-Run Digest Summary Reports**.
