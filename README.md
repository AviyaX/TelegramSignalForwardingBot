# Telegram Trading Signal Formatter Bot

A Telegram bot that monitors multiple trading signal groups, formats the signals into a standardized format using Google's Gemini AI, and forwards them to a destination group.

## Features

- Monitors multiple source groups for trading signals
- Automatically formats trading signals with:
  - Asset name
  - Trade type (BUY/SELL)
  - Entry prices (single or range)
  - Stop Loss levels
  - Take Profit targets
- Ensures price ranges are properly ordered (lower price first)
- Forwards formatted signals to a designated group

## Prerequisites

- Python 3.x installed on your system
- Telegram API credentials (api_id, api_hash)
- Gemini API key

## Quick Setup

1. Clone and setup:
```bash
git clone https://github.com/AviyaX/TelegramSignalForwardingBot.git
cd TelegramSignalForwardingBot
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials (use .env.example as a template):
```env
# Telegram API Credentials
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=your_phone_number

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key

# Groups Configuration
SOURCE_GROUPS_REAL=group_id1,group_id2,group_id3
DESTINATION_GROUP=destination_group_id
```

3. Start the bot:
```bash
python bot.py
```

## Example Signal Format

Input signal:
```
Buy Gold @2931-2927
Sl :2925
Tp1 :2932.5
Tp2 :2935
```

Formatted output:
```
Asset: Gold
Type: BUY
Entry: 2927 - 2931
Stop Loss: 2925
Take Profit: 2932.5 2935
```

## Troubleshooting

- Verify your API credentials in the .env file
- Ensure you have the correct permissions in Telegram groups
- Check your internet connection
- Make sure your Gemini API key is active and has sufficient quota

## Notes

- Keep your API keys secure and never share them publicly
- The bot requires first-time Telegram authentication with a verification code
