import os
import sys
import time
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

# Configure logging once for the entire application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Maximum allowed message length (characters) from users
MAX_MESSAGE_LENGTH = 4096

# Maximum number of cached user sessions and TTL in seconds
MAX_USER_CONTEXTS = 1000
USER_CONTEXT_TTL = 3600  # 1 hour

# Dictionary to store user-specific agents
user_contexts: dict = {}
user_contexts_lock = asyncio.Lock()


def _evict_stale_contexts() -> None:
    """Remove user contexts that have not been used within USER_CONTEXT_TTL."""
    now = time.monotonic()
    stale = [
        uid
        for uid, ctx in user_contexts.items()
        if now - ctx["last_used"] > USER_CONTEXT_TTL
    ]
    for uid in stale:
        del user_contexts[uid]
        logger.info(f"Evicted stale context for user {uid}.")


async def get_user_context(user_id: int) -> dict | None:
    """
    Asynchronously retrieve or create a user-specific context containing the agent.

    Evicts stale sessions and caps total sessions at MAX_USER_CONTEXTS.

    Args:
        user_id: Unique identifier for the user.

    Returns:
        dict: The user's context containing the agent.
        None: If an error occurs during initialization.
    """
    async with user_contexts_lock:
        _evict_stale_contexts()

        if user_id in user_contexts:
            user_contexts[user_id]["last_used"] = time.monotonic()
            return user_contexts[user_id]

        if len(user_contexts) >= MAX_USER_CONTEXTS:
            # Evict the least-recently-used context
            oldest_uid = min(user_contexts, key=lambda uid: user_contexts[uid]["last_used"])
            del user_contexts[oldest_uid]
            logger.info(f"Evicted LRU context for user {oldest_uid} (cap reached).")

        try:
            agent = fetch_agent()
            user_contexts[user_id] = {
                "agent": agent,
                "last_used": time.monotonic(),
            }
            logger.info(f"Initialized context for user {user_id}.")
        except Exception:
            logger.exception(f"Failed to initialize context for user {user_id}")
            return None

        return user_contexts[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command."""
    logger.info(f"User {update.effective_user.id} initiated /start command.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for regular messages."""
    user_id = update.effective_user.id
    user_message = update.message.text

    if not user_message:
        return

    if len(user_message) > MAX_MESSAGE_LENGTH:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Please keep your message under {MAX_MESSAGE_LENGTH} characters.",
        )
        return

    logger.info(f"Received message from user {user_id} (length={len(user_message)}).")

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
    except Exception:
        logger.exception(f"Error handling message from user {user_id}")
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
        application.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), bot_handler)
        )

        # Schedule the health server to start alongside the bot
        application.post_init = lambda app: app.create_task(start_health_server_task())

        logger.info("Bot is polling for updates...")
        application.run_polling()
    except Exception:
        logger.exception("Failed to start the bot or health server")
        sys.exit(1)
    finally:
        logger.info("Bot and health server have been stopped.")


if __name__ == "__main__":
    main()
