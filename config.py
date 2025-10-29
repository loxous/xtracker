import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# Twitter API Configuration
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'YOUR_TWITTER_API_KEY')
TWITTER_API_BASE_URL = 'https://api.twitterapi.io'

# Storage Configuration
DATA_DIR = 'data'
USERS_DB_FILE = os.path.join(DATA_DIR, 'users.json')

# API Endpoints
ENDPOINTS = {
    'user_info': '/twitter/user/info',
    'user_following': '/twitter/user/followings',
    'my_info': '/oapi/my/info'
}

# Bot Messages
MESSAGES = {
    'welcome': """
🤖 *Twitter Tracker Bot*

Welcome! This bot will help you track new followers from your Twitter account.

*Commands:*
/start - Start the bot
/track [username] - Track Twitter user
/list - List all tracked users
/remove [username] - Remove tracking for a user
/credits - Check remaining API credits
/help - Help

*How to use:*
1. Type `/track twitter_username`
2. The bot will automatically track every time you check
3. New follows will be displayed with complete details

Made with ❤️
""",
    'help': """
*📖 User Guide*

*Main Commands:*
• `/track [username]` - Start tracking a user.
  Example: `/track loxous`

• `/list` - View a list of tracked users.

• `/remove [username]` - Stop tracking a user.
  Example: `/remove loxous`

• `/credits` - Check your remaining API credits

*How it works:*
1. When you first track, the bot will save the following data
2. When you check a second time, the bot will detect new followers
3. The bot will automatically fetch the new follower details

*Tips:*
• The bot only tracks when you make a manual request
• Make sure the Twitter username is correct (without @)
• Check periodically for the latest updates
"""
}