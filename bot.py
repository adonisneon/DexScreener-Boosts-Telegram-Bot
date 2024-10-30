import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from datetime import datetime
import json
import pytz
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
TOKEN = "your-telegram-bot-token" # Replace with your token from Botfather
SEEN_TOKENS_FILE = "seen_tokens.json"
LATEST_BOOSTS_URL = "https://api.dexscreener.com/token-boosts/latest/v1"
TOP_BOOSTS_URL = "https://api.dexscreener.com/token-boosts/top/v1"
PAIRS_API_URL = "https://api.dexscreener.com/latest/dex/tokens/{}"
CHANNEL_LINK = "https://t.me/your-channel-link"  # Replace with your channel link
RATE_LIMIT_DELAY = 0.5

class TokenTracker:
    def __init__(self):
        self.seen_tokens = self.load_seen_tokens()

    def load_seen_tokens(self):
        try:
            with open(SEEN_TOKENS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_seen_tokens(self):
        with open(SEEN_TOKENS_FILE, 'w') as f:
            json.dump(self.seen_tokens, f)

    def track_token(self, chain_id: str, token_address: str) -> tuple[bool, str]:
        key = f"{chain_id}_{token_address}"
        current_time = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

        if key not in self.seen_tokens:
            self.seen_tokens[key] = current_time
            self.save_seen_tokens()
            return True, current_time

        return False, self.seen_tokens[key]

def format_number(value: float, suffix: str = '') -> str:
    """Format numbers to human readable format with appropriate suffix"""
    if value is None:
        return "N/A"

    suffixes = ['', 'K', 'M', 'B', 'T']
    for s in suffixes:
        if value < 1000:
            return f"${value:.2f}{s}{suffix}"
        value /= 1000
    return f"${value:.2f}T{suffix}"

def get_token_details(token_address: str) -> dict:
    """Fetch comprehensive token details from DexScreener"""
    try:
        time.sleep(RATE_LIMIT_DELAY)
        response = requests.get(PAIRS_API_URL.format(token_address))
        response.raise_for_status()
        data = response.json()

        if 'pairs' in data and data['pairs']:
            pair = max(data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))

            return {
                'market_cap': float(pair.get('marketCap', 0)) if pair.get('marketCap') else None,
                'fdv': float(pair.get('fdv', 0)) if pair.get('fdv') else None,
                'price': float(pair.get('priceUsd', 0)) if pair.get('priceUsd') else None,
                'symbol': pair.get('baseToken', {}).get('symbol', 'Unknown'),
                'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                'liquidity': float(pair.get('liquidity', {}).get('usd', 0)) if pair.get('liquidity', {}).get('usd') else None
            }
    except Exception as e:
        logging.error(f"Error fetching token details: {str(e)}")

    return {
        'market_cap': None,
        'fdv': None,
        'price': None,
        'symbol': 'Unknown',
        'name': 'Unknown',
        'liquidity': None
    }

token_tracker = TokenTracker()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message handler"""
    welcome_message = (
        "🚀 Welcome to DexScreener Boosts Bot! 🚀\n\n"
        "Available commands:\n"
        "/top_boosts - Get the most active token boosts\n"
        "/latest_boosts - Get the latest token boosts\n"
        "/help - Show detailed help information\n\n"
        f"📢 For automatic updates, subscribe to our channel:\n{CHANNEL_LINK}"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help message handler"""
    help_message = (
        "📚 <b>DexScreener Boosts Bot Help</b>\n\n"
        "<b>Available Commands:</b>\n"
        "🔥 /top_boosts - View tokens with highest boost activity\n"
        "⚡️ /latest_boosts - Get real-time latest token boosts\n"
        "❓ /help - Show this help message\n\n"
        "<b>Token Information Provided:</b>\n"
        "• Token name and symbol\n"
        "• Market cap and FDV\n"
        "• Current price\n"
        "• Liquidity\n"
        "• Boost amount and total boost\n"
        "• Social links (Website, Twitter, Telegram)\n\n"
        f"📢 For automatic updates, join our channel:\n{CHANNEL_LINK}"
    )
    await update.message.reply_text(help_message, parse_mode='HTML')

def format_boost_message(boost: dict, fetch_time: str, prefix: str) -> str:
    """Enhanced message formatter with detailed token information"""
    is_new, first_seen = token_tracker.track_token(
        boost.get('chainId', 'unknown'),
        boost.get('tokenAddress', 'unknown')
    )

    token_details = get_token_details(boost.get('tokenAddress', ''))
    status_indicator = "🆕 NEW!" if is_new else "📊 Updated"

    # Basic token information
    message = [
        f"🚀 <b>{prefix} Token Boost</b> {status_indicator}\n",
        f"💎 <b>Token Information:</b>",
        f"• Name: {token_details['name']} ({token_details['symbol']})",
        f"• Market Cap: {format_number(token_details['market_cap'])}",
        f"• FDV: {format_number(token_details['fdv'])}",
        f"• Price: ${token_details['price']:.8f}" if token_details['price'] else "• Price: N/A",
        f"• Liquidity: {format_number(token_details['liquidity'])}\n",

        f"📈 <b>Boost Details:</b>",
        f"• Boost Amount: {boost.get('amount', 'N/A')}",
        f"• Total Boost Amount: {boost.get('totalAmount', 'N/A')}\n",

        f"⚙️ <b>Additional Information:</b>",
        f"• Chain: {boost.get('chainId', 'N/A')}",
        f"• Token Address: <code>{boost.get('tokenAddress', 'N/A')}</code>",
        f"• First Seen: {first_seen}",
        f"• Last Updated: {fetch_time}\n"
    ]

    # Social links section
    if boost.get('links'):
        message.append("🔗 <b>Social Links:</b>")
        social_links = {'Website': '🌐', 'Twitter': '🐦', 'Telegram': '📱', 'Discord': '💬'}

        for link in boost['links']:
            label = link.get('label', 'Link')
            emoji = social_links.get(label, '🔗')
            message.append(f"• {emoji} <a href='{link.get('url')}'>{label}</a>")

    # DexScreener link
    if boost.get('url'):
        message.append(f"\n🔍 <a href='{boost['url']}'>View on DexScreener</a>")

    return "\n".join(message)

async def fetch_boosts(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, message_prefix: str) -> None:
    """Enhanced boost fetcher with status updates"""
    try:
        status_message = await update.message.reply_text(f"🔍 Fetching {message_prefix.lower()} token boosts...")

        response = requests.get(url, headers={})
        response.raise_for_status()
        data = response.json()

        fetch_time = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        await status_message.edit_text("⚡️ Found boosts! Fetching detailed token information...")

        if isinstance(data, list):
            for idx, boost in enumerate(data, 1):
                message = format_boost_message(boost, fetch_time, f"{message_prefix} #{idx}")
                await update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)
        else:
            message = format_boost_message(data, fetch_time, message_prefix)
            await update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)

        await status_message.delete()

    except Exception as e:
        error_message = f"❌ Error: {str(e)}"
        if isinstance(e, requests.RequestException):
            error_message = "❌ Network error: Could not fetch boost data. Please try again later."
        await update.message.reply_text(error_message)

async def get_latest_boosts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Latest boosts command handler"""
    await fetch_boosts(update, context, LATEST_BOOSTS_URL, "Latest")

async def get_top_boosts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Top boosts command handler"""
    await fetch_boosts(update, context, TOP_BOOSTS_URL, "Top")

def main() -> None:
    """Initialize and start the bot"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("latest_boosts", get_latest_boosts))
    application.add_handler(CommandHandler("top_boosts", get_top_boosts))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
