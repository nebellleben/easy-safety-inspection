# Telegram Bot User Guide

## Getting Started

### 1. Find the Bot

Search for your Safety Inspection bot on Telegram using the username provided by your administrator.

### 2. Start the Bot

Send `/start` to begin. The bot will welcome you and check if you're registered.

## Quick Access Menu

The bot provides multiple ways to access its features:

1. **Command Menu** - Type `/` to see all available commands
2. **Main Menu** - Use `/menu` for an interactive button menu
3. **Quick Actions** - Tap buttons in messages to navigate

### /menu
Display an interactive menu with all bot features.

**Usage:** Send `/menu` to the bot

**Menu Options:**
- 📝 **Report Finding** - Start a new safety finding report
- 📋 **My Reports** - View your reported findings
- 👤 **My Profile** - View your profile details
- ℹ️ **Help** - Show help information

---

## Commands

### /start
Display a welcome message and check your registration status.

**Usage:** Send `/start` to the bot

**Response:**
- If registered: Shows your profile details
- If not registered: Prompts you to register

---

### /register
Register your account to start reporting findings.

**Usage:** Send `/register` to the bot

**Registration Flow:**
1. Enter your full name
2. Enter your Staff ID
3. Select your department from the list
4. Enter your section/team
5. Confirm your details

**Department Options:**
- IMD
- RSMD
- FMD
- Others

**Section Examples:**
- KBD
- EAL
- Civil
- L&AV

**Required Information:**
- Full Name (e.g., "John Doe")
- Staff ID (e.g., "STF00123")
- Department (select from list: IMD, RSMD, FMD, Others)
- Section (e.g., KBD, EAL, Civil, L&AV...)

---

### /report
Submit a new safety finding.

**Usage:** Send `/report` to the bot

**Reporting Flow:**
1. Select the area where the issue was found
2. Describe the safety issue
3. Upload a photo (or type "skip" to continue without)
4. Select the severity level
5. (Optional) Provide the specific location

**Area Options:**
- Workshop
- Equipment Room
- Storage Room
- Trackside
- Office
- Others

**Severity Levels:**
- 🟢 **Low** - Minor issue, no immediate risk
- 🟡 **Medium** - Needs attention soon
- 🟠 **High** - Significant safety concern
- 🔴 **Critical** - Immediate danger, urgent action required

**After Reporting:**
- You'll receive a Report ID (e.g., SF-2024-0001)
- Assigned admins will be notified
- Photo confirmation shown if uploaded

---

### /myreports
View all your reported findings with their current status.

**Usage:** Send `/myreports` to the bot

**Features:**
- Shows a list of all findings you've reported
- Displays current status and severity for each finding
- Interactive buttons to view full details of any finding
- Shows total count of your reports
- Load more option if you have more than 5 reports

**Detail View:**
When you click on a report, you'll see:
- Full description
- Area and location
- Severity and status with emojis
- Report date
- Assigned person (if applicable)
- Status history tracking
- Photos count (if any)
- Back button to return to the list

**Status Indicators:**
- 📋 Open - Report received, not yet reviewed
- 🔄 In Progress - Someone is working on the issue
- ✅ Resolved - Issue has been fixed
- 🔒 Closed - Issue verified and closed

**Severity Indicators:**
- 🟢 Low - Minor issue, no immediate risk
- 🟡 Medium - Needs attention soon
- 🟠 High - Significant safety concern
- 🔴 Critical - Immediate danger, urgent action required

---

### /help
Display help information and available commands.

**Usage:** Send `/help` to the bot

---

### /cancel
Cancel any ongoing operation (registration, reporting, etc.).

**Usage:** Send `/cancel` during any multi-step conversation

---

## Tips for Good Reports

### 1. Be Specific
- **Bad:** "Something is broken"
- **Good:** "Safety guard on Machine #3 is loose and vibrating"

### 2. Include Location
- **Bad:** "Near the machines"
- **Good:** "Workshop, Station 3, near the emergency stop"

### 3. Choose Correct Severity
- **Low**: Minor issues that don't pose immediate risk
- **Medium**: Issues that should be fixed within a few days
- **High**: Serious concerns that need attention today
- **Critical**: Immediate danger - stop work and report now

### 4. Use Photos
Photos help admins understand the issue better. After describing your issue, you'll be prompted to upload a photo. You can also type "skip" to continue without a photo.

---

## Report Status Meanings

| Status | Description |
|--------|-------------|
| **Open** | Report received, not yet reviewed |
| **In Progress** | Someone is working on the issue |
| **Resolved** | Issue has been fixed |
| **Closed** | Issue verified and closed |

---

## Troubleshooting

### "You need to register first"
- Use `/register` to create your account
- Contact your administrator if you continue to have issues

### "This Staff ID is already registered"
- Your Staff ID is unique to you
- Contact your administrator if you believe this is an error

### "No areas configured"
- Your administrator needs to set up areas in the system
- Contact your administrator

---

## Support

For technical support or questions about the bot:
- Contact your safety administrator
- Check the web dashboard at: https://frontend-production-c9d2.up.railway.app
- Login with your staff ID and password to view your findings
