"""Start command handler."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

        # Add menu button to all responses
        keyboard = [[InlineKeyboardButton("🦺 Open Menu", callback_data="menu_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if user:
            # User already registered
            from app.models.user import UserRole
            role_display = {
                UserRole.REPORTER: "Reporter",
                UserRole.ADMIN: "Admin",
                UserRole.SUPER_ADMIN: "Super Admin",
            }

            await update.effective_message.reply_text(
                f"Welcome back, *{user.full_name}*! 👋\n\n"
                f"👤 *Your Profile:*\n"
                f"├ Name: {user.full_name}\n"
                f"├ Staff ID: {user.staff_id}\n"
                f"├ Department: {user.department}\n"
                f"├ Section: {user.section}\n"
                f"└ Role: {role_display.get(user.role, 'Reporter')}\n\n"
                f"Use /menu to see all available options.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # New user - start registration
            await update.effective_message.reply_text(
                "Welcome to *Safety Inspection Bot*! 🦺\n\n"
                "I see you're new here. Let's get you registered.\n\n"
                "Please use /register to start the registration process.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )


handler = CommandHandler("start", start_command)
