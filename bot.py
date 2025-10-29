import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler,
    ContextTypes
)
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN, MESSAGES
from database import Database
from twitter_api import TwitterAPI
from utils import (
    format_user_card,
    format_following_list,
    format_tracked_users,
    create_user_keyboard,
    escape_markdown
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize
db = Database()
twitter_api = TwitterAPI()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        MESSAGES['welcome'],
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        MESSAGES['help'],
        parse_mode=ParseMode.MARKDOWN
    )

async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /track command"""
    if not context.args:
        await update.message.reply_text(
            "❌ use format: `/track username`\n\nExample: `/track loxous`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    username = context.args[0].replace('@', '')
    
    # Send loading message
    loading_msg = await update.message.reply_text(
        f"⏳ Fetching data for @{username}...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Get user info
        user_info_result = twitter_api.get_user_info(username)
        
        if not user_info_result['success']:
            await loading_msg.edit_text(
                f"❌ Error: {escape_markdown(user_info_result['error'])}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        user_data = user_info_result['data']
        current_following = user_data.get('following', 0)
        
        # Check if user already tracked
        existing_user = db.get_user(username)
        
        if existing_user:
            # User already tracked - check for new followings
            difference = current_following - existing_user['following_count']
            
            if difference > 0:
                # Has new followings
                fetch_msg = f"🔍 Detected {difference} new following \\! Fetching details"
                if difference > 200:
                    pages_needed = (difference + 199) // 200  # Ceiling division
                    fetch_msg += f" \\({pages_needed} API calls needed\\)"
                fetch_msg += "\\.\\.\\."
                
                await loading_msg.edit_text(
                    fetch_msg,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                
                # Fetch new followings
                followings_result = twitter_api.fetch_new_followings(username, difference)
                
                if followings_result['success']:
                    # Update database
                    db.save_user(username, user_data, current_following)
                    
                    # Format and send new followings
                    messages = format_following_list(followings_result['new_followings'])
                    
                    await loading_msg.delete()
                    
                    for msg in messages:
                        await update.message.reply_text(
                            msg,
                            parse_mode=ParseMode.MARKDOWN_V2,
                            disable_web_page_preview=True
                        )
                    
                    # Send summary with pagination info
                    summary = f"✅ *Update Complete*\n\n"
                    summary += f"User: @{username}\n"
                    summary += f"Following baru: *{difference}*\n"
                    summary += f"Total following: *{current_following}*\n"
                    
                    # Add pagination info if multiple pages were fetched
                    if followings_result.get('pages_fetched', 1) > 1:
                        summary += f"\n📄 Pages fetched: *{followings_result['pages_fetched']}*"
                        summary += f"\n💳 API calls used: *{followings_result['pages_fetched']}*"
                    
                    await update.message.reply_text(
                        summary,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=create_user_keyboard(username)
                    )
                else:
                    await loading_msg.edit_text(
                        f"❌ Error fetching followings: {escape_markdown(followings_result['error'])}",
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
            
            elif difference < 0:
                # Following decreased (unfollowed)
                db.save_user(username, user_data, current_following)
                
                msg = f"📊 *Update for @{username}*\n\n"
                msg += f"Following decrease: *{abs(difference)}*\n"
                msg += f"Total following: *{current_following}*\n\n"
                msg += "ℹ️ User unfollow"
                
                await loading_msg.edit_text(
                    msg,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=create_user_keyboard(username)
                )
            
            else:
                # No change
                db.save_user(username, user_data, current_following)
                
                msg = f"✅ *@{username}* up\\-to\\-date\\!\n\n"
                msg += f"Following: *{current_following}*\n"
                msg += "Nothing change\\."
                
                await loading_msg.edit_text(
                    msg,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=create_user_keyboard(username)
                )
        
        else:
            # First time tracking
            db.save_user(username, user_data, current_following)
            
            msg = f"✅ *Success tracking @{username}\\!*\n\n"
            msg += format_user_card(user_data)
            msg += "\n\n💡 Use `/track {username}` for check update\\."
            
            await loading_msg.edit_text(
                msg,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_user_keyboard(username),
                disable_web_page_preview=True
            )
    
    except Exception as e:
        logger.error(f"Error in track_command: {e}")
        await loading_msg.edit_text(
            f"❌ error: {escape_markdown(str(e))}",
            parse_mode=ParseMode.MARKDOWN_V2
        )

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command"""
    users = db.get_all_users()
    msg = format_tracked_users(users)
    
    await update.message.reply_text(
        msg,
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remove command"""
    if not context.args:
        await update.message.reply_text(
            "❌ Use format: `/remove username`\n\nExample: `/remove loxous`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    username = context.args[0].replace('@', '')
    
    if db.remove_user(username):
        await update.message.reply_text(
            f"✅ Success delete tracking for @{username}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            f"❌ User @{username} not found in tracking list",
            parse_mode=ParseMode.MARKDOWN
        )

async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /credits command"""
    loading_msg = await update.message.reply_text("⏳ Checking credits...")
    
    result = twitter_api.get_my_credits()
    
    if result['success']:
        msg = f"💳 *API Credits Information*\n\n"
        msg += f"💰 Recharge Credits: *{result['recharge_credits']}*\n"
        msg += f"🎁 Bonus Credits: *{result['total_bonus_credits']}*\n"
        msg += f"📊 Total Available: *{result['recharge_credits'] + result['total_bonus_credits']}*"
        
        await loading_msg.edit_text(
            msg,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await loading_msg.edit_text(
            f"❌ Error: {result['error']}",
            parse_mode=ParseMode.MARKDOWN
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('check_'):
        username = data.replace('check_', '')
        # Simulate /track command
        context.args = [username]
        await track_command(update, context)
    
    elif data.startswith('remove_'):
        username = data.replace('remove_', '')
        
        if db.remove_user(username):
            await query.edit_message_text(
                f"✅ Success delete tracking for @{username}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"❌ User @{username} not found",
                parse_mode=ParseMode.MARKDOWN
            )

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("track", track_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("credits", credits_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()