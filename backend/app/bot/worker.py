"""Telegram bot worker - runs the bot in polling mode."""
import asyncio
import logging

from app.bot import get_bot
from app.core.config import settings
from telegram import BotCommand

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def setup_bot_commands(application) -> None:
    """Set up bot commands for the Telegram command menu."""
    commands = [
        BotCommand("start", "Start the bot or view your profile"),
        BotCommand("menu", "Show bot menu"),
        BotCommand("register", "Register your account"),
        BotCommand("report", "Report a new safety finding"),
        BotCommand("myreports", "View your reported findings"),
        BotCommand("help", "Show help information"),
        BotCommand("cancel", "Cancel current operation"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands registered")


async def main() -> None:
    """Start the bot."""
    logger.info("Starting Telegram bot...")

    application = get_bot()

    # Start the bot using polling
    # In production, you should use webhook instead
    await application.initialize()
    await application.start()

    # Set up bot commands menu
    await setup_bot_commands(application)

    await application.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query", "chosen_inline_result"],
    )

    logger.info("Bot is running... Press Ctrl+C to stop.")

    try:
        # Keep the bot running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
