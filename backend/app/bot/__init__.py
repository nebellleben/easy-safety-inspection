"""Telegram bot module."""
from telegram.ext import Application

from app.core.config import settings


def create_bot_application() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

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
