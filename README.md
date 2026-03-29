<p align="center">
  <img src="https://raw.githubusercontent.com/zixi-liu/openpriors/main/assets/logo.png" alt="OpenPriors" width="120" />
</p>

<h1 align="center">OpenPriors</h1>

<p align="center">
  <strong>Your personal AI assistant that turns what you learn into what you do.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#features">Features</a> &middot;
  <a href="#agent-system">Agents</a> &middot;
  <a href="#architecture">Architecture</a> &middot;
  <a href="#api">API</a>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT" /></a>
</p>

---

Most people forget 90% of what they read within a week. OpenPriors helps you **capture**, **process**, and **integrate** knowledge from books, podcasts, articles, and conversations into your actual daily life — so learning sticks.

Built for intellectuals, lifelong learners, and knowledge workers who consume endlessly but struggle to apply what they learn.

## The Problem

You read a great book. You highlight passages. You feel inspired. Two weeks later, you can't remember the key ideas — let alone practice them.

OpenPriors closes the gap between **knowing** and **doing**.

## How It Works

```
1. Capture    →  Upload a book, paste a URL, or talk about what you learned
2. Extract    →  AI distills actionable principles from your material
3. Synthesize →  AI agents help you connect learnings to your real life
4. Practice   →  Goals with due dates, Slack reminders, and check-ins
```

## Features

| | Feature | Description |
|---|---|---|
| **Capture** | Multi-source input | Upload PDFs, paste YouTube/article links, or voice-record what you learned |
| | Socratic voice Q&A | AI asks follow-up questions to deepen your understanding |
| **Process** | AI extraction | Automatically extracts actionable principles from any source |
| | Semantic search | Hybrid BM25 + vector search across all your materials |
| | LLM formatting | Raw content auto-formatted into structured markdown |
| **Integrate** | Osmosis sessions | AI explores your knowledge and proposes ways to integrate it |
| | Specialized agents | Reflection, Planner, Coach, Writer, and Helper agents |
| | Practice plans | Interactive plans with date pickers and goal tracking |
| **Connect** | Slack integration | Goal reminders and check-ins via Slack |
| **Own** | Local-first | SQLite database — your data stays on your machine |
| | BYOK | Bring your own API key (Gemini, OpenAI, Anthropic) |
| | Themeable UI | Customize background, fonts, and colors |

## Quick Start

**Requirements:** Python 3.10+, Node.js 20+

```bash
# Clone
git clone https://github.com/zixi-liu/openpriors.git
cd openpriors

# Setup — pick your LLM provider and paste your API key
python setup.py

# Install frontend
cd frontend && npm install && cd ..

# Start
python app.py
cd frontend && npm run dev
```

Open the URL shown in your terminal and start learning.

## Agent System

OpenPriors uses a multi-agent architecture. An **Explore agent** reasons about your knowledge and routes to specialized sub-agents:

| Agent | Role | How it works |
|-------|------|-------------|
| **Explore** | Router + knowledge search | Searches your materials, finds connections, proposes integration options |
| **Reflection** | Socratic coach | Walks you through 3-4 probing questions, generates a written reflection |
| **Planner** | Practice designer | Creates goal-based plans with cadence and due dates, saved to DB |
| **Coach** | Roleplay partner | Sets up scenarios to practice applying what you learned |
| **Writer** | Essay guide | Collaborative writing to articulate your learning |
| **Helper** | Free-form | Listens to what you need, searches your knowledge, helps directly |

## Architecture

```
openpriors/
├── app.py                    # FastAPI entry point
├── setup.py                  # CLI setup (BYOK, Slack)
├── core/
│   ├── agent.py              # Explore agent (router + tools)
│   ├── agents/               # Specialized sub-agents
│   │   ├── reflection.py     # Socratic reflection
│   │   ├── planner.py        # Practice plan + goals
│   │   ├── coach.py          # Roleplay practice
│   │   ├── writer.py         # Guided essay writing
│   │   └── helper.py         # Free-form helper
│   ├── embeddings.py         # Chunking, embedding, hybrid search
│   ├── extractor.py          # Prior extraction from sources
│   ├── storage.py            # SQLite (materials, priors, goals, sessions)
│   ├── llm.py                # LLM abstraction (litellm)
│   └── config.py             # Local config (~/.openpriors/)
├── routes/
│   ├── assets.py             # Upload, voice Q&A, materials, search
│   ├── osmosis.py            # Sessions, chat, goals
│   └── setup.py              # BYOK configuration
├── frontend/                 # React + TypeScript + Vite + Tailwind
│   └── src/
│       ├── components/       # Sidebar, ChatPanel, PlanCard, PriorCard
│       └── pages/            # CapturePage, PriorsPage, SettingsPage
└── slack_bot/                # Slack integration for reminders
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/assets/upload/text` | Upload text content |
| `POST` | `/api/assets/upload/url` | Extract from URL (YouTube, articles, books) |
| `POST` | `/api/assets/upload/pdf` | Upload PDF |
| `POST` | `/api/assets/voice/next-question` | Voice Q&A flow |
| `POST` | `/api/assets/voice/generate` | Finalize voice Q&A into learnings |
| `POST` | `/api/assets/search/semantic` | Hybrid BM25 + vector search |
| `GET` | `/api/assets/materials` | List all materials |
| `POST` | `/api/osmosis/sessions` | Create session |
| `POST` | `/api/osmosis/chat` | Chat with agents |
| `GET` | `/api/osmosis/sessions` | List sessions |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, SQLite |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS |
| **LLM routing** | litellm (multi-provider) |
| **Agents** | o3-mini (reasoning), GPT-4o-mini (fast Q&A), Gemini 2.5 Flash (extraction) |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Search** | Hybrid BM25 (FTS5) + vector cosine similarity |

## Configuration

All config lives at `~/.openpriors/config.json` — never in the repo.

```bash
# Reconfigure anytime
python setup.py
```

## License

[MIT](LICENSE)
