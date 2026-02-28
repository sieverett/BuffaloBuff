# BuffaloBuff

Telegram chatbot with RAG for Buffalo Bike maintenance using Anthropic Claude and ChromaDB.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude-191919?style=for-the-badge&logo=anthropic&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

---

## About

BuffaloBuff is a Telegram bot that provides mechanical support for [World Bicycle Relief](https://worldbicyclerelief.org/)'s Buffalo Bikes. It uses retrieval-augmented generation (RAG) to answer maintenance questions grounded in the official Buffalo Bikes Maintenance Manual. The bot uses Anthropic Claude as the backing LLM with ChromaDB for vector retrieval.

## Features

- Conversational bicycle maintenance support through Telegram
- RAG pipeline that retrieves relevant sections from the Buffalo Bikes Maintenance Manual (PDF) via ChromaDB
- Per-user session management with isolated agent contexts
- Multi-stage Docker build for lightweight container images
- HTTP health check endpoint for monitoring

## Architecture

```
Telegram User
    |
    v
bot.py  (python-telegram-bot)
    |
    v
rag_agents.py
    |-- BuffaloBuffAgent
    |       |-- ChromaDB vector store
    |       |-- Buffalo Bikes Maintenance Manual (PDF, fetched at init)
    |       |-- LangChain RecursiveCharacterTextSplitter
    |       |-- Anthropic Claude (claude-sonnet-4-20250514)
    |
    v
health_server.py  (Flask, port 80)
```

## Getting Started

### Prerequisites

- Python 3.11
- Docker (for containerized deployment)
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
- An Anthropic API key

### Environment Variables

Create a `.env` file in the project root:

```
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

### Run Locally with Docker

```bash
docker build -t buffalobuff .
docker run -p 80:80 --env-file .env buffalobuff
```

### Run Without Docker

```bash
pip install -r requirements.txt
python bot.py
```

## License

MIT
