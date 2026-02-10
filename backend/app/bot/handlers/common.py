"""Common command handlers."""
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from app.repositories.user import UserRepository
from app.repositories.finding import FindingRepository
from app.models.finding import Severity, Status
from app.db.session import async_session


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    if not update.effective_message:
        return

    keyboard = [[InlineKeyboardButton("🦺 Open Menu", callback_data="menu_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        "🦺 *Safety Inspection Bot Help*\n\n"
        "*Available commands:*\n\n"
        "/start - Start the bot or see your profile\n"
        "/menu - Show the main menu\n"
        "/register - Register your account\n"
        "/report - Report a new safety finding\n"
        "/myreports - View your reported findings\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation\n\n"
        "*Quick Tip:* Type `/` to see all available commands!\n\n"
        "Need help? Contact your administrator.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def my_reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /myreports command - show user's findings with interactive buttons."""
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

        # Get user's findings
        finding_repo = FindingRepository(db)
        findings, total = await finding_repo.list_findings(
            reporter_id=user.id,
            limit=10
        )

        if total == 0:
            await update.effective_message.reply_text(
                "You haven't reported any findings yet.\n\n"
                "Use /report to submit your first safety finding."
            )
            return

        # Build response with buttons
        severity_emoji = {
            Severity.LOW: "🟢",
            Severity.MEDIUM: "🟡",
            Severity.HIGH: "🟠",
            Severity.CRITICAL: "🔴",
        }

        status_emoji = {
            Status.OPEN: "📋",
            Status.IN_PROGRESS: "🔄",
            Status.RESOLVED: "✅",
            Status.CLOSED: "🔒",
        }

        message = f"📋 *Your Reported Findings* ({total} total)\n\n"

        keyboard = []
        for finding in findings[:5]:  # Show max 5
            sev_emoji = severity_emoji.get(finding.severity, "⚪")
            stat_emoji = status_emoji.get(finding.status, "📋")
            area_name = finding.area.name if finding.area else "N/A"

            keyboard.append([InlineKeyboardButton(
                f"{finding.report_id} - {sev_emoji} {finding.severity.title()} - {stat_emoji} {finding.status.title()}",
                callback_data=f"myreports_detail_{finding.id}"
            )])

            message += (
                f"{stat_emoji} *{finding.report_id}*\n"
                f"{sev_emoji} {finding.severity.title()} | 📍 {area_name}\n"
                f"📝 {finding.description[:40]}{'...' if len(finding.description) > 40 else ''}\n"
                f"━━━━━━━━━━━━━━━━\n"
            )

        # Add navigation button if more than 5 findings
        if total > 5:
            keyboard.append([InlineKeyboardButton(
                f"📄 Load More ({total - 5} more)",
                callback_data="myreports_more"
            )])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def my_reports_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle viewing details of a specific finding."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    finding_id = query.data.split("_")[-1]

    async with async_session() as db:
        finding_repo = FindingRepository(db)
        finding = await finding_repo.get_by_id(uuid.UUID(finding_id))

        if not finding:
            await query.edit_message_text(
                "❌ Finding not found. It may have been deleted."
            )
            return

        # Build detail message
        severity_emoji = {
            Severity.LOW: "🟢",
            Severity.MEDIUM: "🟡",
            Severity.HIGH: "🟠",
            Severity.CRITICAL: "🔴",
        }

        status_emoji = {
            Status.OPEN: "📋",
            Status.IN_PROGRESS: "🔄",
            Status.RESOLVED: "✅",
            Status.CLOSED: "🔒",
        }

        sev_icon = severity_emoji.get(finding.severity, "")
        stat_icon = status_emoji.get(finding.status, "")

        message = f"""
📋 *Finding Details*

*Report ID:* {finding.report_id}
*Severity:* {sev_icon} {finding.severity.title()}
*Status:* {stat_icon} {finding.status.title().replace('_', ' ')}

📍 *Area:* {finding.area.name if finding.area else 'N/A'}
📍 *Location:* {finding.location or 'Not specified'}

📝 *Description:*
{finding.description}

🕐 *Reported:* {finding.reported_at.strftime('%Y-%m-%d %H:%M')} UTC
"""

        if finding.closed_at:
            message += f"🔒 *Closed:* {finding.closed_at.strftime('%Y-%m-%d %H:%M')} UTC\n"

        if finding.assignee:
            message += f"👤 *Assigned To:* {finding.assignee.full_name}\n"

        # Add photos if available
        if finding.photos:
            message += f"\n📷 *Photos:* {len(finding.photos)} attached\n"

        # Add status history
        if finding.status_history:
            message += "\n━━━━━━━━━━━━━━━━\n📜 *Status History:*\n"
            for history in finding.status_history:
                old_str = history.old_status or "Created"
                old_formatted = old_str.title().replace('_', ' ')
                new_formatted = history.new_status.title().replace('_', ' ')
                message += f"  {old_formatted} → {new_formatted}"
                if history.notes:
                    message += f"\n    📝 {history.notes}"
                if history.updated_by_user:
                    message += f"\n    👤 {history.updated_by_user.full_name}"
                message += f"\n    🕐 {history.updated_at.strftime('%Y-%m-%d %H:%M')}\n"

        # Add back button
        keyboard = [[InlineKeyboardButton("« Back to My Reports", callback_data="myreports_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def my_reports_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to reports button."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    # Get the user and refresh their reports
    telegram_id = update.effective_user.id

    async with async_session() as db:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if not user:
            await query.edit_message_text(
                "You need to register first! Use /register to get started."
            )
            return

        # Get user's findings
        finding_repo = FindingRepository(db)
        findings, total = await finding_repo.list_findings(
            reporter_id=user.id,
            limit=10
        )

        if total == 0:
            await query.edit_message_text(
                "You haven't reported any findings yet.\n\n"
                "Use /report to submit your first safety finding."
            )
            return

        # Build response with buttons
        severity_emoji = {
            Severity.LOW: "🟢",
            Severity.MEDIUM: "🟡",
            Severity.HIGH: "🟠",
            Severity.CRITICAL: "🔴",
        }

        status_emoji = {
            Status.OPEN: "📋",
            Status.IN_PROGRESS: "🔄",
            Status.RESOLVED: "✅",
            Status.CLOSED: "🔒",
        }

        message = f"📋 *Your Reported Findings* ({total} total)\n\n"

        keyboard = []
        for finding in findings[:5]:
            sev_emoji = severity_emoji.get(finding.severity, "⚪")
            stat_emoji = status_emoji.get(finding.status, "📋")
            area_name = finding.area.name if finding.area else "N/A"

            keyboard.append([InlineKeyboardButton(
                f"{finding.report_id} - {sev_emoji} {finding.severity.title()} - {stat_emoji} {finding.status.title()}",
                callback_data=f"myreports_detail_{finding.id}"
            )])

            message += (
                f"{stat_emoji} *{finding.report_id}*\n"
                f"{sev_emoji} {finding.severity.title()} | 📍 {area_name}\n"
                f"📝 {finding.description[:40]}{'...' if len(finding.description) > 40 else ''}\n"
                f"━━━━━━━━━━━━━━━━\n"
            )

        if total > 5:
            keyboard.append([InlineKeyboardButton(
                f"📄 Load More ({total - 5} more)",
                callback_data="myreports_more"
            )])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cancel command."""
    if not update.effective_message:
        return

    await update.effective_message.reply_text(
        "❌ Operation cancelled.\n\n"
        "Use /help to see available commands."
    )


# Create handlers
handler = CommandHandler("help", help_command)
my_reports_handler = CommandHandler("myreports", my_reports_command)
cancel_handler = CommandHandler("cancel", cancel_command)

# Callback handlers for myreports navigation
my_reports_detail_handler = CallbackQueryHandler(
    my_reports_detail_callback,
    pattern=r"^myreports_detail_"
)
my_reports_back_handler = CallbackQueryHandler(
    my_reports_back_callback,
    pattern=r"^myreports_back$"
)

# Export individual handlers
__all__ = [
    "handler",
    "my_reports_handler",
    "cancel_handler",
    "my_reports_detail_handler",
    "my_reports_back_handler"
]
