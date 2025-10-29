from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def format_number(num):
    """Format number with K, M suffix"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def format_date(date_str):
    """Format date string to readable format"""
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%d %B %Y")
    except:
        return date_str

def format_datetime(iso_str):
    """Format ISO datetime to readable format"""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return iso_str

def escape_markdown(text):
    """Escape special characters for Telegram MarkdownV2"""
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_user_card(user_data, show_stats=True):
    """Format user information card"""
    name = escape_markdown(user_data.get('name', 'N/A'))
    username = user_data.get('userName', 'N/A')
    description = escape_markdown(user_data.get('description', 'No description'))[:150]
    
    followers = format_number(user_data.get('followers_count', 0))
    following = format_number(user_data.get('following_count', 0))
    tweets = format_number(user_data.get('statuses_count', 0))
    
    created = format_date(user_data.get('created_at', 'N/A'))
    
    # Build message
    msg = f"*{name}*\n"
    msg += f"[@{username}](https://twitter.com/{username})\n\n"
    msg += f"_{description}_\n\n"
    
    if show_stats:
        msg += f"👥 Followers: *{followers}*\n"
        msg += f"➕ Following: *{following}*\n"
        msg += f"📝 Tweets: *{tweets}*\n"
        msg += f"📅 Joined: {created}\n"
    
    return msg

def format_following_list(followings):
    """Format list of new followings"""
    if not followings:
        return "No new following\\."
    
    messages = []
    message = "*🆕 New Following Detected\\!*\n\n"
    message += f"Total: *{len(followings)}* new account\n"
    message += "━━━━━━━━━━━━━━━━━━\n\n"
    messages.append(message)
    
    for idx, user in enumerate(followings, 1):
        name = escape_markdown(user.get('name', 'N/A'))
        username = user.get('userName', 'N/A')
        description = escape_markdown(user.get('description', 'No description'))
        
        # Limit description length
        if len(description) > 100:
            description = description[:97] + "\\.\\.\\."
        
        followers = format_number(user.get('followers_count', 0))
        following = format_number(user.get('following_count', 0))
        tweets = format_number(user.get('statuses_count', 0))
        created = format_date(user.get('created_at', 'N/A'))
        
        user_msg = f"*{idx}\\. {name}*\n"
        user_msg += f"[@{username}](https://twitter.com/{username})\n"
        user_msg += f"_{description}_\n\n"
        user_msg += f"👥 {followers} • ➕ {following} • 📝 {tweets}\n"
        user_msg += f"📅 {created}\n"
        user_msg += "━━━━━━━━━━━━━━━━━━\n\n"
        
        # Check if adding this user exceeds Telegram message limit
        if len(messages[-1] + user_msg) > 4000:
            messages.append(user_msg)
        else:
            messages[-1] += user_msg
    
    return messages

def create_user_keyboard(username):
    """Create inline keyboard for user actions"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Check Update", callback_data=f"check_{username}"),
            InlineKeyboardButton("🗑️ Remove", callback_data=f"remove_{username}")
        ],
        [
            InlineKeyboardButton("🔗 View on Twitter", url=f"https://twitter.com/{username}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def format_tracked_users(users):
    """Format list of tracked users"""
    if not users:
        return "No users are being\\-tracked\\.\n\nUse `/track username` to start tracking\\."
    
    msg = "*📋 List of tracked \\-Users*\n\n"
    
    for user in users:
        username = user.get('username', 'N/A')
        following = user.get('following_count', 0)
        last_checked = format_datetime(user.get('last_checked', ''))
        check_count = user.get('check_count', 0)
        
        msg += f"• *{username}*\n"
        msg += f"  Following: {following} \\| Checked: {check_count}x\n"
        msg += f"  Last: {escape_markdown(last_checked)}\n\n"
    
    msg += f"Total: *{len(users)}* user\n"
    msg += "\nUse `/track username` for check update\\."
    
    return msg