"""Common command handlers."""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.repositories.user import UserRepository
from app.repositories.finding import FindingRepository
from app.db.session import async_session


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    if not update.effective_message:
        return

    await update.effective_message.reply_text(
        "Safety Inspection Bot Help 🦺\n\n"
        "Available commands:\n\n"
        "/start - Start the bot or see your profile\n"
        "/register - Register your account\n"
        "/report - Report a new safety finding\n"
        "/myreports - View your reported findings\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation\n\n"
        "Need help? Contact your administrator."
    )


async def my_reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /myreports command."""
    if not update.effective_user or not update.effective_message:
        return

    telegram_id = update.effective_user.id

    async with async_session() as db:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if not user:
            await update.effective_message.reply_text(
                "You need to register first! Use /register to get started."
            )
            return

        finding_repo = FindingRepository(db)
        findings, total = await finding_repo.list_findings(
            reporter_id=user.id,
            offset=0,
            limit=5,
        )

        if total == 0:
            await update.effective_message.reply_text(
                "You haven't reported any findings yet.\n\n"
                "Use /report to submit your first finding."
            )
            return

        # Format findings
        severity_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }

        message = f"Your recent findings ({total} total):\n\n"

        for f in findings[-5:]:  # Show last 5
            emoji = severity_emoji.get(f.severity, "⚪")
            message += f"{emoji} <b>{f.report_id}</b>\n"
            message += f"Status: {f.status.title().replace('_', ' ')}\n"
            message += f"{f.description[:50]}...\n\n"

        await update.effective_message.reply_text(message, parse_mode="HTML")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cancel command."""
    if not update.effective_message:
        return

    await update.effective_message.reply_text(
        "Operation cancelled. Use /help to see available commands."
    )


# Create handlers
handler = CommandHandler("help", help_command)
my_reports_handler = CommandHandler("myreports", my_reports_command)
cancel_handler = CommandHandler("cancel", cancel_command)

# Export individual handlers
__all__ = ["handler", "my_reports_handler", "cancel_handler"]
