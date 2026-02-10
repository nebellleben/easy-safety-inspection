"""Registration command handler with conversation flow."""
from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes

from app.models.user import Role
from app.repositories.user import UserRepository
from app.db.session import async_session

# Conversation states
FULL_NAME, STAFF_ID, DEPARTMENT, SECTION, CONFIRM = range(5)

# Predefined departments
DEPARTMENTS = [
    "Production",
    "Quality Assurance",
    "Maintenance",
    "Warehouse",
    "Logistics",
    "Administration",
    "Safety",
    "Engineering",
    "Other",
]


async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the registration conversation."""
    if not update.effective_user or not update.effective_message:
        return ConversationHandler.END

    telegram_id = update.effective_user.id

    # Check if user already exists
    async with async_session() as db:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if user:
            await update.effective_message.reply_text(
                "You are already registered! Use /report to submit findings."
            )
            return ConversationHandler.END

    # Start registration
    context.user_data["registration"] = {}

    await update.effective_message.reply_text(
        "Let's register your account! 📝\n\n"
        "First, what is your full name?"
    )

    return FULL_NAME


async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle full name input."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please provide your name.")
        return FULL_NAME

    full_name = update.effective_message.text.strip()
    context.user_data["registration"]["full_name"] = full_name
    context.user_data["registration"]["username"] = update.effective_user.username

    await update.effective_message.reply_text(
        f"Nice to meet you, {full_name}! 👋\n\n"
        "What is your Staff ID?"
    )

    return STAFF_ID


async def staff_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle staff ID input."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please provide your Staff ID.")
        return STAFF_ID

    staff_id = update.effective_message.text.strip()

    # Validate staff ID format (basic check)
    if len(staff_id) < 2:
        await update.effective_message.reply_text(
            "Staff ID seems too short. Please try again."
        )
        return STAFF_ID

    context.user_data["registration"]["staff_id"] = staff_id

    # Create department keyboard
    keyboard = [[dept] for dept in DEPARTMENTS]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}

    await update.effective_message.reply_text(
        "Which department do you belong to?",
        reply_markup=reply_markup,
    )

    return DEPARTMENT


async def department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle department selection."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please select a department.")
        return DEPARTMENT

    department = update.effective_message.text.strip()

    if department not in DEPARTMENTS:
        await update.effective_message.reply_text(
            f"Please select from the list: {', '.join(DEPARTMENTS)}"
        )
        return DEPARTMENT

    context.user_data["registration"]["department"] = department

    await update.effective_message.reply_text(
        f"Got it! What is your section within {department}?\n"
        "(e.g., 'Line A', 'QC Team', 'Night Shift')"
    )

    return SECTION


async def section(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle section input."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please provide your section.")
        return SECTION

    section = update.effective_message.text.strip()
    context.user_data["registration"]["section"] = section

    # Show confirmation
    reg_data = context.user_data["registration"]

    await update.effective_message.reply_text(
        "Please review your details:\n\n"
        f"Name: {reg_data['full_name']}\n"
        f"Staff ID: {reg_data['staff_id']}\n"
        f"Department: {reg_data['department']}\n"
        f"Section: {reg_data['section']}\n\n"
        "Reply 'YES' to confirm or 'NO' to start over."
    )

    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirmation and create user."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please confirm with 'YES' or 'NO'.")
        return CONFIRM

    response = update.effective_message.text.strip().lower()

    if response not in ("yes", "y"):
        await update.effective_message.reply_text(
            "Registration cancelled. Use /register to start again."
        )
        return ConversationHandler.END

    # Create user
    reg_data = context.user_data["registration"]
    telegram_id = update.effective_user.id

    async with async_session() as db:
        user_repo = UserRepository(db)

        # Check for duplicate staff_id
        existing = await user_repo.get_by_staff_id(reg_data["staff_id"])
        if existing:
            await update.effective_message.reply_text(
                "This Staff ID is already registered. Please contact support."
            )
            return ConversationHandler.END

        user = await user_repo.create({
            "telegram_id": telegram_id,
            "username": reg_data.get("username"),
            "full_name": reg_data["full_name"],
            "staff_id": reg_data["staff_id"],
            "department": reg_data["department"],
            "section": reg_data["section"],
            "role": Role.REPORTER,
            "is_active": True,
        })

        await db.commit()

    await update.effective_message.reply_text(
        f"Registration complete! 🎉\n\n"
        f"Welcome, {user.full_name}!\n\n"
        f"You can now use /report to submit safety findings."
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.effective_message.reply_text(
        "Registration cancelled. Use /register to start again."
    )
    return ConversationHandler.END


# Create the conversation handler
handler = ConversationHandler(
    entry_points=[CommandHandler("register", register_command)],
    states={
        FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
        STAFF_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, staff_id)],
        DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, department)],
        SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, section)],
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
