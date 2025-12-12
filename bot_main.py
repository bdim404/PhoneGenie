import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from phone_agent.config.bot_config import BotConfig
from phone_agent.interfaces.telegram import TelegramInterface
from phone_agent.interfaces.task_runner import TaskRunner

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

config = BotConfig()
active_tasks = {}


def check_auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != config.allowed_user_id:
            await update.message.reply_text("Unauthorized user")
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            return
        return await func(update, context)
    return wrapper


@check_auth
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Welcome to Open-AutoGLM Bot!*\n\n"
        "Send me a task to automate your phone.\n\n"
        "*Commands:*\n"
        "/start - Show this message\n"
        "/cancel - Cancel current task\n"
        "/status - Show device status\n\n"
        "*Example:*\n"
        "Open WeChat and send a message",
        parse_mode='Markdown'
    )


@check_auth
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_tasks:
        interface = active_tasks[chat_id]
        interface.cancel()
        await update.message.reply_text("Cancelling task...")
    else:
        await update.message.reply_text("No active task")


@check_auth
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from phone_agent.adb import list_devices

    try:
        devices = list_devices()
        if not devices:
            await update.message.reply_text("No devices connected")
            return

        device_info = "\n".join([
            f"• {d.device_id} ({d.status})" for d in devices
        ])
        await update.message.reply_text(
            f"*Connected Devices:*\n\n{device_info}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"Error getting device status: {str(e)}")
        logger.error(f"Status command error: {e}", exc_info=True)


@check_auth
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in active_tasks:
        await update.message.reply_text(
            "Another task is running. Use /cancel to stop it."
        )
        return

    task = update.message.text

    interface = TelegramInterface(update, context)
    active_tasks[chat_id] = interface

    try:
        runner = TaskRunner(
            interface=interface,
            model_config=config.model_config,
            agent_config=config.agent_config
        )

        result = await runner.run_task(task)
        logger.info(f"Task completed: {result}")

    except Exception as e:
        logger.error(f"Task error: {e}", exc_info=True)
        await interface.send_message(f"Error: {str(e)}")

    finally:
        if chat_id in active_tasks:
            del active_tasks[chat_id]


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    if chat_id not in active_tasks:
        return

    interface = active_tasks[chat_id]

    if query.data == "confirm_yes":
        interface.handle_confirmation_callback(True)
        await query.edit_message_text("Confirmed")
    elif query.data == "confirm_no":
        interface.handle_confirmation_callback(False)
        await query.edit_message_text("Cancelled")
    elif query.data == "takeover_done":
        interface.handle_confirmation_callback(True)
        await query.edit_message_text("Continuing task...")


def main():
    try:
        application = Application.builder().token(config.token).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        ))
        application.add_handler(CallbackQueryHandler(handle_callback_query))

        logger.info("Bot started successfully")
        application.run_polling()

    except Exception as e:
        logger.error(f"Bot startup error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
