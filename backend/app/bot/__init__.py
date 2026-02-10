"""Telegram bot module."""
from telegram.ext import Application

from app.core.config import settings


async def setup_bot_commands(application: Application) -> None:
    """Set up bot commands for the Telegram command menu."""
    from app.bot.handlers.menu import get_bot_commands

    commands = get_bot_commands()
    await application.bot.set_my_commands(commands)


def create_bot_application() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Set up bot commands on startup
    application.post_init = setup_bot_commands

    # Register handlers - order matters! Conversation handlers first
    from app.bot.handlers import (
        start,
        register,
        report,
        common,
        menu,
    )

    # Conversation handlers (must be added before simple command handlers)
    application.add_handler(register.handler)
    application.add_handler(report.handler)

    # Simple command handlers
    application.add_handler(start.handler)
    application.add_handler(menu.handler)
    application.add_handler(common.handler)
    application.add_handler(common.my_reports_handler)
    application.add_handler(common.cancel_handler)

    # Callback handlers for navigation
    application.add_handler(menu.callback_handler)
    application.add_handler(common.my_reports_detail_handler)
    application.add_handler(common.my_reports_back_handler)

    return application


# Global bot application instance
bot_app: Application | None = None


def get_bot() -> Application:
    """Get the bot application instance."""
    global bot_app
    if bot_app is None:
        bot_app = create_bot_application()
    return bot_app
