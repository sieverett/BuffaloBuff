# BuffaloBuff
# Telegram Bot with AutoGen's Agentic Framework

This project is a Python-based Telegram bot that leverages the AutoGen agentic framework to facilitate conversations. The bot can respond to text messages, convert text to uppercase, and initiate chat sessions using the `rag_agents` module. 

## Features

- **Chat Functionality**: The bot initiates and maintains conversations using the `ragproxyagent` and `assistant` from the `rag_agents` module.

## Prerequisites

- Python 3.7+
- A Telegram bot token. Obtain it by creating a new bot through the [BotFather](https://core.telegram.org/bots#botfather).

## Installation

1. Clone this repository:
    ```sh
    git clone <repository_url>
    cd <repository_name>
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project root directory and add your Telegram bot token:
    ```sh
    echo "TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>" > .env
    ```

## Local Usage

1. Ensure you have your environment variables set up by loading the `.env` file:
    ```python
    from dotenv import load_dotenv
    load_dotenv('.env')
    ```

2. Run the bot:
    ```sh
    python bot.py
    ```

## Code Overview

- **Environment Setup**: The bot token is loaded from the `.env` file using the `python-dotenv` library.
- **Logging**: Configured to provide information about the bot's activity.
- **Test Handlers**:
  - `start`: Sends a welcome message when the `/start` command is issued.
  - `caps`: Converts the text following the `/caps` command to uppercase.

