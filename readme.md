# USARB Schedule Automation

Python script that scrapes the CSRF token and session data from https://orar.usarb.md/, then queries the internal API to fetch the weekly schedule and syncs it directly to your iCloud Calendar using CalDAV.

## Features

- ✅ Fetches schedule data from USARB website
- ✅ Syncs lessons directly to iCloud Calendar (no .ics file needed)
- ✅ Unique event IDs prevent duplicates
- ✅ Automatic event updates when schedule changes
- ✅ Supports syncing specific weeks or date ranges
- ✅ Safe overwriting of existing events

## Prerequisites

1. **Python 3.7+** installed
2. **iCloud account** with Two-Factor Authentication enabled
3. **App-specific password** for iCloud (see setup below)

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### Step 1: Enable Two-Factor Authentication

If you haven't already enabled 2FA on your Apple ID:
- On your iPhone/iPad: Go to **Settings** > **[Your Name]** > **Password & Security** > **Two-Factor Authentication**
- Enable it if not already enabled

### Step 2: Generate an App-Specific Password

**⚠️ Important:** You cannot use your regular iCloud password. You MUST use an app-specific password.

1. Go to [Apple ID Account Page](https://appleid.apple.com/)
2. Sign in with your Apple ID
3. In the **Sign-In and Security** section, find **App-Specific Passwords**
4. Click **Generate an app-specific password**
5. Enter a label (e.g., "USARB Schedule Sync")
6. Click **Create**
7. **Copy the 16-character password immediately** (you won't be able to see it again!)

### Step 3: Create `.env` File

Create a `.env` file in the project root directory with the following content:

```env
# iCloud CalDAV Configuration
CALDAV_URL=https://caldav.icloud.com/

# Your iCloud email address (e.g., yourname@icloud.com)
ICLOUD_USERNAME=your.email@icloud.com

# The app-specific password you generated (NOT your regular password!)
ICLOUD_PASSWORD=abcd-efgh-ijkl-mnop

# Calendar name (will be created if doesn't exist)
CALENDAR_NAME=USARB Schedule

# Your group name (e.g., IT11Z, IT12Z, etc.)
GROUP_NAME=IT11Z
```

**Replace the values:**
- `ICLOUD_USERNAME`: Your iCloud email address
- `ICLOUD_PASSWORD`: The app-specific password you generated (format: `xxxx-xxxx-xxxx-xxxx`)
- `CALENDAR_NAME`: Name for the calendar (optional, defaults to "USARB Schedule")
- `GROUP_NAME`: Your group name from the schedule

### Step 4: Verify Your iCloud Email

Make sure you're using the correct iCloud email format:
- `yourname@icloud.com` ✅
- `yourname@me.com` ✅
- `yourname@mac.com` ✅

## Usage

### Basic Usage

Sync current week and next 4 weeks (default):
```bash
python main.py
```

### Sync Specific Weeks

```bash
# Sync specific weeks
python main.py --weeks 1,2,3,4,5

# Sync a range of weeks
python main.py --start-week 1 --end-week 10
```

### Use Different Group

```bash
python main.py --group IT12Z
```

### Debug Mode

See detailed output of what's happening:
```bash
python main.py --debug
```

### Don't Overwrite Existing Events

Skip events that already exist in calendar:
```bash
python main.py --no-overwrite
```

### Command-Line Arguments

```
--group GROUP_NAME      Group name (e.g., IT11Z) [default: from .env]
--weeks WEEKS           Comma-separated list of weeks (e.g., 1,2,3)
--start-week WEEK       Start week (inclusive)
--end-week WEEK         End week (inclusive)
--no-overwrite          Don't update existing events
--debug                 Enable debug output
```

## How It Works

1. **Fetches Schedule**: Connects to https://orar.usarb.md/ and fetches schedule data for your group
2. **Generates Event IDs**: Creates unique 32-character hex IDs for each lesson based on:
   - Group name
   - Week number
   - Day of week
   - Lesson number
   - Course name
   - Course type
3. **Syncs to Calendar**: 
   - Connects to iCloud via CalDAV
   - Creates calendar if it doesn't exist
   - Creates new events or updates existing ones (based on event ID)
   - Prevents duplicates

## Troubleshooting

### "Could not resolve CalDAV server"

- Check that `CALDAV_URL` is correct: `https://caldav.icloud.com/`
- Make sure you have internet connection
- Try accessing https://caldav.icloud.com/ in a browser (should show authentication prompt)

### "Authentication failed" or "Invalid credentials"

- **Most common issue:** You're using your regular iCloud password instead of an app-specific password
- Make sure you generated a new app-specific password
- Verify the password format is correct (16 characters: `xxxx-xxxx-xxxx-xxxx`)
- Check that your iCloud email is correct
- Ensure 2FA is enabled on your Apple ID

### "Calendar not found" or "Permission denied"

- The script will create the calendar automatically if it doesn't exist
- Check that your app-specific password has calendar permissions
- Make sure you're using the correct iCloud account

### Events not appearing in calendar

- Check that the calendar was created (look for "USARB Schedule" in your calendars)
- Make sure you're viewing the correct calendar in Apple Calendar
- Run with `--debug` to see what's happening
- Check that the week numbers are correct (schedule starts at week 1)

### "Import caldav could not be resolved"

- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the correct virtual environment (if using one)

## Security Notes

- **Never commit `.env` file to git** (it's already in `.gitignore`)
- **Never share your app-specific password**
- **Revoke app-specific passwords** if you suspect they're compromised
- The app-specific password can be revoked at any time from [Apple ID account page](https://appleid.apple.com/)

## Example Workflow

```bash
# 1. First time setup - sync all weeks for semester
python main.py --start-week 1 --end-week 20 --debug

# 2. Regular updates - sync current and next weeks
python main.py

# 3. Check specific weeks
python main.py --weeks 5,6,7 --debug
```

## Files

- `main.py` - Main script for calendar sync
- `data_parser.py` - Parses schedule data and calculates dates
- `raw_schedule_data_fetch.py` - Fetches raw schedule from website
- `.env` - Your credentials (not in git)
- `requirements.txt` - Python dependencies

## License

This project is for personal use.
