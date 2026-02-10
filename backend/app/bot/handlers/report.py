"""Report command handler with conversation flow."""
import uuid
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from app.models.finding import Severity, Status
from app.repositories.user import UserRepository
from app.repositories.finding import FindingRepository
from app.repositories.area import AreaRepository
from app.db.session import async_session

# Conversation states
SELECT_AREA, DESCRIPTION, SEVERITY, LOCATION, CONFIRM = range(5)

# Severity options with emojis
SEVERITY_OPTIONS = {
    "Low": "🟢 Low",
    "Medium": "🟡 Medium",
    "High": "🟠 High",
    "Critical": "🔴 Critical",
}


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the report finding conversation."""
    if not update.effective_user or not update.effective_message:
        return ConversationHandler.END

    telegram_id = update.effective_user.id

    # Check if user is registered
    async with async_session() as db:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if not user:
            await update.effective_message.reply_text(
                "You need to register first! Use /register to get started."
            )
            return ConversationHandler.END

        # Get available areas
        area_repo = AreaRepository(db)
        areas = await area_repo.list_areas(level=1)  # Get top-level areas

        if not areas:
            await update.effective_message.reply_text(
                "No areas configured yet. Please contact your administrator."
            )
            return ConversationHandler.END

        context.user_data["report"] = {"user_id": user.id}

        # Create area keyboard
        keyboard = [[InlineKeyboardButton(a.name, callback_data=f"area_{a.id}")] for a in areas[:10]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.reply_text(
            "Let's report a safety finding! 🔍\n\n"
            "Which area is this finding related to?",
            reply_markup=reply_markup,
        )

        return SELECT_AREA


async def area_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle area selection from callback query."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    area_id = query.data.split("_")[1]
    context.user_data["report"]["area_id"] = uuid.UUID(area_id)

    await query.edit_message_text(
        "Got it! Now please describe the safety issue you found.\n\n"
        "What did you observe?"
    )

    return DESCRIPTION


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle description input."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please provide a description.")
        return DESCRIPTION

    description = update.effective_message.text.strip()

    if len(description) < 5:
        await update.effective_message.reply_text(
            "Description is too short. Please provide more details."
        )
        return DESCRIPTION

    context.user_data["report"]["description"] = description

    # Create severity keyboard
    keyboard = [
        [InlineKeyboardButton(SEVERITY_OPTIONS["Low"], callback_data="sev_low")],
        [InlineKeyboardButton(SEVERITY_OPTIONS["Medium"], callback_data="sev_medium")],
        [InlineKeyboardButton(SEVERITY_OPTIONS["High"], callback_data="sev_high")],
        [InlineKeyboardButton(SEVERITY_OPTIONS["Critical"], callback_data="sev_critical")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        "How severe is this issue?",
        reply_markup=reply_markup,
    )

    return SEVERITY


async def severity_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle severity selection from callback query."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    severity_str = query.data.split("_")[1]
    context.user_data["report"]["severity"] = Severity(severity_str)

    await query.edit_message_text(
        "Got it! One last question:\n\n"
        "What is the specific location of this issue? "
        "(e.g., 'Near entrance', 'Machine #3', or reply 'skip' to skip)"
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle location input."""
    if not update.effective_message or not update.effective_message.text:
        await update.effective_message.reply_text("Please provide a location or 'skip'.")
        return LOCATION

    location_text = update.effective_message.text.strip()

    if location_text.lower() not in ("skip", "-"):
        context.user_data["report"]["location"] = location_text
    else:
        context.user_data["report"]["location"] = None

    # Create finding
    report_data = context.user_data["report"]

    async with async_session() as db:
        finding_repo = FindingRepository(db)

        # Generate report ID
        report_id = await finding_repo.get_next_report_id()

        # Create finding
        finding = await finding_repo.create({
            "report_id": report_id,
            "reporter_id": report_data["user_id"],
            "area_id": report_data["area_id"],
            "description": report_data["description"],
            "severity": report_data["severity"],
            "status": Status.OPEN,
            "location": report_data.get("location"),
        })

        await db.commit()

    # Get severity emoji
    severity_emoji = {
        Severity.LOW: "🟢",
        Severity.MEDIUM: "🟡",
        Severity.HIGH: "🟠",
        Severity.CRITICAL: "🔴",
    }

    await update.effective_message.reply_text(
        f"Your safety finding has been recorded! ✅\n\n"
        f"Report ID: {finding.report_id}\n"
        f"Severity: {severity_emoji[finding.severity]} {finding.severity.title()}\n"
        f"Status: {finding.status.title().replace('_', ' ')}\n\n"
        f"Thank you for helping keep our workplace safe! 🦺\n\n"
        f"Use /report to submit another finding."
    )

    # TODO: Send notification to assigned admins

    return ConversationHandler.END


async def cancel_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the report conversation."""
    await update.effective_message.reply_text(
        "Report cancelled. Use /report to start again."
    )
    return ConversationHandler.END


# Create the conversation handler
handler = ConversationHandler(
    entry_points=[CommandHandler("report", report_command)],
    states={
        SELECT_AREA: [CallbackQueryHandler(area_selected)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        SEVERITY: [CallbackQueryHandler(severity_selected)],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
    },
    fallbacks=[CommandHandler("cancel", cancel_report)],
)
