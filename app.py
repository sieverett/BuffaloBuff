from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
# from bot import fetch_agent
from rag_agents import fetch_agent


load_dotenv('.env')
telegram_token=os.getenv("TELEGRAM_BOT_TOKEN")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


ragproxyagent, assistant = fetch_agent()
ragproxyagent.reset()
assistant.reset()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    
async def bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("update:::", update.message.text)
    response = ragproxyagent.initiate_chat(assistant,
                                           silent=False, 
                                           message=update.message.text, 
                                           clear_history=False)
    chat_history = response.chat_history
    res = chat_history[-1]['content']
    _l=len(chat_history)
    if _l >= 6:
        ragproxyagent.clear_history(nr_messages_to_preserve=6)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=res)


if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    
    start_handler = CommandHandler('start', start)
    bot_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), bot)
    caps_handler = CommandHandler('caps', caps)
    application.add_handler(start_handler)
    application.add_handler(bot_handler)
    application.add_handler(caps_handler)
    
    application.run_polling()