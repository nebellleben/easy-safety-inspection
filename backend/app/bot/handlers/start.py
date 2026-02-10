"""Start command handler."""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.repositories.user import UserRepository
from app.db.session import async_session


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    if not update.effective_user or not update.effective_message:
        return

    telegram_id = update.effective_user.id

    async with async_session() as db:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if user:
            # User already registered
            await update.effective_message.reply_text(
                f"Welcome back, {user.full_name}! 👋\n\n"
                f"Your details:\n"
                f"Name: {user.full_name}\n"
                f"Staff ID: {user.staff_id}\n"
                f"Department: {user.department}\n"
                f"Section: {user.section}\n\n"
                f"Use /report to submit a new safety finding."
            )
        else:
            # New user - start registration
            await update.effective_message.reply_text(
                "Welcome to Safety Inspection Bot! 🦺\n\n"
                "I see you're new here. Let's get you registered.\n\n"
                "Please use /register to start the registration process."
            )


handler = CommandHandler("start", start_command)
