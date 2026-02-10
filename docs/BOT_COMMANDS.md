# Telegram Bot User Guide

## Getting Started

### 1. Find the Bot

Search for your Safety Inspection bot on Telegram using the username provided by your administrator.

### 2. Start the Bot

Send `/start` to begin. The bot will welcome you and check if you're registered.

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

**Required Information:**
- Full Name (e.g., "John Doe")
- Staff ID (e.g., "STF00123")
- Department (select from list)
- Section (e.g., "Line A", "QC Team")

---

### /report
Submit a new safety finding.

**Usage:** Send `/report` to the bot

**Reporting Flow:**
1. Select the area where the issue was found
2. Describe the safety issue
3. Select the severity level
4. (Optional) Provide the specific location
5. Confirm your report

**Severity Levels:**
- 🟢 **Low** - Minor issue, no immediate risk
- 🟡 **Medium** - Needs attention soon
- 🟠 **High** - Significant safety concern
- 🔴 **Critical** - Immediate danger, urgent action required

**After Reporting:**
- You'll receive a Report ID (e.g., SF-2024-0001)
- Assigned admins will be notified
- You can track status via `/myreports`

---

### /myreports
View all findings you've reported.

**Usage:** Send `/myreports` to the bot

**Response:** Shows your last 5 reports with:
- Report ID
- Severity level
- Current status
- Description preview

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
- **Good:** "Production Line A, Station 3, near the emergency stop"

### 3. Choose Correct Severity
- **Low**: Minor issues that don't pose immediate risk
- **Medium**: Issues that should be fixed within a few days
- **High**: Serious concerns that need attention today
- **Critical**: Immediate danger - stop work and report now

### 4. Use Photos
Photos help admins understand the issue better. You can send photos along with your description.

---

## Report Status Meanings

| Status | Description |
|--------|-------------|
| **Open** | Report received, not yet reviewed |
| **In Progress** | Someone is working on the issue |
| **Resolved** | Issue has been fixed |
| **Closed** | Issue verified and closed |

---

## Notifications

After registration, you may receive notifications about:
- Status updates on your reports
- Requests for more information
- Confirmations when issues are resolved

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
- Check the web dashboard at the provided URL
- Review your open findings with `/myreports`
