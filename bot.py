import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from rag_agents import fetch_agent
from health_server import run as run_health_server

load_dotenv(".env")

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    sys.exit("Error: TELEGRAM_BOT_TOKEN environment variable not set.")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Dictionary to store user-specific agents
user_contexts: dict = {}
user_contexts_lock = asyncio.Lock()


async def get_user_context(user_id: int) -> dict | None:
    """
    Asynchronously retrieve or create a user-specific context containing the agent.

    Args:
        user_id (int): Unique identifier for the user.

    Returns:
        dict: The user's context containing the agent.
        None: If an error occurs during initialization.
    """
    async with user_contexts_lock:
        if user_id not in user_contexts:
            try:
                agent = fetch_agent()
                user_contexts[user_id] = {
                    "agent": agent,
                }
                logger.info(f"Initialized context for user {user_id}.")
            except Exception as e:
                logger.exception(
                    f"Failed to initialize context for user {user_id}: {e}"
                )
                return None
        else:
            logger.debug(f"Retrieved existing context for user {user_id}.")
        return user_contexts[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} initiated /start command.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /caps command."""
    user_id = update.effective_user.id
    args = context.args
    logger.info(f"User {user_id} initiated /caps command with args: {args}")
    if args:
        text_caps = " ".join(args).upper()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Usage: /caps <text>"
        )


async def bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for regular messages."""
    user_id = update.effective_user.id
    user_message = update.message.text
    logger.info(f"Received message from user {user_id}: {user_message}")

    user_context = await get_user_context(user_id)
    if not user_context:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred initializing your session. Please try again later.",
        )
        return

    agent = user_context["agent"]

    try:
        bot_response = await asyncio.to_thread(agent.chat, user_message)
        logger.info(f"Generated response for user {user_id}: {bot_response[:100]}...")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=bot_response
        )
    except Exception as e:
        logger.exception(f"Error handling message from user {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred while processing your message. Please try again later.",
        )


async def start_health_server_task() -> None:
    """Start the health server as a background task."""
    await asyncio.to_thread(run_health_server)


def main() -> None:
    """Main function to start the bot and the HTTP health server."""
    logger.info("Starting the Telegram bot and health server...")

    try:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Register command and message handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("caps", caps))
        application.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), bot_handler)
        )

        # Start the health server in a separate task
        loop = asyncio.get_event_loop()
        loop.create_task(start_health_server_task())

        logger.info("Bot is polling for updates...")
        application.run_polling()
    except Exception as e:
        logger.exception(f"Failed to start the bot or health server: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot and health server have been stopped.")


if __name__ == "__main__":
    main()
