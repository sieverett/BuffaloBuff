# BuffaloBuff

Telegram chatbot with RAG for Buffalo Bike maintenance using Azure OpenAI and AutoGen.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![AutoGen](https://img.shields.io/badge/AutoGen-4B0082?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

---

## About

BuffaloBuff is a Telegram bot that provides mechanical support for [World Bicycle Relief](https://worldbicyclerelief.org/)'s Buffalo Bikes. It uses retrieval-augmented generation (RAG) to answer maintenance questions grounded in the official Buffalo Bikes Maintenance Manual. The bot is built on Microsoft AutoGen's multi-agent framework with Azure OpenAI as the backing LLM.

## Features

- Conversational bicycle maintenance support through Telegram
- RAG pipeline that retrieves relevant sections from the Buffalo Bikes Maintenance Manual (PDF) via ChromaDB
- Per-user session management with isolated agent contexts
- Multi-stage Docker build for lightweight container images
- CI/CD pipeline via GitHub Actions deploying to Azure App Service
- HTTP health check endpoint for Azure monitoring

## Architecture

```
Telegram User
    |
    v
bot.py  (python-telegram-bot)
    |
    v
rag_agents.py
    |-- RetrieveUserProxyAgent  (AutoGen)
    |       |-- ChromaDB vector store
    |       |-- Buffalo Bikes Maintenance Manual (PDF, fetched at init)
    |       |-- LangChain RecursiveCharacterTextSplitter
    |
    |-- RetrieveAssistantAgent  (AutoGen + Azure OpenAI)
    |
    v
health_server.py  (Flask, port 80)
```

## Getting Started

### Prerequisites

- Python 3.11
- Docker (for containerized deployment)
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
- Azure OpenAI resource with a deployed model

### Environment Variables

Create a `.env` file in the project root:

```
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
DEPLOYMENT_NAME=<your-model-deployment-name>
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

### Deploy to Azure

The repository includes a GitHub Actions workflow (`.github/workflows/azure-deployment.yml`) that builds the Docker image, pushes it to Azure Container Registry, and deploys it to Azure App Service on every push to `main`. Configure the required secrets in your GitHub repository settings.

## License

MIT
