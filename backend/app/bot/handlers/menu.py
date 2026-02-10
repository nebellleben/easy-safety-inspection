"""Menu command handler - shows bot functionality menu."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from app.repositories.user import UserRepository
from app.db.session import async_session


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /menu command - show interactive menu."""
    if not update.effective_message:
        return

    # Build menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("📝 Report Finding", callback_data="menu_report"),
            InlineKeyboardButton("📋 My Reports", callback_data="menu_myreports"),
        ],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="menu_profile"),
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "🦺 *Safety Inspection Bot Menu*\n\n"
        "Choose an option below:"
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu button clicks."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    action = query.data.replace("menu_", "")

    if action == "report":
        await query.edit_message_text(
            "📝 Starting a new safety finding report...\n\n"
            "Please use /report to begin.",
            parse_mode="Markdown"
        )
        # Trigger report command
        from app.bot.handlers.report import start as report_start
        await report_start(update, context)

    elif action == "myreports":
        from app.bot.handlers.common import my_reports_command
        await my_reports_command(update, context)

    elif action == "profile":
        if not update.effective_user:
            return

        telegram_id = update.effective_user.id

        async with async_session() as db:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_telegram_id(telegram_id)

            if not user:
                await query.edit_message_text(
                    "❌ You're not registered yet.\n\n"
                    "Use /register to get started."
                )
                return

            from app.models.user import UserRole
            role_display = {
                UserRole.REPORTER: "Reporter",
                UserRole.ADMIN: "Admin",
                UserRole.SUPER_ADMIN: "Super Admin",
            }

            message = f"""👤 *My Profile*

*Name:* {user.full_name}
*Staff ID:* {user.staff_id}
*Department:* {user.department}
*Section:* {user.section}
*Role:* {role_display.get(user.role, 'Reporter')}
*Status:* {'✅ Active' if user.is_active else '❌ Inactive'}

*Joined:* {user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A'}"""

            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="menu_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

    elif action == "help":
        from app.bot.handlers.common import help_command
        await help_command(update, context)

    elif action == "back":
        # Show menu again
        keyboard = [
            [
                InlineKeyboardButton("📝 Report Finding", callback_data="menu_report"),
                InlineKeyboardButton("📋 My Reports", callback_data="menu_myreports"),
            ],
            [
                InlineKeyboardButton("👤 My Profile", callback_data="menu_profile"),
                InlineKeyboardButton("ℹ️ Help", callback_data="menu_help"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🦺 *Safety Inspection Bot Menu*\n\n"
            "Choose an option below:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


# Get the list of bot commands for the command menu
def get_bot_commands():
    """Return list of bot commands for Telegram command menu."""
    return [
        BotCommand("start", "Start the bot or view your profile"),
        BotCommand("menu", "Show bot menu"),
        BotCommand("register", "Register your account"),
        BotCommand("report", "Report a new safety finding"),
        BotCommand("myreports", "View your reported findings"),
        BotCommand("help", "Show help information"),
        BotCommand("cancel", "Cancel current operation"),
    ]


# Create handlers
handler = CommandHandler("menu", menu_command)
callback_handler = CallbackQueryHandler(menu_callback_handler, pattern=r"^menu_")


__all__ = [
    "handler",
    "callback_handler",
    "get_bot_commands",
]
